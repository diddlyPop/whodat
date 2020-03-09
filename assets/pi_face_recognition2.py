from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
	help = "path to where the face cascade resides")
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
args = vars(ap.parse_args())

print("loading encodings + face detector...")
net = cv2.dnn.readNetFromCaffe("deploy.prototxt.txt", "res10_300x300_ssd_iter_140000.caffemodel")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])
print("starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
fps = FPS().start()

while True:
	frame_conf = vs.read()
	frame_conf = imutils.resize(frame_conf, width=400)
	(h, w) = frame_conf.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(frame_conf, (300, 300)), 1.0,
								 (300, 300), (104.0, 177.0, 123.0))
	net.setInput(blob)
	detections = net.forward()

	for i in range(0, detections.shape[2]):
		confidence = detections[0, 0, i, 2]
		if confidence < .95:
			continue
		else:
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

fps.stop()
print("elasped time: {:.2f}".format(fps.elapsed()))
print(" approx. FPS: {:.2f}".format(fps.fps()))
cv2.destroyAllWindows()
vs.stop()