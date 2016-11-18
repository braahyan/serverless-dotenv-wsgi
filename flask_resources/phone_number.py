from twilio.rest import TwilioRestClient
import twilio.twiml
from flask_restful import Resource, reqparse, fields, marshal_with
from flask import request, make_response
import boto3
import os
import logging
import json
from dateutil.parser import parse

client = TwilioRestClient()

purchase_parser = reqparse.RequestParser()
purchase_parser.add_argument('purchase', required=True,
                             help='Number to purchase is required')

phone_number_list_fields = {
    "friendly_name": fields.String(),
    "phone_number": fields.String()
}


phone_number_fields = {
    "sid": fields.String(),
    "friendly_name": fields.String(),
    "phone_number": fields.String()
}

dynamodb = boto3.resource("dynamodb")
phone_mapping_table = dynamodb.Table(
    os.environ.get("PHONE_MAPPING_TABLE_NAME"))

phone_record_table = dynamodb.Table(
    os.environ.get("PHONE_RECORD_TABLE_NAME"))


class PhoneNumber(Resource):
    def __init__(self, **kwargs):
        pass

    @marshal_with(phone_number_fields)
    def get(self):
        return client.phone_numbers.list()

    def put(self, phone_number):
        phone_mapping_table.update_item(
            Key={
                'PhoneNumber': phone_number
            },
            UpdateExpression="set MappedNumber = :r",
            ExpressionAttributeValues={
                ':r': request.get_json()["map_to"]
            },
            ReturnValues="UPDATED_NEW")
        return '', 204

    def delete(self, phone_number):
        response = phone_mapping_table.get_item(
            Key={
                'PhoneNumber': phone_number
            }
        )

        phone_map = response['Item']['Sid']
        client.phone_number.delete(phone_map)

        phone_mapping_table.delete_item(
            Key={
                'PhoneNumber': phone_number,
            })
        return '', 204


class PhoneNumberList(Resource):
    def __init__(self, **kwargs):
        pass

    @marshal_with(phone_number_list_fields)
    def get(self):
        numbers = client.phone_numbers.search(
            area_code=request.args['search'],
            country="US",
            type="local"
        )
        return numbers

    @marshal_with(phone_number_fields)
    def post(self):
        args = purchase_parser.parse_args()
        number_to_purchase = args['purchase']
        number = client.phone_numbers.purchase(
            friendly_name="My Company Line",
            phone_number=number_to_purchase,
            voice_url=os.environ.get('VOICE_RESPONSE_URL'),
            voice_method="GET",
            status_callback=os.environ.get("STATUS_CALLBACK_URL"),
            status_method="POST"
        )
        phone_mapping_table.update_item(
            Key={
                'PhoneNumber': number.phone_number
            },
            UpdateExpression="set Sid = :r",
            ExpressionAttributeValues={
                ':r': number.sid
            },
            ReturnValues="UPDATED_NEW"
        )
        return number


class PhoneNumberRespond(Resource):
    def __init__(self, **kwargs):
        pass

    def get(self):
        to_number = request.args['To']
        response = phone_mapping_table.get_item(
            Key={
                'PhoneNumber': to_number
            }
        )
        item = response['Item']
        resp = twilio.twiml.Response()
        resp.dial(item['MappedNumber'])
        # we do this to force the xml response
        # twilio doesn't send accept headers
        return make_response(str(resp), 200)


class PhoneNumberRecord(Resource):
    def __init__(self, **kwargs):
        pass

    def post(self):
        phone_record_table.put_item(Item={
            "PhoneNumber": request.form['To'],
            "Timestamp": parse(request.form["Timestamp"]).strftime("%Y-%m-%d %H:%M:%S"),
            "Body": json.dumps(request.form)
        })
        return '', 204
