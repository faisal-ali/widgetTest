import json
import boto3

def lambda_handler(event, context):
    print("inside lambda handler")
    print(event)

    ddb = boto3.client('dynamodb')
    response={}

    if event['httpMethod'] == "GET":

        #get item from 'Widgetstable' dyanmodb table
        id = event['queryStringParameters']['id']
        widgetType = event['queryStringParameters']['widgetType']
        response = ddb.get_item(TableName='Widgetstable', Key={'id': {'S': id}, 'widgetType': {'S': widgetType}})

    elif event['httpMethod'] == "POST":
        body = json.loads(event['body'])
        print(body)
        try:
            response = ddb.put_item(
                TableName='Widgetstable',
                Item={
                    'id': {'S': body['id']},
                    'widgetType': {'S': body['widgetType']},
                    'widgetColor': {'S': body['widgetColor']},
                },
                ConditionExpression='attribute_not_exists(id)'
            )
            print("Inserted new widget")
        except:
            print("Widget with id already exists")

    elif event['httpMethod'] == "DELETE":
        #delete item from 'Widgetstable' dyanmodb table
        id = event['queryStringParameters']['id']
        widgetType = event['queryStringParameters']['widgetType']
        response = ddb.delete_item(TableName='Widgetstable', Key={'id': {'S': id}, 'widgetType': {'S': widgetType}})
        print("Deleted widget")
        print(response)

    elif event['httpMethod'] == "PUT":
        body = json.loads(event['body'])
        print(body)
        response = ddb.update_item(
            TableName='Widgetstable',
            ConditionExpression='attribute_exists(id) and attribute_exists(widgetType)',
            Key={
                'id': {'S': body['id']},
                'widgetType': {'S': body['widgetType']}
            },
            UpdateExpression="set #widgetColor=:c",
            ExpressionAttributeNames={
                '#widgetColor': 'widgetColor'
            },
            ExpressionAttributeValues={
                ':c': {'S': body['widgetColor']}
            }
        )
        print("Updated widget")
        print(response)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def listOjectNames(bucketName):
    return "listObjectNames"