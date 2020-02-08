"""
camera WhoCam class
"""

import cv2 as cv


class WhoCam:
    def __init__(self, display=False, twilio=False):
        self.launchDisplay = display
        if twilio:
            pass

    def start(self):
        cap = cv.VideoCapture(0)

        while (True):
            # Capture frame-by-frame
            ret, frame = cap.read()

            # Our operations on the frame come here
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

            # Display the resulting frame
            if self.launchDisplay:
                cv.imshow('frame', gray)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

    def close(self):
        self.window.close()


if __name__ == '__main__':
    whodat = WhoCam(display=True)
    whodat.start()
    whodat.close()
