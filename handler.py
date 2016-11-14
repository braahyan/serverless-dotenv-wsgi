import logging
import boto3
import os
import settings
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
api = Api(app)

publish_parser = reqparse.RequestParser()
publish_parser.add_argument('AccountId', required=True,
                            help='Account Id is required')

sns_parser = reqparse.RequestParser()
sns_parser.add_argument('Message', required=True,
                        help='Message is required')


class HelloWorld(Resource):
    def __init__(self, **kwargs):
        self.dynamodb = kwargs["dynamodb"]
        self.table = self.dynamodb.Table(os.environ.get("TABLE_NAME"))

    def post(self):
        args = publish_parser.parse_args()
        self.table.put_item(
            Item={
                'AccountId': args['AccountId'],
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Body': request.get_json()
            }
        )
        return "success"


class SnsMessage(Resource):
    def __init__(self, **kwargs):
        pass

    def post(self):
        args = sns_parser.parse_args()
        client = boto3.client('sns')
        arn = "arn:aws:sns:%(region)s:%(accountid)s:%(topicname)s" % {
            "region": "us-east-1",
            "accountid": boto3.client('sts').get_caller_identity().get('Account'),
            "topicname": os.environ.get("TABLE_NAME")
        }
        response = client.publish(
            TopicArn=arn,
            Message=args["Message"],
        )
        return "success"


api.add_resource(HelloWorld, '/rest',
                 resource_class_kwargs={'dynamodb':
                                        boto3.resource('dynamodb')})

api.add_resource(SnsMessage, '/sns')
