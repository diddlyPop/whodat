#!/usr/bin/env python

import PySimpleGUI as sg
import cv2 as cv
import os

# Usage of Tabs in PSG
#
# sg.set_options(background_color='cornsilk4',
#         element_background_color='cornsilk2',
#         input_elements_background_color='cornsilk2')

# Color theme
sg.theme('Dark Amber')

# TODO: Everything settings using sg.set_options
setup_layout = [[sg.Text('Configure settings and finalize setup')]]

'''
TODO: Write code for buttons
Train takes a picture and allows you to enter information; verify with sg.Submit(), go back with sg.Cancel()
Test takes a picture, makes a guess and then asks if it is correct using sg.PopupYesNo()
'''
lab_layout = [[sg.Text('Train your Pi to recognize your friends and family')], [sg.Image(filename='', key='image')],
                [sg.Button('Train', key='-TRAIN-'), sg.Button('Test')]]

'''
TODO: Figure out how to link this to Twilio and authenticate
Password field infinite. That's no good
-----------------------------------------
USER will probably provide API key for twilio ^^^
'''
twilio_layout = [[sg.Text('Link your Twilio to receive message updates from WhoDat')],
                 [sg.Text('Log in\t'), sg.Input(key='-USERNAME-')],
                 [sg.Text('Password'), sg.Input(password_char="*", key='-PASSWORD-')],
                 [sg.Text('API Key'), sg.Input(key='-API_KEY-')],
                 [sg.Button('Log in')]]

# TODO: Fill in with information
# TODO: be concious of duplicating key names, a Button and a Tab with the key 'Train' causes trouble
about_layout = [[sg.Text('About WhoDat')], [sg.Text('\tWhoDat was designed by a group of 6 students to\n'
                                                    '\tpractice machine learning with python, the use of\n'
                                                    '\tAPIs and linking hardware with software. Their\n'
                                                    '\timplementation allows you to use your raspberry\n'
                                                    '\tpi as a facial recognition system. To get started,\n'
                                                    '\tupload images using the \'Lab\' tab and test it out!\n')]]

# This is our predefined layout using our instances from above
layout = [[sg.Image('src/WHODAT_Title3.png', key='-TITLE_IMAGE-'),
           sg.TabGroup([[sg.Tab('Setup', setup_layout),
                         sg.Tab(' Lab  ', lab_layout, key='-LAB-'),
                         sg.Tab('Twilio', twilio_layout),
                         sg.Tab('About', about_layout)]],
                       key='-TAB_GROUP-', tab_location='left', selected_title_color='yellow')]]

# This is the window generated sg.Window(Title of the window, our predefined layout)
window, cap = sg.Window('WhoDat', layout, resizable=True), cv.VideoCapture(0)

while True:

    event, values = window.Read()

    # print(len(values['-PASSWORD-']))
    # print(len(values['-tab_group1-']))

    '''
    TODO: Update on key input or tab switch
    ** Updating shown in terminal recognizes what it's SUPPOSED to do,
        but only updates the gui with button press
    '''
    # ---- This is supposed to limit character input for password field ----
    # ---- by reducing the length of input by 1 any time it exceeds 20. ----
    try:
        if len(values['-PASSWORD-']) > 20:
            window['-PASSWORD-'](values['-PASSWORD-'][:-1])
    except TypeError as e:
        print(f"Error caused by PASSWORD hider, {e}")

    print(event, values)

    if window['-LAB-']:
        while window(timeout=20)[0] is not None:
            window['image'](data=cv.imencode('.png', cap.read()[1])[1].tobytes())

    if event is 'Log in':
        print('You clicked log in')
    if event is None:           # always, always give a way out!
        break

window.close()

