import json
import logging
import boto3
import uuid
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_REGION = "ca-central-1"

s3 = boto3.client('s3')
sns = boto3.client('sns')
ses = boto3.client('ses', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb').Table('Messages')

def lambda_handler(event, context):

	for record in event.get('Records', []):
		id = uuid.uuid4()
		bucket = record['s3']['bucket']['name']
		key = record['s3']['object']['key']
		
		response = s3.get_object(Bucket = bucket, Key = key)
		content = response['Body']
		data = json.loads(content.read())

		logger.info(data)

		#log initial message and timestamp
		dynamodb.put_item(
			Item = {
				'message_id': str(id),
				'timestamp': str(datetime.now()),
				'message_content': data
			},
		)

		if 'Message' not in data or data['Message'] == "":
			logger.info("No message included in file")
		else:
			sendEmail(data['Message'], data['Email'], id)
			sendSMS(data['Message'], data['Phone'], id)

def sendEmail(message, address, id):
	SUBJECT = "Notification"
	BODY_TEXT = message
	SENDER = "fall_back_up@hotmail.com"
	RECIPIENT = address
	logger.info("Attempting to Email: " + address)
	try:
		response = ses.send_email(
			Destination={
				'ToAddresses': [
					RECIPIENT,
				],
			},
			Message={
				'Body': {
					'Text': {
						'Data': BODY_TEXT,
					},
				},
				'Subject': {
					'Data': SUBJECT,
				},
			},
			Source=SENDER,
		)
	except Exception as e:
		logger.info("Email did not send")
		logger.exception(e.response['Error']['Message'])
		updateMessageDBItem({
			"email_status": e.response['Error']['Message'],
			"email_status_code": 0
		}, id)

	else:
		logger.info("Email sent successfully")
		updateMessageDBItem({
			"email_status": "Email sent successfully",
			"email_status_code": 1
		}, id)

def sendSMS(message, number, id):
	logger.info("Attempting to Text: " + number)
	try:
		sns.publish(PhoneNumber = number, Message = message)
	except Exception as e:
		logger.info("Text did not send")
		logger.exception(e)
		updateMessageDBItem({
			"text_status": e,
			"text_status_code": 0
		}, id)
	else:
		logger.info("Text sent successfully")
		updateMessageDBItem({
			"text_status": "Text sent successfully",
			"text_status_code": 1
		}, id)

def updateMessageDBItem(map, id):
	attributes, values = expressionBuilder(map)
	logger.info(attributes)
	logger.info(values)
	response = dynamodb.update_item(
		Key={
			'message_id': str(id)
		},
        ExpressionAttributeValues=dict(values),
        UpdateExpression=attributes,
        ReturnValues='ALL_NEW',
	)

def expressionBuilder(map):
	expression = ["set "]
	values = dict()
	for key, value in map.items():
		expression.append(f" {key} = :{key},")
		values[f":{key}"] = value
	return "".join(expression)[:-1], values