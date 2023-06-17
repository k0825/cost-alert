import os
import ast
import json
import boto3
import urllib.request

def get_secret():
    secretmanager = boto3.client('secretsmanager')
    line_channel_secret = secretmanager.get_secret_value(SecretId="LINE_CHANNEL_SECRET")
    return ast.literal_eval(line_channel_secret['SecretString'])['LINE_CHANNEL_SECRET']

def send_message(webhook_url, token, message):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    urllib.request.urlopen(urllib.request.Request(
        webhook_url,
        data=json.dumps({
            'messages': [{
                    'type': 'text',
                    'text': message
                }]}).encode(),
        method='POST',
        headers=headers
    ))

def lambda_handler(event, context):
    line_broadcast_webhook_url = os.getenv('LINE_BROADCAST_WEBHOOK_URL')
    line_channel_secret = get_secret()
    message = event['Recrods'][0]
    send_message(line_broadcast_webhook_url, line_channel_secret, message)