import logging
import boto3
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


class HelloWorld(Resource):
    def __init__(self, **kwargs):
        self.dynamodb = kwargs["dynamodb"]
        self.table = self.dynamodb.Table('devBiStream')

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


api.add_resource(HelloWorld, '/rest',
                 resource_class_kwargs={'dynamodb':
                                        boto3.resource('dynamodb')})
