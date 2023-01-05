import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from ase.io import write, Trajectory, read
from gpaw import GPAW, FermiDirac
from gpaw.unfold import Unfold, find_K_from_k
import tabulate
import pandas as pd 
import os 
import glob as glob
from IPython.display import HTML


class Bands:
    def __init__(self,path_to_files):
        self.abspath_to_files = os.path.abspath(path_to_files)
        self.path_to_files = path_to_files
        
        if os.path.exists(path_to_files):
            print(f"{self.path_to_files} it's ok")
        else:
            raise FileNotFoundError(f'The {path_to_files} does not exist')
        
        self.files = sorted([i for i in glob.glob(self.abspath_to_files+'/*.gpw')])
        self.df_files = pd.DataFrame(self.files,columns=['File'])
        files_to_dframe = [f.split('/')[-1] for f in self.files]
        df_to_display = pd.DataFrame(files_to_dframe,columns=['File'])
        print(df_to_display.to_string())
    
    def get_bands(self,nofile):
        choice_file = self.df_files['File'].iloc[nofile]    
        self.calc_bands = GPAW(choice_file)
        
        
        
        
        























































