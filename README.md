# UrtheCast-Notification

## Structure

For this assignment I tried to mirror technologies listed in UrtheCast's development stack. Below is a diagram that displays the architecture used, I'll explain each component in a bit more detail.

![Diagram](https://github.com/Zealen/UrtheCast-Notification/blob/main/images/Diagram.PNG)

### Stack
All resources I need for this project are kept within this Stack. 

#### File Input
Bucket that takes input from user. For now this bucket has no public access, so any user with permissions within my IAM are allowed to dump files into it. The bucket sends out s3:ObjectCreated: events to the Event Handler

#### Event Handler
This lambda function receives events from the File Input bucket. The event(s) gets parsed and sends out two outbound messages:

Text Message: Powered by the SNS API, a text message gets sent out provided a phone number exists in the payload.

Email Message: Powered by the SES API, an email message gets sent out provided en email address exists in the payload.

All logging is pushed to CloudWatch & DynamoDB

#### DynamoDB
Dynamo keeps a log of the processed messages, including:
message_id
message_content
timestamp
email_status_code
email_status
text_status_code
text_status

#### IAMPolicy
A few Custom policies are created to assist the Stack pieces interacting with each other.
SNSPubPolicy
SESCrudPolicy
DynamoDBCrudPolicy

### Build
The build process is comprised of the below components

#### GitHub

#### SAM

#### Build Artifacts

#### CloudFormation

## Assumptions

#### Messages

- All inbound files are to use UTF-8 encoding.
- The size of the message shall be less than the limit of 140 characters to satisfy both email and SMS.
- Files will be in the following JSON format:
{
  "Phone": "11234567890",
  "Email": "dylan.jack.ac@gmail.com",
  "Message": "hi"
}

## How would I improve this given more time?

#### Messages

- Unfortunately, sending SMS messages is only subject 100 free messages in the US only. I have implemented and tested this functionality with my own number however. Perhaps there is an alternative service I could use outside AWS.
- Sending Emails to non-verified accounts is something that you can't do in sandbox mode for SES. I've verified some of my personal email addresses for testing purposes.

#### Lambda

- Rudimentary Error checking was implemented such as not having a message or the message being "". As seen in the documentation, there are many constraints surrounding messages:
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.publish
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.send_email
- Validation / Input for this application might be better suited as an API's job. As mentioned above, there are many formatting validation issues when it comes to phone numbers and email addresses.
- Some variables could be setup as AWS or environment parameters such as the SES region or sender email address
- Functions could be improved to be asynchronous. This would allow email & SMS messages to be send should the other throw an exception.
- Payloads for DB logging and sending email are clunky and made / formatted within the function itself. This could be offloaded to another method to clean / simplify our main functions. Something that dynamically builds DynamoDB expressions would be handy too.

#### Infrastructure

- This app only utilizes SNS a little bit. SNS could be used to provision messages in a multitude of ways with Topics and Subs
- SQS could be used to facilitate high volume traffic.
- Artifacts is sort of a floating bucket that doesn't belong in a Stack. In a regular environment that could be handled much better.
- The lambda function had a single permission added manually, adding the permission in SAM template created a circular dependency.

#### Database

- Initially I span up a Postgres instance with my template, I then switched to Dynamo as I've never used it before. Turns out it was much more simple to work with in this context.
- Most of the datatypes that I'm saving in Dynamo are fit to hold String, so some conversion has to take place in my Lambda script (datetime > string)).