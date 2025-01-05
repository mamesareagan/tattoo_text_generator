from celery import shared_task
from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import logging
from typing import Tuple
from django.conf import settings
from dataclasses import dataclass

@dataclass
class TextDimensions:
    """Data class to store text measurement information."""
    width: int
    height: int
    left: int
    top: int
    right: int
    bottom: int

class TattooImageGenerator:
    """Class to handle tattoo image generation with minimal padding."""
    
    # Constants for image generation
    MIN_PADDING = 10  # Reduced minimum padding
    MAX_PADDING = 30  # Maximum padding
    PADDING_RATIO = 0.1  # Reduced padding ratio for tighter images
    
    def __init__(self, text: str, font_path: str, color: str, size: int):
        """Initialize the generator with text and style parameters."""
        self.text = text
        self.font_path = font_path
        self.color = color
        self.size = size
        self.font = None
        self.text_dims = None
    
    def load_font(self) -> None:
        """Load the font and handle potential errors."""
        try:
            self.font = ImageFont.truetype(self.font_path, self.size)
        except IOError as e:
            logging.error(f"Failed to load font from {self.font_path}: {str(e)}")
            raise
    
    def measure_text(self) -> TextDimensions:
        """Measure text dimensions using the loaded font."""
        left, top, right, bottom = self.font.getbbox(self.text)
        return TextDimensions(
            width=right - left,
            height=bottom - top,
            left=left,
            top=top,
            right=right,
            bottom=bottom
        )
    
    def calculate_padding(self) -> int:
        """Calculate appropriate padding based on font size."""
        # Calculate padding proportional to font size, but with limits
        base_padding = min(self.size * self.PADDING_RATIO, self.MAX_PADDING)
        return max(self.MIN_PADDING, int(base_padding))
    
    def calculate_image_size(self) -> Tuple[int, int]:
        """Calculate minimal image size with small padding."""
        padding = self.calculate_padding()
        
        # Add padding to text dimensions
        width = self.text_dims.width + (padding * 2)
        height = self.text_dims.height + (padding * 2)
        
        return width, height
    
    def generate(self) -> str:
        """Generate the tattoo image and return the file path."""
        self.load_font()
        self.text_dims = self.measure_text()
        
        # Calculate image dimensions
        width, height = self.calculate_image_size()
        
        # Create image
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Calculate text position for centering
        x = (width - self.text_dims.width) // 2
        y = (height - self.text_dims.height) // 2
        
        # Draw text
        draw.text((x, y), self.text, font=self.font, fill=self.color)
        
        # Generate output path
        output_dir = os.path.join(settings.MEDIA_ROOT, "tattoos")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{uuid.uuid4()}.png")
        
        # Save image with optimization
        image.save(output_path, 'PNG', optimize=True)
        return output_path

@shared_task(bind=True, max_retries=3)
def generate_tattoo_image(self, text: str, font_path: str, color: str, size: int) -> str:
    """
    Celery task to generate a tattoo image with custom text, font, color, and size.
    
    Parameters:
        text (str): Text to display in the tattoo image
        font_path (str): Path to the .ttf or .otf font file
        color (str): Color of the text in hex format (e.g., '#000000')
        size (int): Font size for the tattoo text
    
    Returns:
        str: Path to the generated tattoo image
    """
    try:
        generator = TattooImageGenerator(text, font_path, color, size)
        return generator.generate()
    except Exception as e:
        logging.error(f"Failed to generate tattoo image: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))