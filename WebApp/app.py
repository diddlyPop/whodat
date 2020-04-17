from flask import Flask, render_template, send_file, request
#from secret_settings import account_sid, auth_token, from_number, to_number
import os.path
import json

app = Flask(__name__)

account_sid = ""
auth_token = ""
from_number = ""
to_number = ""

@app.route('/' ,methods=['GET','POST'])
def home():
    global account_sid
    global auth_token
    global from_number
    global to_number
    if request.method == 'POST':
        account_sid = request.form.get('twilioAccountSID')
        auth_token = request.form.get('twilioAuthToken')
        from_number = request.form.get('twilioFrom')
        to_number = request.form.get('twilioTo')
        twilioJSON("write")
    return render_template("index.html",account = account_sid, token = auth_token, fromN = from_number, toN = to_number)


@app.route('/video_feed')
def video_feed():
    filename = 'static/WHODAT_Title3.png'
    return send_file(filename, mimetype='image/jpg')

def twilioJSON(operation):
    global account_sid
    global auth_token
    global from_number
    global to_number

    if (operation == "read"):
        with open('twilio.json', 'r') as twilioFile:
            data = twilioFile.read()
        twilioObject = json.loads(data)
        account_sid = twilioObject['account_sid']
        auth_token = twilioObject['auth_token']
        from_number = twilioObject['from_number']
        to_number = twilioObject['to_number']

    if (operation == "write"):
        with open('twilio.json','w') as twilioFile:
            json.dump({"account_sid":account_sid, "auth_token":auth_token , "from_number":from_number , "to_number":to_number}, twilioFile)

if os.path.exists('twilio.json'):
    twilioJSON("read")
else:
    twilioJSON("write")
