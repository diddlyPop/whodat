from flask import Flask as Fl
from flask import Response, redirect, url_for, render_template, request, send_file
from imutils.video import VideoStream
from imutils.video import FPS
from imutils import paths
import face_recognition
import imutils
import pickle
import cv2
import threading
import time
import os
import json
from twilio.rest import Client as TwilioClient
from datetime import datetime
import pytz
from pytz import timezone

app = Fl(__name__)

# This is a necessary step to load the var, but wait to initiate
video_stream = None

# Globals
global outputFrame
global lock
global RUN_CAMERA
global RUN_TRAINING, TRAINING

# Twilio environments
account_sid = ""
auth_token = ""
from_number = ""
to_number = ""

# training flags
RUN_TRAINING, TRAINING = False, False
# manually change to use camera during runtime
RUN_CAMERA = True
# thread lock
lock = threading.Lock()
# current frame to be displayed
outputFrame = None

ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}


# Trainer class handles encoding from images
class Trainer:
    def __init__(self):
        self.dataset = "../assets/profiles"
        self.encodings = "encodings.pickle"
        self.detection_method = 'hog'   # for better computers use 'cnn'

    def encode(self):
        global RUN_TRAINING
        global Training
        print("quantifying faces...")
        imagePaths = list(paths.list_images(self.dataset))
        knownEncodings = []
        knownNames = []

        for (i, imagePath) in enumerate(imagePaths):
            print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
            name = imagePath.split(os.path.sep)[-2]
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model=self.detection_method)
            encodings = face_recognition.face_encodings(rgb, boxes)
            for encoding in encodings:
                knownEncodings.append(encoding)
                knownNames.append(name)
        print("[INFO] serializing encodings...")
        data = {"encodings": knownEncodings, "names": knownNames}
        f = open(self.encodings, "wb")
        f.write(pickle.dumps(data))
        f.close()
        RUN_TRAINING = False
        TRAINING = False


# Recognizer class handles facial recognition functionality
class Recognizer:
    def __init__(self):
        self.DRAW_FRAMES = False
        self.vs = None
        self.delay_cache = {}
        self.delay_cache_threshold = 100
        self.messenger = None
        self.default_message = "Whodat? It looks like: "
        self.training_agent = Trainer()

    def face_trigger(self, name):
        print(f"Recognized {name}")
        if name in self.delay_cache:
            last_seen = get_pst()
            diff = time.time() - self.delay_cache[name]
            print(f"{name} last seen at {last_seen}")
            if diff > self.delay_cache_threshold:
                print("RESET DELAY CACHE FOR THIS NAME")
                self.delay_cache[name] = time.time()
            # if time diff greater than some threshold, send message
        else:
            self.delay_cache[name] = time.time()
            if account_sid != "":
                self.messenger = TwilioClient(account_sid, auth_token)
                self.messenger.messages.create(body=self.default_message + name, from_=from_number, to=to_number)
            else:
                print("Add your Twilio credentials to start sending messages")

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
        global TRAINING
        while True:
            if not RUN_TRAINING:
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
                else:
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
            else:
                if not TRAINING:
                    TRAINING = True
                    self.training_agent.encode()


@app.route('/start_training', methods=['POST'])
def start_training():
    global RUN_TRAINING
    RUN_TRAINING = True
    return redirect(url_for('home'))


@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'photo' in request.files:
        photo = request.files['photo']
        first_n = request.files['first_name']
        last_n = request.files['last_name']
        if photo.filename != '':  # and allowed_file(photo)
            photo.save(os.path.join(('../assets/profiles/' + first_n + '_' + last_n), photo.filename))
    return redirect(url_for('home'))


@app.route('/', methods=['GET', 'POST'])
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
    return render_template("index.html", account=account_sid, token=auth_token, fromN=from_number, toN=to_number)


@app.route('/video_feed')
def video_feed():
    # Global RUN_CAMERA used for determining current program state (if camera is needed)
    if RUN_CAMERA:
        return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        filename = 'static/WHODAT_Title3.png'
        return send_file(filename, mimetype='image/jpg')


def gen():
    while True:
        (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
        if not flag:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


def twilioJSON(operation):
    global account_sid
    global auth_token
    global from_number
    global to_number
    if operation == "read":
        with open('twilio.json', 'r') as twilioFile:
            data = twilioFile.read()
            twilio_object = json.loads(data)
            account_sid = twilio_object['account_sid']
            auth_token = twilio_object['auth_token']
            from_number = twilio_object['from_number']
            to_number = twilio_object['to_number']

    if operation == "write":
        with open('twilio.json', 'w') as twilioFile:
            json.dump({"account_sid": account_sid, "auth_token": auth_token,
                       "from_number": from_number, "to_number": to_number}, twilioFile)


# Not currently working ?
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_pst():
    last_seen = datetime.now(tz=pytz.utc)
    last_seen = last_seen.astimezone(timezone('US/Pacific'))
    last_seen = last_seen.strftime("%H:%M on %m/%d/%Y")
    return last_seen


if __name__ == "__main__":
    # setup
    if os.path.isfile('twilio.json'):
        twilioJSON("read")
    else:
        twilioJSON("write")

    # start
    if RUN_CAMERA:
        agent = Recognizer()
        t = threading.Thread(target=agent.run)
        t.daemon = True
        t.start()
    app.run(debug=True, threaded=True, use_reloader=False)  # host='0.0.0.0' keyword to access on another machine

    # end
    if RUN_CAMERA:
        agent.vs.stream.release()
