#!/usr/bin/python
import sys
import requests
from datetime import datetime

url = "https://coulhesrhlyrcvdazrymv3fiba0vhrjl.lambda-url.us-east-1.on.aws/notify"
def send_data(data):
    response = requests.post(url=url, data=data)
    if response.status_code != 200:
        print(f"Api responsed with code({response.status_code}) and message: {str(response.content)} ")

if sys.stdin.isatty():
    message = f"Last command ended at {datetime.now().isoformat()}"
else:
    last_command_result = sys.stdin.read().strip()
    if last_command_result:
        message = f"Last Process output: {last_command_result}"
    else:
        message = f"Last Process with no output."

send_data(message)