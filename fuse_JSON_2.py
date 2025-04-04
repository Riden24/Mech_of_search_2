import json

# Load the two JSON files
with open("annotations.json", "r") as f:
    vision_data = json.load(f)

with open("image_metadata_final.json", "r") as f:
    metadata_list = json.load(f)

# Merge by matching "image_i.jpg" to metadata[i]
merged_data = {}

for idx, meta in enumerate(metadata_list):
    img_key = f"image_{idx}.jpg"

    # Start with the vision data
    combined = vision_data.get(img_key, {})

    # Add metadata fields (safely)
    combined["title"] = meta.get("title", "")
    combined["image_url"] = meta.get("image_url", "")
    combined["file_page_url"] = meta.get("file_page_url", "")
    combined["ImageDescription"] = meta.get("ImageDescription", "")
    combined["Artist"] = meta.get("Artist", "")

    merged_data[img_key] = combined

# Save to a new JSON file
with open("fused_image_data.json", "w") as f:
    json.dump(merged_data, f, indent=4)
