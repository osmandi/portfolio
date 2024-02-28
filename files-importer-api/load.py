"""
Project: csv-importer
Description: Get a CSV from S3 to import to Redshift
Author: http://github.com/osmandi
"""

import boto3 # Inside AWS Lambda Runtime
from os import environ

# Get environment variables
aws_access_key_id=environ["awsAccessKey"]
aws_secret_access_key=environ["awsSecretKey"]
region=environ["region"]
redshift_identifier=environ["redshiftIdentifier"]
redshift_db_name=environ["redshiftDbName"]
redshift_username=environ["redshiftUsername"]

client_redshift = boto3.client('redshift-data', region_name=region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

def main(event, context):

    # Get S3 file key
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event["Records"][0]["s3"]["object"]["key"]
    filename = s3_key.split(".")[0]
    extension = s3_key.split(".")[1]
    filename_extension = f"{filename}.{extension}"
    
    # Copy file to redshift
    query_copy = f"""
    copy {filename}
    from 's3://{s3_bucket}/{filename_extension}' 
    CREDENTIALS
    'aws_access_key_id={aws_access_key_id};aws_secret_access_key={aws_secret_access_key}'
    csv
    TIMEFORMAT 'YYYY-MM-DDTHH24:MI:SSZ';
    """
    client_redshift.execute_statement(ClusterIdentifier=redshift_identifier, Database=redshift_db_name, DbUser=redshift_username, Sql=query_copy)
