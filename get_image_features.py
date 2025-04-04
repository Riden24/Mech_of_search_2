import os
import json
import torch
import torch

import clip
import numpy as np
import cv2
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from sklearn.cluster import KMeans

# Paths
IMAGE_FOLDER = "wikipedia_images"
OUTPUT_JSON = "annotations.json"

# Load models
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

# Function to extract dominant colors
def get_dominant_colors(image_path, k=3):
    img = cv2.imread(image_path)
    if img is None:
        return []
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.reshape(-1, 3)
    kmeans = KMeans(n_clusters=k, random_state=42).fit(img)
    return [list(map(int, color)) for color in kmeans.cluster_centers_]

# Function to generate a caption
def generate_caption(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = blip_processor(images=image, return_tensors="pt").to(device)
    output = blip_model.generate(**inputs)
    return blip_processor.decode(output[0], skip_special_tokens=True)

# Function to classify image with CLIP
def classify_with_clip(image_path, labels=["a frog", "a bird", "a cat", "a landscape", "a painting"]):
    image = clip_preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    text = clip.tokenize(labels).to(device)
    with torch.no_grad():
        image_features = clip_model.encode_image(image)
        text_features = clip_model.encode_text(text)
        similarity = (image_features @ text_features.T).softmax(dim=-1)
    return labels[similarity.argmax().item()]

# Process images and save results
annotations = {}
for filename in os.listdir(IMAGE_FOLDER):
    if filename.lower().endswith((".jpg", ".png", ".jpeg")):
        image_path = os.path.join(IMAGE_FOLDER, filename)
        print(f"Processing {filename}...")

        try:
            annotations[filename] = {
                "dominant_colors": get_dominant_colors(image_path),
                "caption": generate_caption(image_path),
                "clip_label": classify_with_clip(image_path)
            }
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Save to JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(annotations, f, indent=4)

print(f"Saved results to {OUTPUT_JSON}")
