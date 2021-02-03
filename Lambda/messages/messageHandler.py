import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
sns = boto3.client('sns')

def lambda_handler(event, context):

	for record in event.get('Records', []):
		bucket = record['s3']['bucket']['name']
		key = record['s3']['object']['key']
		data = json.loads(json.dumps(record))
		
		logger.info(data)
		
		if 'Message' not in data or data['Message'] == "":
			logger.info("No message included in file")
		else:
			try:
				logger.info("Processing file from: ")
				sendSMS(data['Message'], data['Phone'])

			except Exception as e:
				logger.exception("Error processing file: ")

def sendEmail(message, address):
	pass

def sendSMS(message, number):
	sns.publish(PhoneNumber = number, TextMessage = message)
	pass

def writeDB(record, db):
	pass