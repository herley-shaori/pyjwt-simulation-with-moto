import boto3
import jwt
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

identity_pool_id = os.getenv("identity_pool_id")
user_pool_client_id = os.getenv("user_pool_client_id")
user_pool_id = os.getenv("user_pool_id")

cognito_client = boto3.client('cognito-idp')

def sign_up(username, password, email):
    print(identity_pool_id)
    try:
        response = cognito_client.sign_up(
            ClientId=user_pool_client_id,
            Username=username,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
            ],
        )
        print("Sign up successful:", response)
    except ClientError as e:
        print("Error during sign up:", e.response['Error']['Message'])

def confirm_sign_up(username, confirmation_code):
    try:
        response = cognito_client.confirm_sign_up(
            ClientId=user_pool_client_id,
            Username=username,
            ConfirmationCode=confirmation_code,
        )
        print("Confirmation successful:", response)
    except ClientError as e:
        print("Error during confirmation:", e.response['Error']['Message'])

def authenticate(username, password):
    try:
        response = cognito_client.initiate_auth(
            ClientId=user_pool_client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
            },
        )
        print("Authentication successful:", response)
        return response['AuthenticationResult']['IdToken'], response['AuthenticationResult']['AccessToken']
    except ClientError as e:
        print("Error during authentication:", e.response['Error']['Message'])

def decode_token(token):
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print("Decoded Token:", decoded_token)
        return decoded_token
    except Exception as e:
        print(f"Error decoding token: {e}")

def check_aud_claim(decoded_token):
    if 'aud' in decoded_token:
        print("Token contains 'aud' claim.")
    else:
        print("Token does not contain 'aud' claim.")

def save_token_to_file(token, filename):
    try:
        with open(filename, 'w') as file:
            file.write(token)
        print(f"Token saved to {filename}")
    except Exception as e:
        print(f"Error saving token to file: {e}")

# Example usage
username = "testuser"
password = "TestPassword123!"
email = "saya@mailinator.com"
confirmation_code = "443715"  # Replace with the actual confirmation code sent to the user's email

# Uncomment these to run sign up and confirmation
# sign_up(username, password, email)
# confirm_sign_up(username, confirmation_code)

id_token, access_token = authenticate(username, password)
# decoded_id_token = decode_token(id_token)
# check_aud_claim(decoded_id_token)

# Save access_token to a file
filename = "id_token.txt"
save_token_to_file(id_token, filename)