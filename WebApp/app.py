from flask import Flask, render_template, send_file

app = Flask(__name__)

@app.route('/')

def home():
    return render_template("index1.html")

@app.route('/video_feed')
def video_feed():
    filename = 'static/WHODAT_Title3.png'
    return send_file(filename, mimetype='image/jpg')
