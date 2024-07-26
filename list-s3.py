import boto3
import os
from dotenv import load_dotenv

# Configuration
load_dotenv()

identity_pool_id = os.getenv("identity_pool_id")
user_pool_client_id = os.getenv("user_pool_client_id")
user_pool_id = os.getenv("user_pool_id")

region = "ap-southeast-1"
bucket_name = "example-bucket-singapore"
access_token_file = "id_token.txt"


# Function to read the access token from a file
def read_token_from_file(filename):
    try:
        with open(filename, 'r') as file:
            token = file.read().strip()
        return token
    except Exception as e:
        print(f"Error reading token from file: {e}")
        return None


# Function to get AWS temporary credentials using the Cognito Identity Pool
def get_temporary_credentials(identity_pool_id, access_token):
    try:
        cognito_identity_client = boto3.client('cognito-identity', region_name=region)

        # Get the identity ID
        identity_id_response = cognito_identity_client.get_id(
            IdentityPoolId=identity_pool_id,
            Logins={
                f'cognito-idp.{region}.amazonaws.com/{user_pool_id}': access_token
            }
        )
        identity_id = identity_id_response['IdentityId']

        # Get the temporary credentials
        credentials_response = cognito_identity_client.get_credentials_for_identity(
            IdentityId=identity_id,
            Logins={
                f'cognito-idp.{region}.amazonaws.com/{user_pool_id}': access_token
            }
        )
        credentials = credentials_response['Credentials']
        return credentials
    except Exception as e:
        print(f"Error getting temporary credentials: {e}")
        return None


# Function to list objects in an S3 bucket
def list_s3_objects(bucket_name, credentials):
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=region
        )

        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            for obj in response['Contents']:
                print(obj['Key'])
        else:
            print("No objects found in the bucket.")
    except Exception as e:
        print(f"Error listing objects in S3 bucket: {e}")


# Main function
def main():
    # Read the access token from the file
    access_token = read_token_from_file(access_token_file)
    if access_token:
        # Get temporary AWS credentials
        credentials = get_temporary_credentials(identity_pool_id, access_token)
        if credentials:
            # List objects in the S3 bucket
            list_s3_objects(bucket_name, credentials)

if __name__ == "__main__":
    main()
