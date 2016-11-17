import logging
# this line inclues magic it loads our dotenv file if it is available
import settings
from flask import Flask
from flask_restful import Api
from flask_resources.phone_number import PhoneNumber, PhoneNumberList, PhoneNumberRespond


logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
api = Api(app)

api.add_resource(PhoneNumber, '/phone_number', '/phone_number/<string:phone_number>')
api.add_resource(PhoneNumberList, '/phone_number/list')
api.add_resource(PhoneNumberRespond, '/phone_number/respond')


if __name__ == '__main__':
	app.run(debug=True)
