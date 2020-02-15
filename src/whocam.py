"""
camera WhoCam class
"""
import cv2
import time
import PIL
from PIL import Image, ImageTk


class WhoCam:
    def __init__(self, device, display=False, twilio=False):
        self.device = device
        self.display = display
        self.twilio = twilio
        print(f"Device: {device}")
        print(f"Display: {display}")
        print(f"Twilio: {twilio}")
        if self.device == "pi":
            from picamera import PiCamera
            from picamera.array import PiRGBArray
            self.camera = PiCamera()
            self.rawCapture = PiRGBArray(self.camera)
            time.sleep(0.1)
        elif self.device == "laptop":
            self.camera = cv2.VideoCapture(0)

    def startVideo(self):
        print("Starting video stream")
        input("Press Enter to continue")

        if self.display:
            print("Showing photo")
            # Wait until key press or closee window
        else:
            print("Not showing photos rn")

        if self.device == "pi":
            self.camera.capture(self.rawCapture, format="bgr")
            img = self.rawCapture.array
        elif self.device == "laptop":
            check, img = self.camera.read()
            # Convert to RGB
            cv2_im = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Read image in PIL format
            img = Image.fromarray(cv2_im)
        else:
            img = Image.open("pie.jpg")

    def takePhoto(self):
        if self.device == "pi":
            self.camera.capture(self.rawCapture, format="bgr")
            img = self.rawCapture.array
        elif self.device == "laptop":
            check, img = self.camera.read()
            # Convert to RGB
            cv2_im = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Read image in PIL format
            img = Image.fromarray(cv2_im)
        else:
            img = Image.open("pie.jpg")

        print("Took a photo")

        if self.display:
            print("Showing photo") # Wait until key press or closee window
        else:
            print("Not showing photos rn")
        return img

    def close(self):
        pass


if __name__ == '__main__':
    whocamera = WhoCam("pi", twilio=True)
    whocamera.takePhoto()

