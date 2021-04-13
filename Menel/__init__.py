import logging
import pathlib
import sys

from dotenv import load_dotenv


path = pathlib.Path(__file__).parent
logpath = path.parent.joinpath('.log')

load_dotenv(path.parent.joinpath('.env'), override=True)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_fh = logging.FileHandler(filename=logpath, mode='w', encoding='utf-8')
_ch = logging.StreamHandler(sys.stdout)
_ch.setLevel(logging.INFO)
_fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s:%(module)s] %(message)s'))
_ch.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

log.addHandler(_fh)
log.addHandler(_ch)