from flask import Flask, jsonify, make_response, request
import boto3 # Inside AWS Lambda Runtime
from os import environ

app = Flask(__name__)

@app.route("/")
def hello_from_root():
    return jsonify(message='Hello from root!')

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

@app.route("/hired", methods=["GET"])
def hired():
    from time import sleep
    # Get environment variables
    aws_access_key_id=environ["awsAccessKey"]
    aws_secret_access_key=environ["awsSecretKey"]
    region=environ["region"]
    redshift_identifier=environ["redshiftIdentifier"]
    redshift_db_name=environ["redshiftDbName"]
    redshift_username=environ["redshiftUsername"]
    
    client_redshift = boto3.client('redshift-data', region_name=region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    query_hired = """
    SELECT d.id id, d.department, count(1) AS hired
    FROM hired_employees he
    INNER JOIN departments d ON d.id = he.department_id
    WHERE he.datetime between '2021-01-01' and '2021-12-31'
    GROUP BY d.id, d.department;
    """
    response = client_redshift.execute_statement(ClusterIdentifier=redshift_identifier, Database=redshift_db_name, DbUser=redshift_username, Sql=query_hired)

    # Wait query execute_statement
    query_status = client_redshift.describe_statement(Id=response["Id"])
    while query_status["Status"] not in ["FINISHED", "ABORTED", "FAILED"]:
        query_status = client_redshift.describe_statement(Id=response["Id"])
        print(query_status)
        sleep(1) # Wait for 1 second

    result = client_redshift.get_statement_result(Id=response["Id"])
    return make_response(result, 200)

@app.route("/employees", methods=["GET"])
def employees():
    from time import sleep
    # Get environment variables
    aws_access_key_id=environ["awsAccessKey"]
    aws_secret_access_key=environ["awsSecretKey"]
    region=environ["region"]
    redshift_identifier=environ["redshiftIdentifier"]
    redshift_db_name=environ["redshiftDbName"]
    redshift_username=environ["redshiftUsername"]
    
    client_redshift = boto3.client('redshift-data', region_name=region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
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
    response = client_redshift.execute_statement(ClusterIdentifier=redshift_identifier, Database=redshift_db_name, DbUser=redshift_username, Sql=query_employees)

    # Wait query execute_statement
    query_status = client_redshift.describe_statement(Id=response["Id"])
    while query_status["Status"] not in ["FINISHED", "ABORTED", "FAILED"]:
        query_status = client_redshift.describe_statement(Id=response["Id"])
        print(query_status)
        sleep(1) # Wait for 1 second

    result = client_redshift.get_statement_result(Id=response["Id"])
    return make_response(result, 200)

@app.route("/upload", methods=['POST'])
def upload_files():
    if 'csv' in request.files:
        # If file is a csv
        print("There are a file")
        file = request.files.get('csv')
        filename = file.filename
        # Export to S3
        bucket_name = environ["bucketName"]
        s3 = boto3.resource("s3")
        s3.Bucket(bucket_name).upload_fileobj(file, filename)
        return make_response(jsonify(message="File loaded successfully"), 200)
    return make_response(jsonify(message="Error file not uploaded"), 400)
