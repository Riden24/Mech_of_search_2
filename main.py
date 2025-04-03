import os
import csv
import requests
from bs4 import BeautifulSoup
import time

# Set up folders
SAVE_DIR = "wikipedia_images"
os.makedirs(SAVE_DIR, exist_ok=True)

CSV_FILE = "image_metadata.csv"
HEADERS = {
    "User-Agent": "Lucas_Hines_bot/1.0 (lucas.ah369@gmail.com)"
}
# Do 
# Wikipedia parent page to start from
START_URL = "https://en.wikipedia.org/wiki/Wikipedia:Featured_pictures"

def get_wikipedia_images(start_url, max_images=1000, max_current_count=5):
    visited_subpages = set()
    image_count = 0
    metadata_list = []

    # Step 1: Get all subcategory links
    response = requests.get(start_url, headers=HEADERS)
    if response.status_code != 200:
        print("Failed to access the parent page.")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all subcategory links
    subcategory_links = [
        "https://en.wikipedia.org" + a["href"]
        for a in soup.find_all("a", href=True, title=True)
        if a["title"].startswith("Wikipedia:Featured pictures/")
    ]

    print(f"Found {len(subcategory_links)} subcategories to explore.")

    # Step 2: Visit each subcategory and scrape images
    for subpage in subcategory_links:
        current_count = 0
        if subpage in visited_subpages or image_count >= max_images :
            continue

        visited_subpages.add(subpage)
        print(f"Visiting subcategory: {subpage}")

        sub_response = requests.get(subpage, headers=HEADERS)
        time.sleep(1) 
        if sub_response.status_code != 200:
            print(f"Failed to access {subpage}")
            continue

        sub_soup = BeautifulSoup(sub_response.text, "html.parser")

        # Find all image links with class="mw-file-description"
        image_tags = [
            (a, a.find("img"))
            for a in sub_soup.find_all("a", class_="mw-file-description")
            if a.find("img")
        ]
        print(f"Found {len(image_tags)} images in {subpage}")

        for a_tag, img_tag in image_tags:
            if current_count >= max_current_count:
                break
            img_url = img_tag.get("src")
            current_count +=1
            if not img_url or "upload.wikimedia.org" not in img_url:
                continue

            # Extract metadata
            full_url = "https:" + img_url
            file_page_url = "https://en.wikipedia.org" + a_tag["href"]
            title = a_tag.get("title", "Unknown Title")
            width = int(img_tag.get("data-file-width", 0))
            height = int(img_tag.get("data-file-height", 0))

            # Skip small images
            if width < 200 or height < 200:
                continue

            save_image(full_url, image_count)
            metadata_list.append([image_count, title, width, height , full_url, file_page_url])

            image_count += 1
            if image_count >= max_images:
                break

    save_metadata(metadata_list)

def save_image(url, img_num):
    img_data = requests.get(url, stream=True, headers=HEADERS).content
    img_name = f"image_{img_num}.jpg"
    with open(os.path.join(SAVE_DIR, img_name), "wb") as img_file:
        img_file.write(img_data)
    print(f"Saved: {img_name}")

def save_metadata(metadata_list):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Title", "Width", "Height", "Image URL", "File Page URL"])
        writer.writerows(metadata_list)
    print(f"Metadata saved in {CSV_FILE}")

# Run the scraper
get_wikipedia_images(START_URL, max_images=1000)
