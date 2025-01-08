import requests
import os

def download_google_fonts(output_dir="google_fonts"):
    api_url = "https://www.googleapis.com/webfonts/v1/webfonts"
    api_key = "AIzaSyA9xYq-feh_3X-RqURVtSVfcvq-OEl3zHE"  # Replace with your API key

    # Fetch font data
    response = requests.get(f"{api_url}?key={api_key}")
    fonts = response.json()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Loop through the fonts and download only if not already downloaded
    for font in fonts['items']:
        font_name = font['family']
        for variant in font['files']:
            font_url = font['files'][variant]
            file_name = f"{font_name}-{variant}.ttf"
            file_path = os.path.join(output_dir, file_name)
            
            # Check if the file already exists
            if os.path.exists(file_path):
                print(f"Skipping {file_name}, already downloaded.")
            else:
                print(f"Downloading {file_name}...")
                font_data = requests.get(font_url)
                with open(file_path, "wb") as font_file:
                    font_file.write(font_data.content)
    print("Font download process complete!")

# Call the function
download_google_fonts()
