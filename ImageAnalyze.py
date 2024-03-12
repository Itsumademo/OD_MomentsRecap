# Pre-requisition

# pip install 'transformers[torch]'
# pip install pillow
# pip install timm
# pip install exifread

import os
import pprint
import datetime as _dt
import requests as _req
import exifread as _reader
import warnings as _warn
import AnalyzeResultModel as _model

from transformers import pipeline
from geopy.geocoders import Nominatim

_warn.filterwarnings('ignore')

def getCaption(image: str): 

    image_to_text = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")

    raw = image_to_text(image)
    for entity in raw: 
        captionText = entity['generated_text']

    caption_analyze = pipeline('sentiment-analysis')(captionText)
    for entity in caption_analyze: 
        is_caption_possitive = entity['label'].lower() == 'POSITIVE'.lower()
        caption_score = entity['score']

    caption = _model.Caption()
    caption.Title = captionText
    caption.IsPositive = is_caption_possitive
    caption.Confidence = caption_score
    return caption

def getTags(image: str):

    object_detection = pipeline("object-detection", model="facebook/detr-resnet-50")
    
    raw = object_detection(image)
    highest_scores = {}

    for item in raw:
        label = item['label']
        score = item['score']
        if label not in highest_scores or score > highest_scores[label]['score']:
            highest_scores[label] = {'score': score}

    tags = []    
    for item in [{'label': label, 'score': highest_scores[label]['score']} for label in highest_scores]:
        tag = _model.Tag()
        tag.Name = item['label']
        tag.Confidence = item['score']
        tags.append(tag)

    return tags

def getExif(image: str):

    exif = {}

    response = _req.get(image)
    with open('temp.jpg', 'wb') as f:
        f.write(response.content)

    with open('temp.jpg', 'rb') as f:
        exif = _reader.process_file(f)

        if 'EXIF DateTimeOriginal' in exif:
            taken_time = str(exif['EXIF DateTimeOriginal'])
            exif.DateTaken = taken_time

        if 'GPS GPSLatitude' in exif and 'GPS GPSLongitude' in exif:
            lat = str(exif['GPS GPSLatitude'])
            lon = str(exif['GPS GPSLongitude'])
            geolocator = Nominatim(user_agent = "VisualStudioCode")
            loc = geolocator.reverse(lat, lon)
            
            location = _model.Location()
            location.County = loc.raw['address']['country']
            location.State = loc.raw['address']['state']
            location.Country = loc.raw['address']['county']
            location.City = loc.raw['address']['city']
            location.PostalCode = loc.raw['address']['postal_code']
            exif.Location = location

    os.remove("temp.jpg")

def getSummarize(paragraph: str, maxLength: int, minLength: int): 
    
    summarizer = pipeline("summarization", model="Falconsai/text_summarization")

    paragraph = "a birthday cake with a bunch of girls in it. a family is celebrating with a birthday cake. children are gathered around a table with cake. a family celebrating with a cake"
    summarizer(paragraph, maxLength, minLength, do_sample = False)

def isQualified(result: _model.Result, startTime: _dt.datetime, endTime: _dt.datetime):

    if (result.Caption == None or 
        result.Caption.IsPositive == False or 
        result.DateTaken == None or 
        result.Location == None):
        return False
    
    dateTaken = _dt.datetime.strptime(result.DateTaken, "%d/%m/%Y").timestamp()

    return startTime <= dateTaken and dateTaken < endTime


def getLocationKey(location: _model.Location, locationLevel = _model.LocationLevel.City):
    if (locationLevel == _model.LocationLevel.State): 
        return location.Country + "_" + location.State
    elif (locationLevel == _model.LocationLevel.County):
        return location.Country + "_" + location.State + "_" + location.County
    elif (locationLevel == _model.LocationLevel.City):
        return location.Country + "_" + location.State + "_" + location.County + "_" + location.City
    else:
        return location.Country + "_" + location.State + "_" + location.County + "_" + location.City + "_" + location.PostalCode


def getFilteredResult(fileUrls, startTime: _dt.datetime, endTime: _dt.datetime):
    
    result = []

    for fileUrl in fileUrls:
        
        exif = getExif(fileUrl)

        currentResult = _model.Result()
        currentResult.Caption = getCaption(fileUrl)
        currentResult.DateTaken = exif.DateTaken
        currentResult.Location = exif.Location
        currentResult.Tags = getTags(fileUrl)

        if (isQualified(currentResult, startTime, endTime)):
            key = getLocationKey(currentResult.Location)
            if key not in result:
                result[key] = []
                result[key].append(currentResult)
            else:
                result[key].append(currentResult)
    
    return result

baseUrl = "C:\\Users\\wechen2\\Downloads\\FHLImages"
urls = []
for x in range(1, 56):
    urls.append(baseUrl + '\\' + 'ImageFile(' + str(x) + ').JPG')
    

result = getFilteredResult(urls, _dt.datetime(2014, 8, 1), _dt.datetime(2016, 6, 1))

pprint.pprint(result)