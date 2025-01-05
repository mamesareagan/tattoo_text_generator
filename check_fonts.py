import os
import django

# Set the Django settings module explicitly
os.environ['DJANGO_SETTINGS_MODULE'] = 'tattoo_text_generator.settings'  # Replace with actual project settings

# Initialize Django
django.setup()

from tattoos.models import Font

font_directory = 'media/fonts'

# Initialize font count
new_font_count = 0

# Loop through font files
for font_file in os.listdir(font_directory):
    if font_file.endswith(('.ttf', '.otf')):  # Check for font files
        font_name = font_file.split('.')[0]  # Extract the font name (without extension)
        font_path = os.path.join(font_directory, font_file)  # Full path to the font file

        # Check if the font already exists in the database
        if Font.objects.filter(name=font_name).exists():
            print(f"Font '{font_name}' already exists in the database.")
        else:
            # Register the font in the database
            Font.objects.create(name=font_name, file_path=font_path)
            new_font_count += 1
            print(f"Registered new font: {font_name}")

# Get the total number of fonts in the database
total_fonts = Font.objects.count()

print(f"\nTotal fonts available in the database: {total_fonts}")
print(f"New fonts registered: {new_font_count}")
