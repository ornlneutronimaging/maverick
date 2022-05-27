import os
from qtpy.uic import loadUi
from maverick import ui
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

root = os.path.dirname(os.path.realpath(__file__))
refresh_image = os.path.join(root, "icons/refresh.png")
settings_image = os.path.join(root, "icons/plotSettings.png")


ANGSTROMS = u"\u212B"
LAMBDA = u"\u03BB"
MICRO = u"\u00B5"
SUB_0 = u"\u2080"


def load_ui(ui_filename, baseinstance):
    ui_filename = os.path.split(ui_filename)[-1]
    ui_path = os.path.dirname(ui.__file__)

    # get the location of the ui directory
    # this function assumes that all ui files are there
    filename = os.path.join(ui_path, ui_filename)

    return loadUi(filename, baseinstance=baseinstance)
