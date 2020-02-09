"""
camera WhoCam class
"""
# import cv2


class WhoCam:
    def __init__(self, device, display=False, twilio=False):
        self.device = device
        self.display = display
        self.twilio = twilio
        print(f"Device: {device}")
        print(f"Display: {display}")
        print(f"Twilio: {twilio}")

    def startVideo(self):
        print("Starting video stream")
        input("Press Enter to continue")

    def takePhoto(self):
        print("Took a photo")
        if self.display:
            print("Showing photo")
            # Wait until key press or closee window
        else:
            print("Not showing photos rn")

    def close(self):
        pass


if __name__ == '__main__':
    whocamera = WhoCam("pi", twilio=True)
    whocamera.takePhoto()

