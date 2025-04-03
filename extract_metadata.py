import os
import json
from PIL import Image
from PIL.ExifTags import TAGS


image_dir = "./wikipedia_images"
output_json = "image_metadata.json"

# List to store metadata
metadata_list = []

with Image.open("./wikipedia_images/image_0.jpg") as img:
    print("img = ", img)

def convert_metadata_to_json_serializable(metadata):
    """Convert EXIF metadata to JSON-compatible format."""
    json_metadata = {}
    for tag, value in metadata.items():
        if isinstance(value, bytes):
            json_metadata[tag] = value.hex()  # Convert bytes to hex string
        elif isinstance(value, tuple):
            json_metadata[tag] = tuple(str(v) for v in value)  # Convert tuples to strings
        elif isinstance(value, int) or isinstance(value, float) or isinstance(value, str):
            json_metadata[tag] = value  # Keep simple types as they are
        else:
            json_metadata[tag] = str(value)  # Convert other objects to string
    return json_metadata
# Function to extract EXIF metadata
def extract_metadata(image_path):
    metadata = {}
    with Image.open(image_path) as img:
        # Get basic image info
        metadata["filename"] = os.path.basename(image_path)
        metadata["format"] = img.format
        metadata["size"] = img.size  # (width, height)
        metadata["mode"] = img.mode  # Color mode (e.g., RGB, CMYK)
        
        # Extract EXIF metadata if available
        exif_data = img.getexif()
        if exif_data:
            # Keep only specific EXIF tags
            interesting_tags = ["Artist", "ImageDescription"]
            filtered_exif = {
                TAGS.get(tag, tag): value for tag, value in exif_data.items() 
                if TAGS.get(tag, tag) in interesting_tags
            }
            metadata["exif"] = filtered_exif
    
    return metadata



# Loop through all images in the directory
for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        image_path = os.path.join(image_dir, filename)
        metadata = extract_metadata(image_path)
        metadata = convert_metadata_to_json_serializable(metadata)
        metadata_list.append(metadata)

# Save metadata as a JSON file
with open(output_json, "w", encoding="utf-8") as json_file:
    json.dump(metadata_list, json_file, indent=4)

print(f"Metadata saved in {output_json}")
