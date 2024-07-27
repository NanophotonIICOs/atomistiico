import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os 
import glob as glob
from .utils.atomistiico_io import make_dir
import collections
from typing import Any, Dict
from gpaw import GPAW   
from tabulate import tabulate 
from collections import namedtuple

def check_files(path_to_files):
    if os.path.exists(path_to_files):
        #print(f"{path_to_files} it's ok")
        abspath_to_files = os.path.abspath(path_to_files)
    else:
        raise FileNotFoundError(f'The {path_to_files} does not exist')
    return abspath_to_files

def title(name,toplot=False):
    name = name.split(".gpw")[0].split("_")
    if toplot:
        title = r" ".join(name)+r'$\epsilon$'
    else:
        title = r"_".join(name) 
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
    def __init__(self,path_to_files,out_json=False,diroutput='json',show_files=True):
        self.abspath_to_files = check_files(path_to_files)
        self.bs               = None
        self.xcoords          = None
        self.ekn_array        = None
        self.selected_file    = None
        self.fermi_level      = None
        self.dos              = None
        self.dos_array        = None
        self.diroutput        = diroutput
        self.files            = sorted(glob.glob(self.abspath_to_files+'/*.gpw'))
        self._df_files        = pd.DataFrame(self.files,columns=['gpw File'])
        self.files_to_dframe  = [f.split('/')[-1] for f in self.files]
        self._df_to_display   = pd.DataFrame(self.files_to_dframe,columns=['gpw File'])
        self.spin_up          = 0
        self.spin_down        = 1
        self.out_json         = out_json
        self._calc            = None
        self._calcname        = None
        self._fixed_calc      = None
        self.file             = None
        self.name2plot        = None
        self.xyz              = None
        
        
        
        #print(f"Output files (json) will being saved on {diroutput} dir")
        if show_files:
            print(tabulate(self._df_to_display, headers = 'keys', tablefmt = 'github'))
        
    def _select_file(self,nofile:int):
        self.selected_file         = self._df_files['gpw File'].iloc[nofile] 
        self.file                  = self._df_to_display["gpw File"].iloc[nofile]
        self._calcname             = title(self.file)
        self._out : Dict[str, Any] = {'file': self.selected_file,
                                      'name': self._calcname}                                  
        return self._out
        
    def write_xyz(self,atoms):
        xyz_string = f"{len(atoms)}\n\n"
        for atom in atoms:
            xyz_string += f"{atom.symbol} {atom.position[0]} {atom.position[1]} {atom.position[2]}\n"
        return xyz_string       
        
    def get_calc(self,nofile:int)->tuple:
        file = self._select_file(nofile)
        # print(f"You chose {self._df_to_display['gpw File'].iloc[nofile]}")  
        from gpaw import GPAW   #type: ignore
        self._calc  = GPAW(file['file'])
        calc_results = namedtuple("calc_results",["gpaw","file","name","nofile"])
        return calc_results(self._calc , file['file'], file['name'], nofile)
    
    def _get_dos(self,bands,ef,no_of_spins,**kwargs)->tuple:
        # export dos    
        try:
            npts = kwargs.pop('npts',2001)
            width = kwargs.pop('width',None)
        except Exception as e:
            raise ValueError("There is an error in the get_dos arguments from **kwargs, verify if it these are correct")      
        e_up, self.dos_up     = bands.get_dos(spin=self.spin_up,npts=npts,width=width)      
        e_down, self.dos_down = bands.get_dos(spin=self.spin_down,npts=npts,width=width)  
        self.dos_array = np.zeros((no_of_spins,len(e_up),2))
        self.dos_array[0,:,0] = e_up-ef
        self.dos_array[0,:,1] = self.dos_up 
        self.dos_array[1,:,0] = e_down-ef
        self.dos_array[1,:,1] = -self.dos_down
        dos_up_max            = self.dos_up.max()
        dos_down_max          = self.dos_down.max()
        results               = namedtuple("results",["dos_array","dos_up_max","dos_down_max"])
        return results(self.dos_array,dos_up_max,dos_down_max)
    
    def get_bands(self,nofile:int,fixed=False,write=False,**kwargs):
        """function to get band structure from specfic gpw file, this function returns an array"""
        
        # if nofile not in self.df_files['File'].iloc[nofile]:
        #     raise IndexError("Does not input number file")
        
        # self.selected_file     = self._df_files['gpw File'].iloc[nofile] 
        # self._calcname = title(self._df_to_display["gpw File"].iloc[nofile])
        # print(f'You chose {self.files_to_dframe[nofile]}')   
        calc               = self.get_calc(nofile)
        self._calc         = calc.gpaw       
        self.selected_file = calc.file       
        self._calcname     = calc.name       
        nofile             = calc.nofile     
        
        
        if fixed:
            filename = 'fixed_'+self.files_to_dframe[nofile]
            _calcbands    = self.get_fixed(write,**kwargs)
            self.name2plot = title(filename,toplot=True)
        else:
            filename  = self.files_to_dframe[nofile]
            _calcbands = self._calc
            self.name2plot = title(filename,toplot=True)
            
        
        # get bands parameters 
        self.bs          = _calcbands.band_structure()        
        self.fermi_level = _calcbands.get_fermi_level()       
        no_of_spins      = _calcbands.get_number_of_spins()   
        no_of_bands      = _calcbands.get_number_of_bands()   
        energies         = self.bs.energies-self.fermi_level

        #from gpaw documentation.
        self.xcoords, label_xcoords, x_labels = self.bs.get_labels()
        self.ekn_array = np.zeros(( no_of_spins,len(self.xcoords),no_of_bands))

        x_labels = [i if 'K' not in i else "K" for i in x_labels ]
        x_labels = [TeXlabel(i) for i in x_labels]
        
        self.ekn_array[:,:,0]=self.xcoords
        for spin, e_kn in enumerate(energies):
            for col,e_k in enumerate(e_kn.T[1:]):
                self.ekn_array[spin,:,col+1] = e_k
        
        self.dos_results = self._get_dos(_calcbands,self.fermi_level,no_of_spins)
        self.xyz = self.write_xyz(self._calc.atoms)
        
        self.results: Dict[str, Any] = {
                                   'name2plot'    : self.name2plot,
                                   'name'         : self._calcname,
                                   'energies'     : self.ekn_array.tolist(),
                                   'xcoords'      : self.xcoords.tolist(),
                                   'label_xcoords': label_xcoords.tolist(),
                                   'x_labels'     : x_labels,
                                   'energies_dim' : self.ekn_array.shape,
                                   'dos'          : self.dos_results.dos_array.tolist(), 
                                   'dos_max'      : [self.dos_results.dos_up_max,self.dos_results.dos_down_max], 
                                   'no_of_bands'  : no_of_bands,
                                   'xyz':self.xyz,
                                   }      

        #export output to json file
        from .utils.atomistiico_io import calc2json
        if self.out_json == True:
            try:
                calc2json(self.results,filename,dirsave=self.diroutput)
            except ValueError:
                print(f"Can't created {self.selected_file}!")
        else:
            print("All good!... I hope so :)")
        return self.results

    @property
    def get_dframe(self):
        # Return dataframe with gpw files in terminal
        # if to_print=True returns dataframe to display, this means that shows only name of gpw files in path
        # therefore if to_print=False returns datframe with gpw files with the real path to being found
        return self._df_files
    
    def show_files(self):
        # Return dataframe with gpw files in terminal
        # if to_print=True returns dataframe to display, this means that shows only name of gpw files in path
        # therefore if to_print=False returns datframe with gpw files with the real path to being found
        from tabulate import tabulate
        print(tabulate(self._df_to_display, headers = 'keys', tablefmt = 'github'))

    def get_pdos(self,calc,**kwargs):
        self.calc = calc
        self.ef   = self.calc.get_fermi_level()
        self.cell = self.calc.get_atoms()
        self.symbols = self.cell.get_chemical_symbols()
        self.pdos_symbols  =([item for item, count in collections.Counter(self.symbols).items() if count > 1])
        lsymbs = len(self.pdos_symbols)
        
    def get_fixed(self,write,**kwargs):    
        try:
            path = kwargs.pop('path','MGKM')
            npoints = kwargs.pop('npoints',100)
        except Exception as e:
            raise ValueError("There is an error in the path, verify if it is correct")      
        
        self.bp  = self._calc.atoms.cell.bandpath(path=path,npoints=npoints) 
        self._fixed_calc = self._calc.fixed_density(kpts=self.bp)            
        if write:
            self._fixed_calc.write(f"{self.diroutput}/fixed_{self._calcname}.gpw")
            print(f"wrtite--->{self.diroutput}/fixed_{self._calcname}.gpw")
        return self._fixed_calc
    
    
    
    
    
    
    
    
    
    
