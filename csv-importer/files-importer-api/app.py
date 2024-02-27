from flask import Flask, jsonify, make_response, request
import boto3 # Inside AWS Lambda Runtime

app = Flask(__name__)


@app.route("/")
def hello_from_root():
    return jsonify(message='Hello from root!')


@app.route("/hello")
def hello():
    return jsonify(message='Hello from path!')

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

@app.route("/upload", methods=['POST'])
def upload_files():
    if 'csv' in request.files:
        # If file is a csv
        print("There are a file")
        file = request.files.get('csv')
        # Export to S3
        bucket_name = "osmandi-sls-csv-importer"
        s3 = boto3.resource("s3")
        s3.Bucket(bucket_name).upload_fileobj(file, "test.csv")
    else:
        return jsonify(message="Not csv file"), 400
    return jsonify(message="Hello")
