from rest_framework import serializers
from tattoos.models import Font, TattooRequest

class FontSerializer(serializers.ModelSerializer):
    """
    Serializer for the Font model.
    Ensures only the necessary fields are exposed.
    """
    class Meta:
        model = Font
        fields = ['id', 'name']
        read_only_fields = ['id']


class TattooRequestSerializer(serializers.ModelSerializer):
    """TattooRequestSerializer is a ModelSerializer for the TattooRequest model.

    Attributes:
        user (serializers.HiddenField): Automatically assigns the current authenticated user.
        font_name (serializers.ReadOnlyField): Displays the font name for readability.

    Meta:
        model (TattooRequest): The model that is being serialized.
        fields (list): The fields to include in the serialization.
        read_only_fields (list): The fields that are read-only.

    Methods:
        validate_color(value):
            Validates that the color is a valid hexadecimal color code.
            Args:
                value (str): The color code to validate.
            Raises:
                serializers.ValidationError: If the color code is invalid.
            Returns:
                str: The validated color code.

        validate_text(value):
            Ensures the tattoo text is not empty and doesn't exceed a limit.
            Args:
                value (str): The text to validate.
            Raises:
                serializers.ValidationError: If the text is empty or exceeds the maximum length.
            Returns:
                str: The validated text.

        validate(data):
            Performs custom validation for the TattooRequest.
            Ensures the font exists when specified.
            Args:
                data (dict): The data to validate.
            Raises:
                serializers.ValidationError: If the font is not provided.
            Returns:
                dict: The validated data.
    """
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )  # Automatically assign the current authenticated user

    font_name = serializers.ReadOnlyField(source="font.name")  # Show font name for readability

    class Meta:
        model = TattooRequest
        fields = [
            'id', 
            'user', 
            'text', 
            'font', 
            'font_name', 
            'color', 
            'image_path', 
            'task_id',  # Include the task_id in the fields
            'created_at'
        ]
        read_only_fields = ['id', 'image_path', 'created_at']

    def validate_color(self, value):
        """
        Validate that the color is a valid hexadecimal color code.
        """
        if not value.startswith("#") or len(value) != 7:
            raise serializers.ValidationError("Invalid color code. Use a valid hex color (e.g., #FF5733).")
        return value

    def validate_text(self, value):
        """
        Ensure the tattoo text is not empty and doesn't exceed a limit.
        """
        if not value.strip():
            raise serializers.ValidationError("Tattoo text cannot be empty.")
        if len(value) > 255:
            raise serializers.ValidationError("Tattoo text exceeds the maximum length of 255 characters.")
        return value

    def validate(self, data):
        """
        Perform custom validation for the TattooRequest.
        Ensure the font exists when specified.
        """
        if 'font' in data and data['font'] is None:
            raise serializers.ValidationError("A valid font must be provided.")
        return data