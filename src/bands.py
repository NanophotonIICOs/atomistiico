import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os 
import glob as glob
from IPython.display import HTML
from utils import make_dir
import collections
from typing import Any, Dict
# from gpaw import GPAW

def  check_files(path_to_files):
    if os.path.exists(path_to_files):
        print(f"{path_to_files} it's ok")
        abspath_to_files = os.path.abspath(path_to_files)
    else:
        raise FileNotFoundError(f'The {path_to_files} does not exist')
    return abspath_to_files

def title(name):
    name = name.split(".gpw")[0].split("_")
    title = r" ".join(name)+"\%"
    return title
    
    
class Bands:
    def __init__(self,path_to_files,out_json=False,diroutput='json'):
        self.abspath_to_files = check_files(path_to_files)
        self.bs               = None
        self.xcoords          = None
        self.ekn_array        = None
        self.ch_file          = None
        self.fermi_level      = None
        self.dos              = None
        self.dos_array        = None
        self.diroutput        = diroutput
        self.files            = sorted(glob.glob(self.abspath_to_files+'/*.gpw'))
        self._df_files        = pd.DataFrame(self.files,columns=['gpw File'])
        self.files_to_dframe  = [f.split('/')[-1] for f in self.files]
        self._df_to_display    = pd.DataFrame(self.files_to_dframe,columns=['gpw File'])
        self.spin_up          = 0
        self.spin_down        = 1
        self.out_json         = out_json
        self._calc_           = None
        self._calc_name_      = None
        print(f"Output files (json) will being saved on {diroutput} dir")
        #display(self.df_to_display)


    def get_calc(self,calc_file) -> None:
        from gpaw import GPAW
        self._calc_  = GPAW(calc_file)
        return self._calc_
        
    def get_bands(self,nofile:int,**kwargs):
        """function to get band structure from specfic gpw file, this function returns an array"""
        
        # if nofile not in self.df_files['File'].iloc[nofile]:
        #     raise IndexError("Does not input number file")
        def pretty(kpt):
            if kpt == 'G':
                kpt = r'$\Gamma$'
            elif len(kpt) == 2:
                kpt = kpt[0] + '$_' + kpt[1] + '$'
            return kpt
        
        self.ch_file     = self._df_files['gpw File'].iloc[nofile] 
        self._calc_name_ = title(self._df_to_display["gpw File"].iloc[nofile])
        print(f'You chose {self.files_to_dframe[nofile]}')   
        
        # get bands parameters 
        _calc_bands      = self.get_calc(self.ch_file)
        self.bs          = _calc_bands.band_structure()
        self.fermi_level = _calc_bands.get_fermi_level()
        no_of_spins      = _calc_bands.get_number_of_spins()
        energies         = self.bs.energies-self.fermi_level
        no_of_bands      = _calc_bands.get_number_of_bands()
                
        #from gpaw documentation.
        self.xcoords, label_xcoords, x_labels = self.bs.get_labels()
        e_range          = len(self.xcoords)
        self.ekn_array = np.zeros(( no_of_spins,len(self.xcoords),no_of_bands))

        x_labels = [i if 'K' not in i else "K" for i in x_labels ]
        x_labels = [pretty(i) for i in x_labels]
        
        self.ekn_array[:,:,0]=self.xcoords
        for spin, e_kn in enumerate(energies):
            for col,e_k in enumerate(e_kn.T[1:]):
                self.ekn_array[spin,:,col+1] = e_k
        
        # export dos    
        e_up, self.dos_up   = _calc_bands.get_dos(spin=self.spin_up,**kwargs)
        e_down, self.dos_down = _calc_bands.get_dos(spin=self.spin_down,**kwargs)
        
        self.dos_array = np.zeros((no_of_spins,len(e_up),2))
        self.dos_array[0,:,0] = e_up-self.fermi_level
        self.dos_array[0,:,1] = self.dos_up 
        self.dos_array[1,:,0] = e_down-self.fermi_level
        self.dos_array[1,:,1] = -self.dos_down
        dos_up_max = self.dos_up.max()
        dos_down_max = self.dos_down.max()
        
        self.results: Dict[str, Any] = {
                                   'name'         : self._calc_name_,
                                   'energies'     : self.ekn_array.tolist(),
                                   'xcoords'      : self.xcoords.tolist(),
                                   'label_xcoords': label_xcoords.tolist(),
                                   'x_labels'     : x_labels,
                                   'energies_dim' : self.ekn_array.shape,
                                   'dos'          : self.dos_array.tolist(),
                                   'dos_max'      : [dos_up_max,dos_down_max]
                                   }      

        #export output to json file
        from utils.outfiles import calc2json
        if self.out_json == True:
            try:
                calc2json(self.results,self.files_to_dframe[nofile],dirsave=self.diroutput)
            except ValueError:
                print(f"Can't created {self.ch_file}!")
        else:
            print("All good!... I hope so :)")
        return self.results

    @property
    def get_dframe(self):
        # Return dataframe with gpw files in terminal
        # if to_print=True returns dataframe to display, this means that shows only name of gpw files in path
        # therefore if to_print=False returns datframe with gpw files with the real path to being found
        return self._df_files
    
    @property
    def show_files(self):
        # Return dataframe with gpw files in terminal
        # if to_print=True returns dataframe to display, this means that shows only name of gpw files in path
        # therefore if to_print=False returns datframe with gpw files with the real path to being found
        from tabulate import tabulate
        print(tabulate(self._df_to_display, headers = 'keys', tablefmt = 'github'))


    def get_pdos(self,calc,**pdos_args):
        self.calc = calc
        self.ef   = self.calc.get_fermi_level()
        self.cell = self.calc.get_atoms()
        self.symbols = self.cell.get_chemical_symbols()
        self.pdos_symbols  =([item for item, count in collections.Counter(self.symbols).items() if count > 1])
        lsymbs = len(self.pdos_symbols)
        
       
       
    
        
        
        

    

        
        
        
        
        
        
        























































