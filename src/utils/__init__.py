import os 
import io
import sys
import numpy as no
import json
from ase.utils import jsonable

def make_dir(folder):
    if os.path.exists(folder):
        print(f"{folder} dir already exist!")
    else:
        print(f"{folder} dir it's created!")
        os.mkdir(folder)

