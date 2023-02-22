import json
import os
import sys
import boto3
import base64

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./package"))

import requests

TABLE = os.environ['TABLE_NAME']
TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def handle(event, context):
    # failing to return StatusCode 200 can make telegram api to avoid your bot 
    response_msg = ""
    try: 
        path = event["rawPath"]

        if "bot" in path:
            data = json.loads(event.get("body", "{}"))
            message = str(data["message"]["text"])
            chat_id = data["message"]["chat"]["id"]
            first_name = data["message"]["chat"]["first_name"]

            if "/signup" in message:
                register_account(chat_id, first_name)
                send_message(f"{first_name} has been added to the notification list", chat_id)

            elif "/signoff" in message:
                deregister_account(chat_id)
                send_message(f"{first_name} has been removed from the notification list", chat_id)
            
            elif "/check" in message:
                check = check_account(chat_id)
                confirmation = ('is' if check else 'isn\'t')
                send_message(f"{first_name} {confirmation} registered", chat_id)

            else:
                send_message("command not recognized, the options are:\n - /signup\n - /signoff\n - /check", chat_id)
        
        elif "notify" in path:
            data = event.get("body", "{}")
            if event.get("isBase64Encoded", False):
                print(f"decoding: {data}")
                data = base64.b64decode(data.encode("ascii")).decode("ascii")

            try: 
                data = json.loads(data)
                data_formated = ""
                for key in data.keys():
                    data_formated += f"- {key}: {data.get(key)}\n"
                data = data_formated
            except Exception as e:
                print(f"error decoding json: {e}")

            message = f"Notification:\n{data}"
            notify_accounts(message)
        
        else: 
            return {"statusCode": 201, "body": "Path not found"}

    except Exception as e:
        print()
        response_msg = str(e)
        

    return {"statusCode": 200, "body": response_msg}


def register_account(chat_id,first_name):
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_client.put_item(TableName=TABLE,Item={
        'id': {"S": str(chat_id)},
        'first_name': {"S": first_name},
    })


def deregister_account(chat_id):
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_client.delete_item(TableName=TABLE,Key={
        'id': {"S": str(chat_id)},
    })


def check_account(chat_id):
    dynamodb_client = boto3.client('dynamodb')
    response = dynamodb_client.get_item(TableName=TABLE,Key={
        'id': {"S": str(chat_id)},
    })
    return 'Item' in response


def notify_accounts(message):
    dynamodb_client = boto3.client('dynamodb')
    scan_response = dynamodb_client.scan(TableName=TABLE)
    items = scan_response["Items"]

    for item in items:
        chat_id = item['id']["S"]
        send_message(message, chat_id)
    

def send_message(message, chat_id):
    data = {"text": message.encode("utf8"), "chat_id": chat_id}
    url = BASE_URL + "/sendMessage"
    response = requests.post(url, data)
    print(f"sending message to {chat_id}: {message}")
    print(f"API response code: {str(response.status_code)}")
    print(f"API response body: {str(response.content)}")