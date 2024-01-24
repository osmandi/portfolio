"""
Project: Thumbnail generator.
Description: Generate thumbnail from an image.
Author: http://github.com/osmandi
"""

import boto3
from PIL import Image
thumbnail_size = (128, 128)

def thumbnail_generator(filename_original: str, filename_thumbnail: str):

    with Image.open(filename_original) as im:
        im.thumbnail(thumbnail_size)
        im.save(f"{filename_thumbnail}")

def main(event, context):

    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event["Records"][0]["s3"]["object"]["key"]
    filename = s3_key.split("/")[-1].split(".")[0]
    extension = s3_key.split("/")[-1].split(".")[1]
    filename_thumbnail_base = f"{filename}_thumbnail.{extension}"
    filename_original = f"/tmp/{filename}.{extension}"
    filename_thumbnail = f"/tmp/{filename_thumbnail_base}"
 
    # Start s3 client
    s3 = boto3.client("s3")

    # Download image
    s3.download_file(s3_bucket, s3_key, filename_original)

    # Generate thumbnail
    thumbnail_generator(filename_original, filename_thumbnail)

    # Put file to S3
    s3.upload_file(f"{filename_thumbnail}", s3_bucket, f"output/{filename_thumbnail_base}")

    return {
        "message": "Thumbnail generated",
        "event": event
    }
