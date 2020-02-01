"""
gui App class TESTS
"""

import src.gui


def test_gui_app():
    test_app = src.gui.App()
    assert test_app.did_load


print("TEST GUI APP PASS")

