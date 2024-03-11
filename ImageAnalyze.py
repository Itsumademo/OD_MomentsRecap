# Pre-requisition

# pip install 'transformers[torch]'
# pip install pillow
# pip install timm
# pip install exifread

import os
import json
import requests
import exifread
import warnings
import AnalyzeResultModel

from transformers import pipeline
from geopy.geocoders import Nominatim

warnings.filterwarnings('ignore')

result = AnalyzeResultModel.Result()
image = "https://raw.githubusercontent.com/Itsumademo/OD_MomentsRecap/wechen2/resource/B5.jpg"

image_to_text = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")
object_detection = pipeline("object-detection", model="facebook/detr-resnet-50")

# Calculate caption
caption_json = image_to_text(image)
for entity in caption_json: 
    captionText = entity['generated_text']

is_caption_possitive = 0
caption_quality = 0.0
caption_analyze = pipeline('sentiment-analysis')(captionText)
for entity in caption_analyze: 
    is_caption_possitive = entity['label'].lower() == 'POSITIVE'.lower()
    caption_score = entity['score']

caption = AnalyzeResultModel.Caption()
caption.Title = captionText
caption.IsPositive = is_caption_possitive
caption.Confidence = caption_score
result.Caption = caption

# Get tags
od_json = object_detection(image)
highest_scores = {}

for item in od_json:
    label = item['label']
    score = item['score']
    if label not in highest_scores or score > highest_scores[label]['score']:
        highest_scores[label] = {'score': score}

tags = []    
for item in [{'label': label, 'score': highest_scores[label]['score']} for label in highest_scores]:
    tag = AnalyzeResultModel.Tag()
    tag.Name = item['label']
    tag.Confidence = item['score']
    tags.append(tag)

result.Tags = tags

# Get EXIF
response = requests.get(image)
with open('temp.jpg', 'wb') as f:
    f.write(response.content)

with open('temp.jpg', 'rb') as f:
    exif = exifread.process_file(f)

    if 'EXIF DateTimeOriginal' in exif:
        taken_time = str(exif['EXIF DateTimeOriginal'])
        result.DateTaken = taken_time

    if 'GPS GPSLatitude' in exif and 'GPS GPSLongitude' in exif:
        lat = str(exif['GPS GPSLatitude'])
        lon = str(exif['GPS GPSLongitude'])
        geolocator = Nominatim(user_agent = "VisualStudioCode")
        loc = geolocator.reverse(lat, lon)
        
        location = AnalyzeResultModel.Location()
        location.County = location.raw['address']['country']
        location.State = location.raw['address']['state']
        location.Country = location.raw['address']['county']
        location.City = location.raw['address']['city']
        result.Location = location

os.remove("temp.jpg")

print("\n\n\n" + result.toJSON())

summarizer = pipeline("summarization", model="Falconsai/text_summarization")

paragraph = "a birthday cake with a bunch of girls in it. a family is celebrating with a birthday cake. children are gathered around a table with cake. a family celebrating with a cake"
print(summarizer(paragraph, max_length = 10, min_length = 5, do_sample = False))
print("\n\n\n")