from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2



class Face_Recognition:
    def __init__(self):
        self.DRAW_FRAMES = False

    def get_frame(self):
        ret, frame = self.video.read()

        # DO WHAT YOU WANT WITH TENSORFLOW / KERAS AND OPENCV

        ret, jpeg = cv2.imencode('.jpg', frame)

        return jpeg.tobytes()

    def start(self):

        print("loading encodings + face detector...")
        data = pickle.loads(open("encodings.pickle", "rb").read())
        detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        print("starting video stream...")
        vs = VideoStream(src=0).start()
        time.sleep(2.0)
        fps = FPS().start()

        while True:
            frame = vs.read()
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
            if self.DRAW_FRAMES:
                # draw name and bounding boxes
                for ((top, right, bottom, left), name) in zip(boxes, names):
                    cv2.rectangle(frame, (left, top), (right, bottom),
                                  (167, 167, 167), 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                                0.75, (255, 255, 255), 2)
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break
                fps.update()
            else:
                pass

        fps.stop()
        print("elasped time: {:.2f}".format(fps.elapsed()))
        print(" approx. FPS: {:.2f}".format(fps.fps()))
        cv2.destroyAllWindows()
        vs.stop()