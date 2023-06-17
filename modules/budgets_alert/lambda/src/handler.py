import os
import ast
import base64
import json
import boto3
from botocore.exceptions import ClientError
import urllib.request

def get_secret():
    secretsmanager = boto3.client('secretsmanager')
    secret_name = os.getenv('LINE_CHANNEL_ACCESS_TOKEN_ARN')
    try:
        get_secret_value_response = secretsmanager.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        secret = ast.literal_eval(secret)['LINE_CHANNEL_ACCESS_TOKEN']
    return secret

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
    line_channel_access_token = get_secret()
    message = str(event['Records'][0])
    send_message(line_broadcast_webhook_url, line_channel_access_token, message)