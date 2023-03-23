import json
import numpy as np

def get_json(file):
    with open(file, 'r') as file:
        data = json.load(file)
    return data

class pjson:
    def __init__(self,path) -> None:
        self.data=get_json(path)
        self.energies = None
        self.xcoords  = None
        self.xlabels  = None
        self.xyz      = None
    @property
    def get_data(self):
        return self.data
    
    @property
    def get_energies(self):
        return np.array(self.data['energies'])
    
    @property
    def get_xyz(self): 
        return self.data['xyz']
