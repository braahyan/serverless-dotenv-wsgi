import logging
# this line inclues magic it loads our dotenv file if it is available
import settings
from flask import Flask
from flask_restful import Api
from flask_resources.phone_number import PhoneNumber, PhoneNumberList


logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
api = Api(app)


api.add_resource(PhoneNumber, '/phone_number', '/phone_number/<string:sid>')
api.add_resource(PhoneNumberList, '/phone_number/list')
