import numpy as np
import re
import glob as glob 
from ase import Atoms
from ase.data.colors import jmol_colors as chemical_colors
from ase.io.pov import write_pov
from ase.io import read,write
import ase.io as io
from tqdm import tqdm
import matplotlib.pyplot as plt
import os  
import xml.etree.ElementTree as ET
import subprocess

try:
    result = subprocess.run(['latex', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    print("LaTeX is correct. Versión:")
    print(result.stdout.decode())
    plt.rcParams['text.usetex'] = True
except subprocess.CalledProcessError:
        print("LaTeX is not installed.")
except FileNotFoundError:
        print("LaTeX is not installed.")

def TeXlabel(kpt):
    if kpt == 'G':
        kpt = '$\Gamma$'
    elif '1' in kpt:
        kptsplit = kpt.split('1')[0]
        kpt = '%s$_{1}$'%(kptsplit)
    elif len(kpt) > 2:
        kpt = kpt[0] + '$_' + kpt[1] + '$'
        
    return kpt

def find_line(file,text):
    file_o = open(file, 'r')
    Lines = file_o.readlines()
    lf = re.compile(rf"{text}")
    times = []
    count_times = 0
    for line in Lines:
        if lf.search(line):
            lf_value = float(line.split(" ")[-2])
            count_times+=1
            times.append([count_times,lf_value])
    return lf_value
    
    
def find_line_2(file, text):
    file_o = open(file, 'r')
    Lines = file_o.readlines()
    lf = re.compile(rf"{text}")
    for line in Lines:
        if lf.search(line):
            return line.strip()
        
        
        
def try_open_file(path, error_message):
    try:
        return ET.parse(path)
    except Exception as e:
        print(f"{error_message}: {e}")
        return None

def try_glob_file(pattern, error_message):
    try:
        return glob.glob(pattern)[0]
    except IndexError:
        print(f"{error_message}")
        return None


class Qe(object):
    def __init__(self,
                 prefix,
                 out_data='.',
                 out_files='.',
                 eps_data='.',
                 path_kpts=[],
                 nspin=1):
        self.prefix = prefix
        self.out_data = out_data
        self.out_files = out_files
        self.eps_data  = eps_data
        self.nspin = nspin
        self.path_kpts = path_kpts
        self.xc_kpts = []           
        self.file_scf  = try_glob_file(f'{self.out_files}/{self.prefix}*.scf.pw.out', "Error to import SCF file!")
        self.file_nscf = try_glob_file(f'{self.out_files}/{self.prefix}*.nscf.pw.out', "Error to import NSCF file!")
        print(f"SCF file:{self.file_scf}")
        print(f"NSCF file:{self.file_nscf}")

    @property
    def get_kpoints(self):
        try:
            file_xc = try_glob_file(f"{self.out_files}/{self.prefix}*.bands.out", "Error")
            self.file = open(file_xc, 'r')
            self.Lines = self.file.readlines()
            self.lf = re.compile(rf"{'x coordinate'}")
            self.xc_kpts = []
            for line in self.Lines:
                if self.lf.search(line):
                    self.vl = line.split(" ")[-1]
                    self.xc_kpts.append(float(self.vl))
            return self.xc_kpts
        except TypeError:
            print("Neither k-points path data!")
            return np.zeros_like(self.path_kpts)

    @property
    def get_bands(self):
        if self.nspin == 1:
            file = try_glob_file(f"{self.out_data}/{self.prefix}*.bands.gnu", "Gnu file out doesn't exist")
            data_import = np.loadtxt(file)
            k = np.unique(data_import[:, 0])
            bands = np.reshape(data_import[:, 1], (-1, len(k)))
            # dout = np.vstack((k,bands)).T
            return k, bands

    @property
    def get_efermi(self):
        if self.file_nscf and os.path.isfile(self.file_nscf):
            try:
                ef = find_line(self.file_nscf, "the Fermi energy is")
                return ef
            except UnboundLocalError:
                print("NSCF file is incompleted!")
                if self.file_scf and os.path.isfile(self.file_scf):
                    ef = find_line(self.file_scf, "the Fermi energy is")
                    return ef
                else:
                    print("Neither exist SCF or NSCF files, then Ef=0!")
                    return 0
        
    @property
    def edges(self):
        k, bands = self.get_bands
        ef       = self.get_efermi
        nbands =bands - ef
        cb = []
        vb = []
        for i in range(len(nbands)):
            if min(nbands[i])>0:
                cb.append(nbands[i])
            if max(nbands[i])<0:
                vb.append(nbands[i])
        cb = np.array(cb)
        vb = np.array(vb)
        cbmin_index = np.argmin(cb)
        vbmax_index = np.argmin(vb)
        cbmin = cb[0,:][cbmin_index]
        vbmax = vb[-1,:][vbmax_index]
        n = 7
        cb_edge = np.array([k[cbmin_index-n:cbmin_index+n],cb[0,cbmin_index-n:cbmin_index+n]]) 
        vb_edge = np.array([k[vbmax_index-n:vbmax_index+n],vb[-1,vbmax_index-n:vbmax_index+n]])
        cb_edge_point = [k[cbmin_index],cbmin]
        vb_edge_point = [k[vbmax_index],vbmax]
        
        class edge:
            def __init__(self, cb,vb,cb_edge, vb_edge,cb_edge_point,vb_edge_point,cbmin,vbmax):
                self.cb = cb[0,:]
                self.vb = vb[-1,:]
                self.cb_edge = cb_edge.T
                self.vb_edge = vb_edge.T
                self.cb_edge_point = cb_edge_point
                self.vb_edge_point = vb_edge_point
                self.cbmin = cbmin
                self.vbmax = vbmax
                
        return edge(cb,vb,cb_edge, vb_edge,cb_edge_point,vb_edge_point,cbmin,vbmax)

    def plot_bands(self, ax, ymin=None, ymax=None, color="b", ls="-", lw=2, yshift=0, alpha=1,show_Eg=False, **kwargs):
        """
        Plot band structure
        """
        k, bands = self.get_bands
        xmin = np.min(k)
        xmax = np.max(k)
        ef = self.get_efermi
        for band in range(len(bands)):
            ax.plot(k, bands[band, :]-ef+yshift, color=color, ls=ls, lw=lw, alpha=alpha, **kwargs)

        ax.set_ylim(ymin, ymax)
        for i in self.get_kpoints:
            ax.axvline(i,c='k',ls='--',linewidth=0.5, alpha=0.5)
            
        klabels = [TeXlabel(i) for i in self.path_kpts]    
        print
        ax.set_xticks(ticks=self.get_kpoints,labels=[ i for i in klabels])
        ax.axhline(0,c='k',ls='--',lw=0.5,alpha=0.5)
        ax.set_xlim(xmin,xmax)
        ax.set_ylabel(r"\bf{E (eV)}")
        
        if show_Eg==True:
            edges =self.edges
            cb = edges.cb_edge
            vb = edges.vb_edge
            cb_min_point = edges.cb_edge_point
            vb_max_point = edges.vb_edge_point
            ax.plot(cb[:,0],cb[:,1],'bo',ms=3)
            ax.plot(vb[:,0],vb[:,1],'bo',ms=3)
            ax.plot(cb_min_point[0],cb_min_point[1],'ob')
            ax.plot(vb_max_point[0],vb_max_point[1],'ob')


        
    def exportdata(self,filename,dirsave='.'):
            k,bands          = self.get_bands
            ef               = self.get_efermi
            nbnd,klen        = bands.shape
            energies         = bands-ef
            klabel_coords    =  self.get_kpoints            
            ekn_array        = np.zeros((self.nspin,klen,nbnd+1))
            klabels          = [TeXlabel(i) for i in self.path_kpts]
            ekn_array[:,:,0] = k
            edges =self.edges
            cbm     = edges.cb
            vbm     = edges.vb
            cb_edge = edges.cb_edge
            vb_edge = edges.vb_edge
            cb_min_point = edges.cb_edge_point
            vb_max_point = edges.vb_edge_point
            
            for spin in range(self.nspin):
                ekn_array[spin,:,1:] = energies.T
                
            
            results: Dict[str, Any] = {
                                   'name'           : self.prefix,
                                   'energies'       : ekn_array.tolist(),
                                   'k'              : k.tolist(),
                                   'klabels_coords' : klabel_coords,
                                   'klabels'        : klabels,
                                   'energies_dim'   : ekn_array.shape,
                                   'nbnd'           : nbnd,
                                   'cbm'            : cbm.tolist(),
                                   'vbm'            : vbm.tolist(),
                                   'cbm_edge'       : cb_edge.tolist(),
                                   'vbm_edge'       : vb_edge.tolist(),
                                   'cbm_point'      : cb_min_point,
                                   'vbm_point'      : vb_max_point
                                   } 
            
            
            from .utils.atomistiico_io import calc2json
            try:
                calc2json(results,filename,dirsave)
            except ValueError:
                print(f"Can't created {dirsave}/{filename}!")

    # optical properties:
    @property
    def get_eps(self):
        epsr=[ ]
        epsi=[ ]
        epsr_files=[ ]
        epsi_files=[ ]
        epsrx_exp2tex = [ ]
        epsix_exp2tex = [ ]
        epsry_exp2tex = [ ]
        epsiy_exp2tex = [ ]
        epsrz_exp2tex = [ ]
        epsiz_exp2tex = [ ]
        
        epsr_files = sorted(glob.glob(f"{self.eps_data}/epsr*.dat"))
        epsi_files = sorted(glob.glob(f"{self.eps_data}/epsi*.dat"))
        if not epsr_files or not epsi_files  :
            print(f"There are not epsilon files in: {self.eps_data}")
        else:
            for i,j in zip(epsr_files,epsi_files):
                epsr_i = np.loadtxt(i, unpack=True, comments='#',skiprows=5)
                epsi_j = np.loadtxt(j, unpack=True, comments='#',skiprows=5)
                epsr.append(epsr_i.T)
                epsi.append(epsi_j.T)
        
            for i  in range(len(epsr)):
                epsrx = epsr[i][:,1]
                epsry = epsr[i][:,2]
                epsrz = epsr[i][:,3]
                epsix = epsi[i][:,1]
                epsiy = epsi[i][:,2]
                epsiz = epsi[i][:,3]
                epsrx_exp2tex.append(epsrx)
                epsry_exp2tex.append(epsry)
                epsrz_exp2tex.append(epsrz)
                epsix_exp2tex.append(epsix)
                epsiy_exp2tex.append(epsiy)
                epsiz_exp2tex.append(epsiz)
                
            npepsrx =np.vstack((np.array(epsr[0][:,0]),np.asarray(epsrx_exp2tex))).T
            npepsry =np.vstack((np.array(epsr[0][:,0]),np.asarray(epsry_exp2tex))).T
            npepsrz =np.vstack((np.array(epsr[0][:,0]),np.asarray(epsrz_exp2tex))).T

            npepsix =np.vstack((np.array(epsi[0][:,0]),np.asarray(epsix_exp2tex))).T
            npepsiy =np.vstack((np.array(epsi[0][:,0]),np.asarray(epsiy_exp2tex))).T
            npepsiz =np.vstack((np.array(epsi[0][:,0]),np.asarray(epsiz_exp2tex))).T
                
            class return_epsilon:
                def __init__(self, epsr,epsi,epsr_files,epsi_files,npepsrx,npepsry,npepsrz,npepsix,npepsiy,npepsiz):
                    self.epsr = epsr
                    self.epsi = epsi
                    self.epsr_files = epsr_files
                    self.epsi_files = epsi_files
                    self.npepsrx = npepsrx
                    self.npepsry = npepsry
                    self.npepsrz = npepsrz
                    self.npepsix = npepsix
                    self.npepsiy = npepsiy
                    self.npepsiz = npepsiz
            return return_epsilon(epsr,epsi,epsr_files,epsi_files,npepsrx,npepsry,npepsrz,npepsix,npepsiy,npepsiz)


    
    
    