import json
import boto3
import datetime
from botocore.exceptions import ClientError
import base64
import ast
import os
import urllib.request
import math


ce = boto3.client('ce')

def lambda_handler(event, context):
    line_channel_access_token = get_secret()
    webhook_url = os.getenv('LINE_BROADCAST_WEBHOOK_URL')

    today = datetime.date.today()
    today_iso = get_today_iso(today)
    begin_of_month_iso = get_begin_of_month_iso(today)
    begin_of_next_month_iso = get_begin_of_next_month_iso(today)

    total_cost = get_total_cost(begin_of_month_iso, begin_of_next_month_iso)
    forecast_cost = get_forecast_cost(today_iso, begin_of_next_month_iso)
    service_costs = get_service_costs(begin_of_month_iso, begin_of_next_month_iso)

    message = create_message(begin_of_month_iso, today_iso, total_cost, forecast_cost, service_costs)
    send_message(webhook_url, line_channel_access_token, message)


    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

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

def create_message(start_date, end_date, total_cost, forecast_cost, service_costs):
    message = f'${start_date}~{end_date}のAWS利用料金は、{round(total_cost, 2)} USD\n'
    message += f'今月のAWS利用料金の予測は、{round(forecast_cost, 2)} USD\n'
    message += 'サービスごとの利用料金は、\n'
    for service_name, service_cost in service_costs.items():
        if not math.isclose(round(service_cost, 2), 0):
            message += f'{service_name}: {round(service_cost, 2)} USD\n'
    return message

def get_total_cost(start_date, end_date):
    res = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=[
            'UnblendedCost',
        ]
    )
    total_cost = float(res['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
    return total_cost

def get_service_costs(start_date, end_date):
    res = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=[
            'UnblendedCost',
        ],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            },
        ]
    )
    service_costs = {}
    for service in res['ResultsByTime'][0]['Groups']:
        service_name = service['Keys'][0]
        service_costs[service_name] = float(service['Metrics']['UnblendedCost']['Amount'])
    return service_costs

def get_forecast_cost(start_date, end_date):
    res = ce.get_cost_forecast(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Metric='UNBLENDED_COST',
        Granularity='MONTHLY'
    )
    forecast_cost = float(res['Total']['Amount'])
    return forecast_cost

def get_today_iso(today):
    return today.isoformat()

def get_begin_of_month_iso(today):
    return datetime.date(today.year, today.month, 1).isoformat()

def get_begin_of_next_month_iso(today):
    return datetime.date(today.year, today.month+1, 1).isoformat()