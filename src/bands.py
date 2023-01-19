import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os 
import glob as glob
from IPython.display import HTML
from utils import make_dir
import collections
from typing import Any, Dict
from gpaw import GPAW   
from tabulate import tabulate 
from collections import namedtuple

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

def TeXlabel(kpt):
    if kpt == 'G':
        kpt = r'$\Gamma$'
    elif '1' in kpt:
        kptsplit = kpt.split('1')[0]
        kpt = r'%s$_{1}$'%(kptsplit)
    elif len(kpt) > 2:
        kpt = kpt[0] + '$_' + kpt[1] + '$'
    return kpt
    
    
#from GPAW
default_parameters: Dict[str, Any] = {
        'pat' : 'XGX1X',
        'npoints':150,
        # 'symmetry': {'point_group': True,
        #              'time_reversal': True,
        #              'symmorphic': True,
        #              'tolerance': 1e-7,
        #              'do_not_symmetrize_the_density': None},  # deprecated
                     }  
    
    
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
        self._fixed_calc      = None
        print(f"Output files (json) will being saved on {diroutput} dir")
        print(tabulate(self._df_to_display, headers = 'keys', tablefmt = 'github')) #pyright: ignore


    def _select_file(self,nofile:int):
        self.ch_file     = self._df_files['gpw File'].iloc[nofile] 
        self._calc_name_ = title(self._df_to_display["gpw File"].iloc[nofile])
        self._out : Dict[str, Any] = {'file': self.ch_file,
                                      'name': self._calc_name_}
                                             
        return self._out
        
        
    def get_calc(self,nofile:int):
        file = self._select_file(nofile)
        print(f"You chose {file['file']}")  
        
        from gpaw import GPAW   #type: ignore
        self._calc_  = GPAW(file['file'])
        return self._calc_ , file['file'], file['name'], nofile
    
    def _get_dos(self,bands,ef,no_of_spins)->tuple:
        # export dos    
        e_up, self.dos_up     = bands.get_dos(spin=self.spin_up)      #pyright: ignore
        e_down, self.dos_down = bands.get_dos(spin=self.spin_down)  #pyright: ignore
        
        self.dos_array = np.zeros((no_of_spins,len(e_up),2))
        self.dos_array[0,:,0] = e_up-ef
        self.dos_array[0,:,1] = self.dos_up 
        self.dos_array[1,:,0] = e_down-ef
        self.dos_array[1,:,1] = -self.dos_down
        dos_up_max = self.dos_up.max()
        dos_down_max = self.dos_down.max()
        results = namedtuple("results",["dos_array","dos_up_max","dos_down_max"])
        return results(self.dos_array,dos_up_max,dos_down_max)
    
        
    def get_bands(self,calc,fixed=False,**kwargs):
        """function to get band structure from specfic gpw file, this function returns an array"""
        
        # if nofile not in self.df_files['File'].iloc[nofile]:
        #     raise IndexError("Does not input number file")
        
        # self.ch_file     = self._df_files['gpw File'].iloc[nofile] 
        # self._calc_name_ = title(self._df_to_display["gpw File"].iloc[nofile])
        # print(f'You chose {self.files_to_dframe[nofile]}')   
        
        self._calc_, self.ch_file, self._calc_name_ , nofile = calc
        if fixed:
            filename = 'fixed_'+self.files_to_dframe[nofile]
            print(filename)
            _calc_bands = self.get_fixed(**kwargs)
        else:
            filename  = self.files_to_dframe[nofile]
            _calc_bands = self._calc_
            
        
        # get bands parameters 
        self.bs          = _calc_bands.band_structure()         #pyright: ignore
        self.fermi_level = _calc_bands.get_fermi_level()        #pyright: ignore
        no_of_spins      = _calc_bands.get_number_of_spins()    #pyright: ignore
        energies         = self.bs.energies-self.fermi_level
        no_of_bands      = _calc_bands.get_number_of_bands()    #pyright: ignore
                
        #from gpaw documentation.
        self.xcoords, label_xcoords, x_labels = self.bs.get_labels()
        e_range          = len(self.xcoords)
        self.ekn_array = np.zeros(( no_of_spins,len(self.xcoords),no_of_bands))

        x_labels = [i if 'K' not in i else "K" for i in x_labels ]
        x_labels = [TeXlabel(i) for i in x_labels]
        
        self.ekn_array[:,:,0]=self.xcoords
        for spin, e_kn in enumerate(energies):
            for col,e_k in enumerate(e_kn.T[1:]):
                self.ekn_array[spin,:,col+1] = e_k
        
        self.dos_results = self._get_dos(_calc_bands,self.fermi_level,no_of_spins)
        
        self.results: Dict[str, Any] = {
                                   'name'         : self._calc_name_,
                                   'energies'     : self.ekn_array.tolist(),
                                   'xcoords'      : self.xcoords.tolist(),
                                   'label_xcoords': label_xcoords.tolist(),
                                   'x_labels'     : x_labels,
                                   'energies_dim' : self.ekn_array.shape,
                                   'dos'          : self.dos_results.dos_array.tolist(),  #pyright: ignore
                                   'dos_max'      : [self.dos_results.dos_up_max,self.dos_results.dos_down_max]  #pyright: ignore
                                   }      

        #export output to json file
        from utils.outfiles import calc2json
        if self.out_json == True:
            try:
                calc2json(self.results,filename,dirsave=self.diroutput)
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
        print(tabulate(self._df_to_display, headers = 'keys', tablefmt = 'github')) #pyright: ignore

    def get_pdos(self,calc,**kwargs):
        self.calc = calc
        self.ef   = self.calc.get_fermi_level()
        self.cell = self.calc.get_atoms()
        self.symbols = self.cell.get_chemical_symbols()
        self.pdos_symbols  =([item for item, count in collections.Counter(self.symbols).items() if count > 1])
        lsymbs = len(self.pdos_symbols)
        
    def get_fixed(self,**kwargs):
        path = kwargs.pop('path','XGX1X')
        npoints = kwargs.pop('npoints',150)       
        self.bp  = self._calc_.atoms.cell.bandpath(path=path,npoints=npoints)  #pyright: ignore
        self._fixed_calc = self._calc_.fixed_density(kpts=self.bp,**kwargs)    #pyright: ignore
        return self._fixed_calc
        
        
        
        
        
       
       
    
        
        
        

    

        
        
        
        
        
        
        























































