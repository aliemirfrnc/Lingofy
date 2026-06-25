import requests
import os

url = "http://127.0.0.1:8000/api/pronunciation/analyze"

# Create dummy audio file
with open("dummy.webm", "wb") as f:
    f.write(b"dummy data")

# To bypass authentication (assuming we have an endpoint to get a token, but wait, the endpoint requires a user id!)
# Let's check how auth works.
