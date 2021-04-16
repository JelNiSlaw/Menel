import pathlib

from dotenv import load_dotenv


PATH = pathlib.Path(__file__).parent

load_dotenv(PATH.parent.joinpath('.env'), override=True)