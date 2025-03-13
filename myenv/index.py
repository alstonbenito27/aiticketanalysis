import os
import sys
import boto3
import pandas as pd
import io

# Patch `os.add_dll_directory` if it exists to prevent errors in AWS Lambda
if hasattr(os, "add_dll_directory"):
    os.add_dll_directory = lambda x: None  # No-op function

def lambda_handler(event, context):
    # Initialize the S3 client
    s3_client = boto3.client('s3')

    # Validate if Records exist in the event
    if 'Records' not in event or len(event['Records']) == 0:
        print("Invalid event: No records found.")
        return {
            'statusCode': 400,
            'body': "Invalid event: No records found."
        }

    # Get the bucket name and file key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']

    print(f"Processing file: {file_key} from bucket: {bucket_name}")

    # Validate if the uploaded file is from the correct bucket
    expected_bucket = 'dem-forcast-test'
    if bucket_name != expected_bucket:
        error_msg = f"File uploaded to the wrong bucket: {bucket_name}. Expected '{expected_bucket}'."
        print(error_msg)
        return {
            'statusCode': 400,
            'body': error_msg
        }

    try:
        # Get the file content from S3
        file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = file_obj['Body'].read()

        # Read the file into a DataFrame
        if file_key.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        elif file_key.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            error_msg = f"Unsupported file format: {file_key}"
            print(error_msg)
            return {
                'statusCode': 400,
                'body': error_msg
            }

        # Check for null values in any column
        if df.isnull().any().any():
            null_columns = df.columns[df.isnull().any()].tolist()
            validation_result = f"Validation failed for file: {file_key}. Columns with null values: {', '.join(null_columns)}"
        else:
            validation_result = f"Validation successful for file: {file_key}. No null values found."

        print(validation_result)  # Log the result

        return {
            'statusCode': 200,
            'body': validation_result
        }

    except Exception as e:
        error_message = f"Error processing file {file_key}: {str(e)}"
        print(error_message)
        return {
            'statusCode': 500,
            'body': error_message
        }
