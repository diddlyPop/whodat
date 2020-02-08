"""
camera WhoCam class
"""
# import cv2

class WhoCam:
    def __init__(self, display=False, twilio=False):
        self.launchDisplay = display
        if twilio:
            pass

    def takeVideo(self):
        pass

    def takePhoto(self):
        pass

    def close(self):
        self.window.close()


if __name__ == '__main__':
    whodat = WhoCam(display=True)
    whodat.start()
    whodat.close()
