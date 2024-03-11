# Pre-requisition

# pip install 'transformers[torch]'
# pip install pillow

import json
import warnings
import AnalyzeResultModel

from transformers import pipeline

warnings.filterwarnings('ignore')

image_to_text = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")

caption_json = image_to_text("https://ankur3107.github.io/assets/images/image-captioning-example.png")

for entity in caption_json: 
    caption = entity['generated_text']

is_caption_possitive = 0
caption_quality = 0.0
caption_analyze = pipeline('sentiment-analysis')(caption)

for entity in caption_analyze: 
    is_caption_possitive = entity['label'].lower() == 'POSITIVE'.lower()
    caption_score = entity['label']

print(caption_analyze)