#!/usr/bin/env python

import PySimpleGUI as sg

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
train_layout = [[sg.Text('Train your Pi to recognize your friends and family')],
                [sg.Button('Train', pad=(80,100)), sg.Button('Test')]]

'''
TODO: Figure out how to link this to Twilio and authenticate
Password field infinite. That's no good
-----------------------------------------
USER will probably provide API key for twilio ^^^
'''
twilio_layout = [[sg.Text('Link your Twilio to receive message updates from WhoDat')],
                 [sg.Text('Log in\t'), sg.Input(key='-USERNAME-')],
                 [sg.Text('Password'), sg.Input(password_char="*", key='-PASSWORD-')],
                 [sg.Button('Log in')]]

# TODO: Fill in with information
about_layout = [[sg.Text('About WhoDat')], [sg.Text('\tINFOMATSION')]]

# This is our predefined layout using our instances from above
layout = [[sg.TabGroup([[sg.Tab('Setup', setup_layout),
                         sg.Tab('Train', train_layout),
                         sg.Tab('Twilio', twilio_layout),
                         sg.Tab('About', about_layout)]],
                       key='-TAB_GROUP-', tab_location='top', selected_title_color='yellow')]]

# This is the window generated sg.Window(Title of the window, our predefined layout)
window = sg.Window('WhoDat').Layout(layout)

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
    # ---- by reducing the length of input by 1 any time it exceeds 10. ----
    if len(values['-PASSWORD-']) > 10:
        window.Element('-PASSWORD-').Update(values['-PASSWORD-'][:-1])
    # ----------------------------------------------------------------------

    print(event, values)

    if event is 'Log in':
        print('You clicked log in')
    if event is None:           # always, always give a way out!
        break

window.close()
