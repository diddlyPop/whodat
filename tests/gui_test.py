"""
gui App class TESTS
"""

import GUI.gui


def test_gui_app():
    test_app = GUI.gui.App()
    assert test_app.did_load


print("TEST GUI APP PASS")

