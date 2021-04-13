import logging
import pathlib
import sys

from dotenv import load_dotenv


path = pathlib.Path(__file__).parent

load_dotenv(path.parent.joinpath('.env'), override=True)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_fh = logging.FileHandler(filename=path.parent.joinpath('.log'), mode='w', encoding='utf-8')
_ch = logging.StreamHandler(sys.stdout)

_formatter = logging.Formatter('%(asctime)s [%(levelname)s:%(module)s:%(lineno)d] %(message)s')

_fh.setFormatter(_formatter)
_ch.setFormatter(_formatter)

log.addHandler(_fh)
log.addHandler(_ch)