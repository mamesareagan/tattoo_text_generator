from django.db import models
import uuid
from django.conf import settings


class Font(models.Model):
    """
    Model for storing font details used in tattoo text generation.
    """
    name = models.CharField(max_length=255, unique=True)
    file_path = models.FileField(
        upload_to="fonts/",  # Upload fonts to media/fonts/
        verbose_name="Font File"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TattooRequest(models.Model):
    """
    Model representing a tattoo request made by a user.

    Attributes:
        id (UUIDField): Primary key for the tattoo request, automatically generated.
        user (ForeignKey): Reference to the user who made the request, linked to the AUTH_USER_MODEL.
        text (CharField): The text content of the tattoo, with a maximum length of 255 characters.
        font (ForeignKey): Reference to the font used for the tattoo text, can be null.
        color (CharField): Hexadecimal color code for the tattoo text, default is black (#000000).
        image_path (ImageField): Path to the generated tattoo image, can be null or blank.
        task_id (CharField): ID of the task associated with generating the tattoo, can be null or blank.
        created_at (DateTimeField): Timestamp when the tattoo request was created, automatically set.

    Methods:
        __str__: Returns a string representation of the tattoo request, including the text and the username of the requester.

    Meta:
        ordering (list): Orders the tattoo requests by creation date in descending order.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    font = models.ForeignKey(Font, on_delete=models.SET_NULL, null=True)
    color = models.CharField(max_length=7, default="#000000")  # Hex color
    image_path = models.ImageField(upload_to='tattoos/', null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)  # Store task ID here
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tattoo ({self.text}) for {self.user.username}"
    class Meta:
        ordering = ['-created_at']
