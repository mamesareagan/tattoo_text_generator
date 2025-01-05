from rest_framework.permissions import IsAuthenticated
from celery.result import AsyncResult
from django.core.exceptions import ValidationError
from tattoo_text_generator import settings
from tattoos.tasks import generate_tattoo_image
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from tattoos.models import Font, TattooRequest
from tattoos.serializers import TattooRequestSerializer

class GenerateTattooView(APIView):
    """
     API View for generating tattoo text images.
    
    Handles the creation of tattoo requests and initiates asynchronous image generation.
    Attributes:
        permission_classes (list): List of permission classes for the view.
        MIN_FONT_SIZE (int): Minimum allowed font size.
        MAX_FONT_SIZE (int): Maximum allowed font size.
        DEFAULT_FONT_SIZE (int): Default font size if not specified.
        DEFAULT_COLOR (str): Default color in hex format if not specified.
    Methods:
        validate_color(color: str) -> bool:
            Validate hex color format.
        validate_size(size: int) -> int:
            Validate and constrain font size.
        post(request):
                text (str): Required - Text to generate.
                font (str): Required - Font name to use.
                color (str): Optional - Hex color code (default: #000000).
                size (int): Optional - Font size (default: 100).
    """
   
    permission_classes = [IsAuthenticated]
    
    # Constants for validation
    MIN_FONT_SIZE = 12
    MAX_FONT_SIZE = 200
    DEFAULT_FONT_SIZE = 100
    DEFAULT_COLOR = "#000000"
    
    def validate_color(self, color: str) -> bool:
        """Validate hex color format."""
        if not color:
            return False
        return color.startswith('#') and len(color) == 7
    
    def validate_size(self, size: int) -> int:
        """Validate and constrain font size."""
        try:
            size = int(size)
            return max(min(size, self.MAX_FONT_SIZE), self.MIN_FONT_SIZE)
        except (TypeError, ValueError):
            return self.DEFAULT_FONT_SIZE
    
    def post(self, request):
        """
        Handle POST request to generate a tattoo image.
        
        Request Parameters:
            text (str): Required - Text to generate
            font (str): Required - Font name to use
            color (str): Optional - Hex color code (default: #000000)
            size (int): Optional - Font size (default: 100)
        """
        # Extract and validate basic parameters
        text = request.data.get("text", "").strip()
        font_name = request.data.get("font", "").strip()
        color = request.data.get("color", self.DEFAULT_COLOR).strip()
        size = request.data.get("size", self.DEFAULT_FONT_SIZE)
        
        # Validate required fields
        if not text:
            return Response(
                {"error": "Text is required and cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not font_name:
            return Response(
                {"error": "Font name is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate color format
        if not self.validate_color(color):
            return Response(
                {"error": "Invalid color format. Use hex color (e.g., #FF5733)."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate and constrain size
        size = self.validate_size(size)
        
        try:
            # Get font object
            font = Font.objects.get(name=font_name)
            
            # Ensure font file exists
            if not font.file_path:
                return Response(
                    {"error": "Font file is missing."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Create TattooRequest first
            tattoo_request = TattooRequest.objects.create(
                user=request.user,
                text=text,
                font=font,
                color=color,
                #status='pending'  # Set initial status
            )
            
            # Generate image asynchronously
            result = generate_tattoo_image.apply_async(
                args=[text, str(font.file_path), color, size],
                task_id=str(tattoo_request.id)  # Use request ID as task ID
            )
            
            # Update request with task ID
            tattoo_request.task_id = result.id
            tattoo_request.save(update_fields=['task_id'])
            
            # Serialize and return response
            serializer = TattooRequestSerializer(tattoo_request)
            
            return Response({
                "request_id": str(tattoo_request.id),
                "task_id": result.id,
                "message": "Image generation started.",
                "status": "pending",
                "data": serializer.data
            }, status=status.HTTP_202_ACCEPTED)
            
        except Font.DoesNotExist:
            return Response(
                {"error": f"Font '{font_name}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response(
                {"error": "Failed to initiate image generation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class CheckTaskStatusView(APIView):
    """
    Check the status of a tattoo generation task.
    
    Endpoints:
        GET /api/tasks/<task_id>/
        
    Returns:
        - 200: Task completed successfully with image URL
        - 202: Task is still in progress
        - 404: Task not found
        - 500: Task failed or encountered an error
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        try:
            if not task_id:
                return Response(
                    {"error": "Task ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Retrieve the Celery task result
            task_result = AsyncResult(task_id)
            
            # Define response based on task state
            response_data = {
                "task_id": task_id,
                "status": task_result.state.lower(),
            }
            
            if task_result.state == 'PENDING':
                return Response(
                    {**response_data, "message": "Task is still pending."},
                    status=status.HTTP_202_ACCEPTED
                )
                
            elif task_result.state == 'STARTED':
                return Response(
                    {**response_data, "message": "Task is currently processing."},
                    status=status.HTTP_202_ACCEPTED
                )
                
            elif task_result.state == 'SUCCESS':
                image_path = task_result.result
                if not image_path:
                    raise ValidationError("No image path returned from task")
                    
                image_url = f"{settings.MEDIA_URL}{image_path}"
                return Response({
                    **response_data,
                    "message": "Task completed successfully.",
                    "image_url": image_url,
                    "created_at": task_result.date_done
                }, status=status.HTTP_200_OK)
                
            elif task_result.state == 'FAILURE':
                error_msg = str(task_result.result) if task_result.result else "Unknown error occurred"
                return Response({
                    **response_data,
                    "message": "Task failed.",
                    "error": error_msg
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            elif task_result.state == 'REVOKED':
                return Response({
                    **response_data,
                    "message": "Task was cancelled."
                }, status=status.HTTP_410_GONE)
                
            else:
                return Response({
                    **response_data,
                    "message": f"Unknown task state: {task_result.state}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except ValidationError as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "error": "An unexpected error occurred while checking task status"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)