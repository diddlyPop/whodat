from flask import Flask as fl
from flask import Response, redirect, url_for, render_template, request
import cv2
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import threading
import time
from flask import send_file
import os
from twilio.rest import Client as TwilioClient
#from secret_settings import account_sid, auth_token, from_number, to_number

app = fl(__name__)

# This is a necessary step to load the var, but wait to initiate
video_stream = None

# Globals
global outputFrame, lock
global RUN_CAMERA

RUN_CAMERA = False
lock = threading.Lock()
outputFrame = None

ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}


# Recognizer class handles facial recognition functionality
class Recognizer:
    def __init__(self):
        self.DRAW_FRAMES = False
        self.vs = None
        self.delay_cache = {}
        self.delay_cache_threshold = 100
        #self.messenger = TwilioClient(account_sid, auth_token)
        self.default_message = "Whodat? It looks like: "

    def face_trigger(self, name):
        print(f"Recognized {name}")
        if name in self.delay_cache:
            diff = time.time() - self.delay_cache[name]
            print(f"Last seen {diff} seconds ago")
            if diff > self.delay_cache_threshold:
                print("RESET DELAY CACHE FOR THIS NAME")
            # if time diff greater than some threshold, send message
        else:
            self.delay_cache[name] = time.time()
            #message = self.messenger.messages.create(body=self.default_message+name, from_=from_number, to=to_number)

    def run(self):
        print("loading encodings + face detector...")
        data = pickle.loads(open("encodings.pickle", "rb").read())
        detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        print("starting video stream...")
        self.vs = VideoStream(src=0).start()
        time.sleep(2.0)
        fps = FPS().start()
        current_faces = {}
        global outputFrame
        while True:
            frame = self.vs.read()
            frame = imutils.resize(frame, width=500)

            # create greyscale and rgb/brg versions for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # detection using greyscale
            rects = detector.detectMultiScale(gray, scaleFactor=1.1,
                                              minNeighbors=5, minSize=(30, 30),
                                              flags=cv2.CASCADE_SCALE_IMAGE)
            # OpenCV returns bounding box coordinates in (x, y, w, h) order
            # i reordered to (top, right, bottom, left)
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
            # compute the facial embeddings for each face bounding box
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

            for encoding in encodings:
                # attempt to match each face in the input image to our known
                # encodings
                matches = face_recognition.compare_faces(data["encodings"],
                                                         encoding)
                name = "Unknown"

                if True in matches:
                    # index the faces and start a container to keep track of guesses
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    # count each time a face is seen
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    # choose the name with the highest probibility (# of votes of confidence) and append it
                    name = max(counts, key=counts.get)
                names.append(name)
                # draw name and bounding boxes
                for ((top, right, bottom, left), name) in zip(boxes, names):
                    cv2.rectangle(frame, (left, top), (right, bottom),
                                  (167, 167, 167), 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                                0.75, (255, 255, 255), 2)
                    if name in current_faces:
                        current_faces[name] += 1
                    else:
                        current_faces[name] = 1
                    if current_faces[name] == 20:
                        self.face_trigger(name)
                        current_faces.clear()
            if self.DRAW_FRAMES:
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break
                fps.update()
            else:
                with lock:
                    outputFrame = frame.copy()


# Not currently working ?
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_file', methods=['POST'])
def upload_file():
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':  # and allowed_file(photo)
                photo.save(os.path.join('../assets/profiles', photo.filename))

        return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template("index.html")


def gen():
    global outputFrame
    while True:
        (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
        if not flag:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


@app.route('/video_feed')
def video_feed():
    # Global RUN_CAMERA used for determining current program state (if camera is needed)
    if RUN_CAMERA:
        return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        filename = 'static/WHODAT_Title3.png'
        return send_file(filename, mimetype='image/jpg')


if __name__ == "__main__":
    if RUN_CAMERA:
        agent = Recognizer()
        t = threading.Thread(target=agent.run)
        t.daemon = True
        t.start()
    app.run(debug=True, threaded=True, use_reloader=False)  # host='0.0.0.0' keyword to access on another machine
    if RUN_CAMERA:
        agent.vs.stream.release()
