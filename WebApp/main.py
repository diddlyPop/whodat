from flask import Flask as fl
from flask import Response, redirect, url_for, render_template, request
from camera import VideoCamera
import cv2

app = fl(__name__)

# This is a necessary step to load the var, but wait to initiate
video_stream = None


@app.route("/")
def home():
    return render_template("index.html")


def gen(camera):
    global video_stream
    global global_frame

    while True:
        frame = camera.get_frame()

        if frame is not None:
            global_frame = frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    video_stream = VideoCamera()
    return Response(gen(video_stream),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/twilio", methods=["POST", "GET"])
def twilio():
    if request.method == "POST":
        auth = request.form["nm"]

        # some connection to twilio to try api key

        # return a redirect back to twilio page with authentication success/failure
        # if successful, return render_template("twilio_conn_success.html")
        # if failure, do the following:
        return render_template("twilio_conn_failed.html")
    else:
        return render_template("twilio.html")


@app.route("/<usr>")
def user(usr):
    return f"<h1>{usr}</h1>"


if __name__ == "__main__":
    app.run(debug=True)
