"""
gui App class TESTS
"""

import src.gui


def test_gui_app():
    test_app = src.gui.App()
    assert test_app.name == "WHODAT"


print("TEST GUI APP PASS")

