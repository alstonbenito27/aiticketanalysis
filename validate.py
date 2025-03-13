import boto3
import pandas as pd
import io
import re
import urllib.parse

def validate_date_format(date_value):
    """Ensure date is in DD-MM-YYYY format."""
    if pd.isnull(date_value):  # Handle NaN values
        return False

    if isinstance(date_value, pd.Timestamp):  
        # Convert Timestamp to string in DD-MM-YYYY format
        date_value = date_value.strftime('%d-%m-%Y')

    date_value = str(date_value)  # Ensure it's a string

    # Regex pattern for DD-MM-YYYY format
    date_pattern = re.compile(r"^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4}$")
    return bool(date_pattern.match(date_value))

def handler(event, context):
    s3_client = boto3.client('s3')
    
    # Check if event contains 'Records' key
    if 'Records' not in event or not event['Records']:
        print("Error: 'Records' key missing or empty in event")
        return {'statusCode': 400, 'body': "Invalid event format"}

    try:
        # Get bucket name and file key from event
        bucket_name = event['Records'][0].get('s3', {}).get('bucket', {}).get('name')
        file_key_encoded = event['Records'][0].get('s3', {}).get('object', {}).get('key')

        if not bucket_name or not file_key_encoded:
            print("Error: Bucket name or file key missing in event")
            return {'statusCode': 400, 'body': "Invalid S3 event structure"}

        if bucket_name != 'dem-forcast-test':
            print(f"File uploaded to the wrong bucket: {bucket_name}. Expected 'dem-forcast-test'.")
            return {'statusCode': 400, 'body': f"Incorrect bucket: {bucket_name}"}
        
        # Decode the file key to handle spaces and special characters
        file_key = urllib.parse.unquote_plus(file_key_encoded)
        
        # Extract username and filename from file path
        path_parts = file_key.split('/')
        username = path_parts[0]
        filename = path_parts[-1]  # Extracts the file name

        # Get file content from S3
        file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = file_obj['Body'].read()

        # Read file into DataFrame WITHOUT automatic date parsing
        if file_key.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content), dtype=str)
        elif file_key.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(file_content), dtype=str, engine='openpyxl')
        else:
            print(f"Unsupported file format: {file_key}")
            return {'statusCode': 400, 'body': "Unsupported file format"}

        # Define the date columns that need validation
        date_columns = ['createdDate']
        invalid_dates = {}

        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True).dt.strftime('%d-%m-%Y')
                df[col] = df[col].astype(str)

                # Find invalid date formats
                invalid_values = df[~df[col].apply(validate_date_format)][col].tolist()
                if invalid_values:
                    invalid_dates[col] = invalid_values

        # Check for validation issues
        if df.isnull().any().any():
            null_columns = df.columns[df.isnull().any()].tolist()
            validation_result = f"Validation failed. Columns with null values: {', '.join(null_columns)}"
        elif invalid_dates:
            validation_result = f"Validation failed. Invalid date formats in columns: {invalid_dates}"
        else:
            validation_result = f"Validation successful for file: {file_key}. No null values or incorrect date formats found."
            
            # Define new bucket and key
            new_bucket_name = "dem-forecast-validated"
            validated_key = f"{username}/{filename}"  # Store under same username with original filename
            
            buffer = io.BytesIO()
            if file_key.endswith('.csv'):
                df.to_csv(buffer, index=False)
            elif file_key.endswith('.xlsx'):
                df.to_excel(buffer, index=False, engine='openpyxl')
            
            buffer.seek(0)
            s3_client.put_object(Bucket=new_bucket_name, Key=validated_key, Body=buffer.getvalue())
            
            print(f"File successfully written to: {new_bucket_name}/{validated_key}")
        
        print(validation_result)
        return {'statusCode': 200, 'body': validation_result}

    except Exception as e:
        error_message = f"Error processing file {file_key}: {str(e)}"
        print(error_message)
        return {'statusCode': 500, 'body': error_message}
