import json
import urllib.parse
import boto3
from collections import Counter
from typing import Dict


print('Loading function')

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamoDB = boto3.resource('dynamodb')
sns_client = boto3.client('sns')


def lambda_handler(event, context):
    # Rekognition
    rekognition_Response = rekognition.detect_text(
        Image={'S3Object': {'Bucket': 'imagebucket14062696', 'Name': 'Test.jpg'}})
   
   
     # S3 Bucket
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        # processes the words from rekognition
        wordsFound = []
        textDetections = rekognition_Response['TextDetections']
        for text in textDetections:
            if text['Type'] == "WORD":
                wordsFound.append(text['DetectedText'])

        # Formats those words to return a quantity
        quantity = {}
        for item in wordsFound:
            x = item
            d = Counter(wordsFound)
            quantity[x] = d[x]

        # processes inventory list from DynamoDB
        snsResp = "Items that need to be Ordered are: "
        table = dynamoDB.Table("Inventory")
        inventory = table.scan()['Items']
        for obj in inventory:
            name = obj["name"]
            amount = obj["quantity"]
            
            # Calculates what items need to be returned.
            try:
                current = quantity[name]
                if current == amount:
                    print(name + " stock levels correct")
                else:
                    toOrder = amount - current
                    snsResp += str(toOrder) + "x " + name + ", "
                    print(name, toOrder)
            except Exception:
                snsResp += str(amount) + "x " + name + ", "
                print(name, amount)

        # Sends custom SNS.
        sns_client.publish(TopicArn='arn:aws:sns:us-east-1:796890585344:boxes_foundV2',
                           Message=snsResp, Subject='Stock to Order')

        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        print("BOXES FOUND: " + str(inventory))
        return snsResp
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
