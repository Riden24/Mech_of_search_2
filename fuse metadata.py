import json
import csv
import ast  # To safely evaluate the EXIF string into a dictionary

metadata_list = []
output_json = "image_metadata_final.json"

# Reading CSV file
with open('./image_metadata.csv', mode='r', encoding='utf-8') as f:
    csv_data = csv.reader(f)
    headers = next(csv_data)  # Skip the header row
    
    # Reading JSON file
    with open('./image_metadata.json', 'r') as json_file:
        json_data = json.load(json_file)
    
    # Iterating over each row in CSV
    for row in csv_data:
        metadata = {}  # Reset metadata for each row
        id = "image_" + row[0] + ".jpg"
        title = row[1]
        image_url = row[4]
        file_page_url = row[5]

        # Find the corresponding image in the JSON data
        for item in json_data:
            if item['filename'] == id:
                metadata['title'] = title
                metadata['image_url'] = image_url
                metadata['file_page_url'] = file_page_url
                print(item)
                # Parsing the EXIF field, if present
                if item.get('exif', None):
                    try:
                        exif_data = ast.literal_eval(item['exif'])  # Convert string to dict
                        for key, value in exif_data.items():
                            metadata[key] = value
                    except Exception as e:
                        print(f"Error parsing EXIF data for {id}: {e}")

                metadata_list.append(metadata)

# Writing the updated metadata into the final JSON file
with open(output_json, "w", encoding="utf-8") as json_file:
    json.dump(metadata_list, json_file, indent=4)
