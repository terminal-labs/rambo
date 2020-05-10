import json
import os
import site
import tempfile

## GLOBALS
# Create env var indicating where this code lives. This will be used latter by
# Vagrant as a check that the python cli is being used, as well as being a useful var.
PROJECT_LOCATION = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PROJECT_LOCATION, "settings.json"), "r") as f:
    SETTINGS = json.load(f)
PROVIDERS = SETTINGS["PROVIDERS"]
PROJECT_NAME = SETTINGS["PROJECT_NAME"]
CONF_FILES = [f"{PROJECT_NAME}.conf", f"my_{PROJECT_NAME}.conf"]

SITEPACKAGESPATH = site.getsitepackages()[0]
APPDIR = os.path.abspath(os.path.dirname(__file__))
SETUPFILEDIR = os.path.abspath(os.path.join(APPDIR, ".."))
TESTDIR = os.path.abspath(os.path.join(APPDIR, "tests"))
MEMTEMPDIR = "/dev/shm"
VERSION = "0.0.6"
PRINT_VERBOSITY = "high"
EXCLUDED_DIRS = [".DS_Store"]
SETUP_NAME = PROJECT_NAME
EGG_NAME = SETUP_NAME.replace("_", "-")
TEMPDIR = "/tmp"
TEXTTABLE_STYLE = ["-", "|", "+", "-"]
DIRS = [f"{TEMPDIR}/{PROJECT_NAME}"]
MINIMUM_PYTHON_VERSION = (3, 6, 0)
COVERAGERC_PATH = f"{APPDIR}/.coveragerc"
PAYLOADPATH = SITEPACKAGESPATH
