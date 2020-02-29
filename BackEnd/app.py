from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import json
import os.path

app = Flask(__name__)

#Global variables to store twilio username and password
twilioUserName = "-Not Configured-"
twilioApiKey = ""

#Function to return Twilio JSON format
def returnTwilioJSON():
	data = {"userName": twilioUserName, "apiKey": twilioApiKey}
	return data

#Function to update the Twilio username and api key
def updateTwilioJSON(userName, apiKey):
	global twilioUserName
	global twilioApiKey
	twilioUserName = userName
	twilioApiKey = apiKey
	return

#Startup code to read from the twilio.json file and create one if it doesn't exist
if os.path.exists('twilio.json'):
	with open('twilio.json', 'r') as twilioFile:
		data = twilioFile.read()
		twilioObject = json.loads(data)
		updateTwilioJSON(twilioObject['userName'],twilioObject['apiKey'])
else:
	with open('twilio.json','w') as twilioFile:
		json.dump(returnTwilioJSON(), twilioFile)

#Route to return either the twilio api information or to update the information
@app.route("/api/v1/twilio", methods=['GET', 'POST'])
def twilioSettings():
	if request.method == 'POST':
		updateTwilioJSON(request.form['userName'], request.form['apiKey'])
		with open('twilio.json','w') as twilioFile:
			json.dump(returnTwilioJSON(), twilioFile)
		return '', 204
	else:
		return returnTwilioJSON()

#Route to return either the training file or to update it
@app.route("/api/v1/weights", methods=['GET','POST'])
def trainingFileManagement():
	if request.method == 'POST':
		file = request.files['file']
		file.save(secure_filename(file.filename))
		return '', 204
	else:
		try:
			return send_from_directory('', 'dummyFile.txt', as_attachment=True)
		except FileNotFoundError:
				abort(404)
