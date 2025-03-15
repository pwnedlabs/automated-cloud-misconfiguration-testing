from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Path to your service account key file
credentials = service_account.Credentials.from_service_account_file(
    '/home/hac/Downloads/phantomwave-testing-2-d26bf10d33d7.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

# Get a fresh token
credentials.refresh(Request())
access_token = credentials.token
print(access_token)
