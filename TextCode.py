import json
import boto3
import random

# boto3 is a Python client  used by AWS https://aws.amazon.com/sdk-for-python/
pinpoint = boto3.client('pinpoint')

def lambda_handler(event, context):
    messages = ["Captain America: The First Avenger",
                "Iron Man",
                "Thor Ragnarok",
                "Avengers: Infinity War",
                "Avengers: Endgame",
                "Black Panther",
                "Guardians of the Galaxy"
                ]

    Message = random.choice(messages) # Pick a random movie to watch

    pinpoint.send_messages(
        ApplicationId='COPY_APPLICATION_ID_FROM_AWS_PINPOINT',
        MessageRequest={
            'Addresses': {
                '+1XXXXXXXXXX': {'ChannelType': 'SMS'}
            },
            'MessageConfiguration': {
                'SMSMessage': {
                    'Body': Message,
                    'MessageType': 'PROMOTIONAL'
                }
            }
        }
    )
