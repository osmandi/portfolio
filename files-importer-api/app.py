"""
AWS Flask Application

This Flask application interacts with AWS services such as Amazon Redshift and Amazon S3 to perform data analytics tasks. It provides endpoints for retrieving information about hired employees, analyzing employee data, and uploading CSV files to an S3 bucket.

Endpoints:
- /: Hello message from the root.
- /hired: Retrieve data about hired employees from Redshift.
- /employees: Analyze employee data from Redshift.
- /upload: Upload a CSV file to an S3 bucket.

Dependencies:
- Flask: Web framework for building APIs.
- Boto3: AWS SDK for Python, used for interacting with AWS services.

Note: Ensure that the required environment variables are set for AWS access and Redshift configuration. See env_example file.

Author: http://github.com/osmandi
Year: 2024
"""

from flask import Flask, jsonify, make_response, request
import boto3
from os import environ

app = Flask(__name__)


@app.route("/")
def hello_from_root():
    """
    Endpoint to get a hello message from the root.

    Returns:
        JSON: A JSON response with a hello message.
    """

    return jsonify(message="Hello from root!")


@app.errorhandler(404)
def resource_not_found(e):
    """
    Error handler for 404 Not Found.

    Args:
        e: Exception object.

    Returns:
        JSON: A JSON response indicating the resource was not found.
    """

    return make_response(jsonify(error="Not found!"), 404)


@app.route("/hired", methods=["GET"])
def hired():
    """
    Endpoint to retrieve hired employees data from Redshift.

    Returns:
        JSON: A JSON response with the result of the query.
    """

    from time import sleep

    # Get environment variables
    aws_access_key_id = environ["awsAccessKey"]
    aws_secret_access_key = environ["awsSecretKey"]
    region = environ["region"]
    redshift_identifier = environ["redshiftIdentifier"]
    redshift_db_name = environ["redshiftDbName"]
    redshift_username = environ["redshiftUsername"]

    client_redshift = boto3.client(
        "redshift-data",
        region_name=region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    query_hired = """
    SELECT d.id id, d.department, count(1) AS hired
    FROM hired_employees he
    INNER JOIN departments d ON d.id = he.department_id
    WHERE he.datetime between '2021-01-01' and '2021-12-31'
    GROUP BY d.id, d.department;
    """
    response = client_redshift.execute_statement(
        ClusterIdentifier=redshift_identifier,
        Database=redshift_db_name,
        DbUser=redshift_username,
        Sql=query_hired,
    )

    # Wait query execute_statement
    query_status = client_redshift.describe_statement(Id=response["Id"])
    while query_status["Status"] not in ["FINISHED", "ABORTED", "FAILED"]:
        query_status = client_redshift.describe_statement(Id=response["Id"])
        print(query_status)
        sleep(1)  # Wait for 1 second

    result = client_redshift.get_statement_result(Id=response["Id"])
    return make_response(result, 200)


@app.route("/employees", methods=["GET"])
def employees():
    """
    Endpoint to retrieve employees data from Redshift.

    Returns:
        JSON: A JSON response with the result of the query.
    """

    from time import sleep

    # Get environment variables
    aws_access_key_id = environ["awsAccessKey"]
    aws_secret_access_key = environ["awsSecretKey"]
    region = environ["region"]
    redshift_identifier = environ["redshiftIdentifier"]
    redshift_db_name = environ["redshiftDbName"]
    redshift_username = environ["redshiftUsername"]

    client_redshift = boto3.client(
        "redshift-data",
        region_name=region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    query_employees = """
    WITH base AS (
    SELECT d.department, j.job, extract(quarter FROM he.datetime) as quarter
    FROM hired_employees he
    INNER JOIN departments d ON d.id = he.department_id
    INNER JOIN jobs j ON j.id = he.job_id
    WHERE he.datetime between '2021-01-01' and '2021-12-31'
    )
    SELECT 
    	department
    	,job
        ,SUM(CASE WHEN quarter = 1 THEN 1 ELSE 0 END) AS Q1
        ,SUM(CASE WHEN quarter = 2 THEN 1 ELSE 0 END) AS Q2
        ,SUM(CASE WHEN quarter = 3 THEN 1 ELSE 0 END) AS Q3
        ,SUM(CASE WHEN quarter = 4 THEN 1 ELSE 0 END) AS Q4
    FROM base b
    GROUP BY department, job
    ORDER BY department, job;
    """
    response = client_redshift.execute_statement(
        ClusterIdentifier=redshift_identifier,
        Database=redshift_db_name,
        DbUser=redshift_username,
        Sql=query_employees,
    )

    # Wait query execute_statement
    query_status = client_redshift.describe_statement(Id=response["Id"])
    while query_status["Status"] not in ["FINISHED", "ABORTED", "FAILED"]:
        query_status = client_redshift.describe_statement(Id=response["Id"])
        print(query_status)
        sleep(1)  # Wait for 1 second

    result = client_redshift.get_statement_result(Id=response["Id"])
    return make_response(result, 200)


@app.route("/upload", methods=["POST"])
def upload_files():
    """
    Endpoint to upload a CSV file to S3.

    Returns:
        JSON: A JSON response indicating the success or failure of the file upload.
    """

    if "csv" in request.files:
        # If file is a csv
        print("There are a file")
        file = request.files.get("csv")
        filename = file.filename
        # Export to S3
        bucket_name = environ["bucketName"]
        s3 = boto3.resource("s3")
        s3.Bucket(bucket_name).upload_fileobj(file, filename)
        return make_response(jsonify(message="File loaded successfully"), 200)
    return make_response(jsonify(message="Error - The file is not a CSV file"), 415)
