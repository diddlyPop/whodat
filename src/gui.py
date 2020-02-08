"""
gui App class
"""
import PySimpleGUI as sg
import cv2
from whocam import WhoCam


class App:
    def __init__(self):
        self.did_load = True
        sg.theme('Dark Amber')

        self.setup_layout = [[sg.Text('Configure settings and finalize setup')]]

        self.lab_layout = [[sg.Text('Train your Pi to recognize your friends and family')],
                           [sg.Button('Train', key='-TRAIN-'), sg.Button('Camera')]]

        self.twilio_layout = [[sg.Text('Link your Twilio to receive message updates from WhoDat')],
                              [sg.Text('Log in\t'), sg.Input(key='-USERNAME-')],
                              [sg.Text('Password\t'), sg.Input(password_char="*", key='-PASSWORD-')],
                              [sg.Text('API Key\t'), sg.Input(key='-API_KEY-')],
                              [sg.Button('Submit')]]

        self.about_layout = [[sg.Text('About WhoDat')],
                             [sg.Text('\tWhoDat was designed by a group of 6 students to\n'
                                      '\tpractice machine learning with python, the use of\n'
                                      '\tAPIs and linking hardware with software. Their\n'
                                      '\timplementation allows you to use your raspberry\n'
                                      '\tpi as a facial recognition system. To get started,\n'
                                      '\tupload images using the \'Lab\' tab and test it out!\n')]]

        self.layout = [[sg.Image('WHODAT_Title3.png', key='-TITLE_IMAGE-'),
                        sg.TabGroup([[sg.Tab('Setup', self.setup_layout),
                                      sg.Tab(' Lab  ', self.lab_layout, key='-LAB-'),
                                      sg.Tab('Twilio', self.twilio_layout),
                                      sg.Tab('About', self.about_layout)]],
                                    key='-TAB_GROUP-', tab_location='left', selected_title_color='yellow')]]

        self.window = sg.Window('WhoDat', self.layout, resizable=True)

    def start(self):
        while True:

            event, values = self.window.Read()

            if event is None:  # always, always give a way out!
                break
            elif event is 'Camera':
                self.launchCamera()
            elif event is 'Submit':
                print('You clicked log in')

    def close(self):
        self.window.close()

    def launchCamera(self):
        cam = WhoCam(display=False)
        cam.start()
        pass


if __name__ == '__main__':
    whodat = App()
    whodat.start()
    whodat.close()
