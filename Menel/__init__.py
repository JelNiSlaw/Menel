import os
import pathlib

PATH = pathlib.Path(__file__).parent

for var in "JISHAKU_HIDE", "JISHAKU_NO_UNDERSCORE", "JISHAKU_NO_DM_TRACEBACK":
    os.environ[var] = "true"
