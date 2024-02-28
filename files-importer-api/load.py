"""
AWS Redshift Data Loading Script

This script is designed to be triggered by an AWS Lambda function in response to S3 events. It copies data from a CSV file stored in an S3 bucket to an Amazon Redshift cluster.

Dependencies:
- Boto3: AWS SDK for Python, used for interacting with AWS services.

Note1: Ensure that the required environment variables are set for AWS access and Redshift configuration. See env_example file.

Note2: This script assumes that the Lambda function is configured to receive S3 events with the necessary permissions.

Author: http://github.com/osmandi
Year: 2024
"""


import boto3
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
    """
    Lambda handler function triggered by S3 events to copy data from a CSV file to Redshift.

    Args:
        event (dict): AWS Lambda event object.
        context (object): AWS Lambda context object.

    Returns:
        None
    """

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
