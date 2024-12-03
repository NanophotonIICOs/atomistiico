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
    print("LaTeX is correct.")
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
        
def find_levels(file):
    file_o = open(file, 'r')
    Lines = file_o.readlines()
    for line in Lines:
        if "highest occupied, lowest unoccupied level (ev):" in line: 
            values = line.split()[-2::]
            ef = (float(values[0])+float(values[1]))/2
            break
        elif "highest occupied level (ev):" in line: 
            values = line.split()[-2::]
            ef = float(values[1])
            break
    return ef

    
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

def try_glob_files(pattern, error_message):
    try:
        return glob.glob(pattern)
    except IndexError:
        print(f"{error_message}")
        return None

class Qe(object):
    def __init__(self,
                 prefix,
                 scf_files='.',
                 nscf_files=',',
                 band_files='.',
                 eps_files='.',
                 path_kpts=[],
                 nspin=1):
        self.prefix = prefix
        self.band_files = band_files
        self.scf_files = scf_files
        self.nscf_files = nscf_files
        self.eps_files  = eps_files
        self.nspin = nspin
        self.path_kpts = path_kpts
        self.xc_kpts = []           
        self.file_scf  = try_glob_file(f'{self.scf_files}/{self.prefix}*.scf.pw.out', "Error to import SCF file!")
        self.file_nscf = try_glob_file(f'{self.nscf_files}/{self.prefix}*.nscf.pw.out', "Error to import NSCF file!")
        self.file_xc = try_glob_file(f"{self.band_files}/{self.prefix}*.bands.out", "Error")
        print(f"SCF file:{self.file_scf}")
        print(f"NSCF file:{self.file_nscf}")
        print(f"BANDS file:{self.file_xc}")
        self.epsr_files = sorted(try_glob_files(f"{self.eps_files}/epsr_*{self.prefix}.dat", "Error to import Epsilon real file!"))
        self.epsi_files = sorted(try_glob_files(f"{self.eps_files}/epsi_*{self.prefix}.dat", "Error to import Epsilon imaginary file!"))
        print(f"Eps Re files:{self.epsr_files}")
        print(f"Eps Im files:{self.epsi_files}")

    @property
    def get_kpoints(self):
        try:
            self.file = open(self.file_xc, 'r')
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
            file = try_glob_file(f"{self.band_files}/{self.prefix}*.bands.gnu", "Gnu file out doesn't exist")
            data_import = np.loadtxt(file)
            k = np.unique(data_import[:, 0])
            bands = np.reshape(data_import[:, 1], (-1, len(k)))
            # dout = np.vstack((k,bands)).T
            return k, bands
        else:
            file = try_glob_file(f"{self.band_files}/{self.prefix}*.bands.gnu", "Gnu file out doesn't exist")
            data_import = np.loadtxt(file)
            k = np.unique(data_import[:, 0])
            bands = np.reshape(data_import[:, 1], (-1, len(k)))
            # dout = np.vstack((k,bands)).T
            return k, bands
            

    @property
    def get_efermi(self):
        if self.file_nscf:
            try:
                ef = find_line(self.file_nscf, "the Fermi energy is")
                return ef
            except UnboundLocalError:
                try: 
                    ef = find_levels(self.file_nscf)
                    return ef
                except:
                    print("NSCF file error!")
                    if self.file_scf and os.path.isfile(self.file_scf):
                        ef = find_line(self.file_scf, "the Fermi energy is")
                        return ef
                    else:
                        return 0
        else:
                print("NSCF file is incompleted or doesn't exist!")
                if self.file_scf and os.path.isfile(self.file_scf):
                    try:
                        ef = find_line(self.file_scf, "the Fermi energy is")
                        return ef
                    except UnboundLocalError:
                        ef = find_levels(self.file_scf)
                        return ef   
                else:
                    print("Neither exist SCF or NSCF files, then Ef=0!")
                    return 0
                
    @property
    def total_energy(self):
        if self.file_nscf:
                tot_en = find_line(self.file_nscf, "!    total energy")
                return tot_en*13.6057039763
        else:
            tot_en = find_line(self.file_scf, "!    total energy")
            return tot_en*13.6057039763
        
    @property
    def volume_cell(self):
        if self.file_nscf:
                vol_cell = find_line(self.file_nscf, "unit-cell volume")
                return vol_cell*0.148185
        else:
            vol_cell = find_line(self.file_scf, "unit-cell volume")
            return vol_cell*0.148185 
        
    def edges(self,npoints_edge=25):
        k, bands = self.get_bands
        ef       = self.get_efermi
        nbands =bands - ef
        cb = []
        vb = []
        for i in range(len(nbands)):
            if min(nbands[i])>0.05:
                cb.append(nbands[i])
            if max(nbands[i])<0.05 :
                vb.append(nbands[i])
        cb = np.array(cb)
        vb = np.array(vb)
        cbm = cb[0,:]
        vbm = vb[-1,:]
        cbmin_index = cb[0].argmin()
        vbmax_index = vb[-1].argmax()
        cbmin = cb[0,:][cbmin_index]
        vbmax = vb[-1,:][vbmax_index]
        n = npoints_edge
        cbm_edge = np.array([k[cbmin_index-n:cbmin_index+n],cb[0,cbmin_index-n:cbmin_index+n]+ef ]) 
        vbm_edge = np.array([k[vbmax_index-n:vbmax_index+n],vb[-1,vbmax_index-n:vbmax_index+n]+ef]) 
        cbm_point = [k[cbmin_index],cbmin+ef]
        vbm_point = [k[vbmax_index],vbmax+ef]
        
        class edge:
            def __init__(self, cbm,vbm,cbm_edge, vbm_edge,cbm_point,vbm_point,cbmin,vbmax):
                self.cbm = cb[0,:]+ef
                self.vbm = vb[-1,:]+ef
                self.cbm_edge = cbm_edge.T
                self.vbm_edge = vbm_edge.T 
                self.cbm_point = cbm_point 
                self.vbm_point = vbm_point  
                self.cbmin = cbmin 
                self.vbmax = vbmax 
                
        return edge(cb,vb,cbm_edge, vbm_edge,cbm_point,vbm_point,cbmin,vbmax)

    def plot_bands(self, ax, ymin=None, ymax=None, color="b", ls="-", lw=2, alpha=1,show_Eg=False,npoints_edge=25, **kwargs):
        """
        Plot band structure
        """
        k, bands = self.get_bands
        xmin = np.min(k)
        xmax = np.max(k)
        ef = self.get_efermi
        for band in range(len(bands)):
            ax.plot(k, bands[band, :]-ef, color=color, ls=ls, lw=lw, alpha=alpha, **kwargs)

        ax.set_ylim(ymin, ymax)
        for i in self.get_kpoints:
            ax.axvline(i,c='k',ls='--',linewidth=0.5, alpha=0.5)
            
        klabels = [TeXlabel(i) for i in self.path_kpts]    
        print
        ax.set_xticks(ticks=self.get_kpoints,labels=[ i for i in klabels])
        ax.axhline(0,c='k',ls='--',lw=0.5,alpha=0.5)
        ax.set_xlim(xmin,xmax)
        ax.set_ylabel("$E-E_f$ (eV)")
        
        if show_Eg==True:
            edges =self.edges(npoints_edge=npoints_edge)
            cbm = edges.cbm_edge
            vbm = edges.vbm_edge
            cbm_point = edges.cbm_point
            vbm_point = edges.vbm_point
            ax.plot(cbm[:,0],cbm[:,1]-ef,'bo',ms=3)
            ax.plot(vbm[:,0],vbm[:,1]-ef,'bo',ms=3)
            ax.plot(cbm_point[0],cbm_point[1]-ef,'ob')
            ax.plot(vbm_point[0],vbm_point[1]-ef,'ob')


        
    def exportdata(self,filename,dirsave='.',npoint_edges=25):
            k,bands          = self.get_bands
            ef               = self.get_efermi
            nbnd,klen        = bands.shape
            energies         = bands-ef
            klabel_coords    =  self.get_kpoints            
            ekn_array        = np.zeros((self.nspin,klen,nbnd+1))
            klabels          = [TeXlabel(i) for i in self.path_kpts]
            ekn_array[:,:,0] = k
            tot_en           = self.total_energy 
            vol_cell         = self.volume_cell
            edges = self.edges(npoint_edges)
            cbm     = edges.cbm
            vbm     = edges.vbm
            cbm_edge = edges.cbm_edge
            vbm_edge = edges.vbm_edge
            cbm_point = edges.cbm_point
            vbm_point = edges.vbm_point
            
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
                                   'cbm_edge'       : cbm_edge.tolist(),
                                   'vbm_edge'       : vbm_edge.tolist(),
                                   'cbm_point'      : cbm_point,
                                   'vbm_point'      : vbm_point,
                                   'tot_en'         : tot_en,
                                   'vol_cell'       : vol_cell,
                                   'ef'             : ef
                                   } 
            if not self.epsr_files or not self.epsi_files  :
                pass
            else:
                geps = self.get_eps
                epsrx = geps.npepsrx
                epsry = geps.npepsry
                epsrz = geps.npepsrz
                epsix = geps.npepsix
                epsiy = geps.npepsiy
                epsiz = geps.npepsiz
                epsr_labels = geps.epsr_labels
                epsi_labels = geps.epsi_labels
                results.update({
                                'epsrx' : epsrx.tolist(),
                                'epsry' : epsry.tolist(),
                                'epsrz' : epsrz.tolist(),
                                'epsix' : epsix.tolist(),
                                'epsiy' : epsiy.tolist(),
                                'epsiz' : epsiz.tolist(),
                                'epsr_labels' : epsr_labels,
                                'epsi_labels' : epsi_labels,
                })
                
            
            from .utils.atomistiico_io import calc2json
            try:
                calc2json(results,filename,dirsave)
            except ValueError:
                print(f"Can't created {dirsave}/{filename}!")
                
    def exportdata_eps(self,filename,dirsave='.'):    
            results: Dict[str, Any] = {
                                   'name'           : self.prefix,
                                   } 
            if not self.epsr_files or not self.epsi_files  :
                pass
            else:
                geps        = self.get_eps
                eps_en      = geps.eps_energies
                epsrx       = geps.npepsrx
                epsry       = geps.npepsry
                epsrz       = geps.npepsrz
                epsix       = geps.npepsix
                epsiy       = geps.npepsiy
                epsiz       = geps.npepsiz
                epsr_labels = geps.epsr_labels
                epsi_labels = geps.epsi_labels
                alphax      = geps.alphax
                alphay      = geps.alphay
                alphaz      = geps.alphaz
                results.update({
                                'epsrx' : epsrx.tolist(),
                                'epsry' : epsry.tolist(),
                                'epsrz' : epsrz.tolist(),
                                'epsix' : epsix.tolist(),
                                'epsiy' : epsiy.tolist(),
                                'epsiz' : epsiz.tolist(),
                                'epsr_labels' : epsr_labels,
                                'epsi_labels' : epsi_labels,
                                'eps_energies': eps_en.tolist(),
                                'alphax' : alphax.tolist(), 
                                'alphay' : alphay.tolist(),
                                'alphaz' : alphaz.tolist(),
                })
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
        epsrx_exp2tex = [ ]
        epsix_exp2tex = [ ]
        epsry_exp2tex = [ ]
        epsiy_exp2tex = [ ]
        epsrz_exp2tex = [ ]
        epsiz_exp2tex = [ ]
    
        if not self.epsr_files or not self.epsi_files  :
            print(f"There are not epsilon files in: {self.eps_files}")
        else:
            for i,j in zip(self.epsr_files,self.epsi_files):
                epsr_i = np.loadtxt(i, unpack=True, comments='#',skiprows=10)
                epsi_j = np.loadtxt(j, unpack=True, comments='#',skiprows=10)
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
                
            eps_energies = np.asarray(epsr[0][:,0])
            npepsrx =np.vstack((eps_energies,np.asarray(epsrx_exp2tex))).T
            npepsry =np.vstack((eps_energies,np.asarray(epsry_exp2tex))).T
            npepsrz =np.vstack((eps_energies,np.asarray(epsrz_exp2tex))).T

            npepsix =np.vstack((eps_energies,np.asarray(epsix_exp2tex))).T
            npepsiy =np.vstack((eps_energies,np.asarray(epsiy_exp2tex))).T
            npepsiz =np.vstack((eps_energies,np.asarray(epsiz_exp2tex))).T
            
            # alpha
            c         = 2.99792458  # (10^8 m/s)
            hbar      = 6.582119569 # (10^{-16} eV.s)
            #hbar      = 6.582119569E-16  
            alphapref = 2/(hbar*c)  # (10^8 / m or 10^6 / cm) 
            lB        = 20/1.55612398   # scaling factor for monolayer
            alphax  = alphapref * eps_energies * np.sqrt((np.sqrt((lB*npepsrx[:,1])**2+(lB*npepsix[:,1])**2)-(lB*npepsrx[:,1]))/2)
            alphay  = alphapref * eps_energies * np.sqrt((np.sqrt((lB*npepsry[:,1])**2+(lB*npepsiy[:,1])**2)-(lB*npepsry[:,1]))/2)
            alphaz  = alphapref * eps_energies * np.sqrt((np.sqrt((lB*npepsrz[:,1])**2+(lB*npepsiz[:,1])**2)-(lB*npepsrz[:,1]))/2)
                            
            epsr_labels = [i.split("/")[-1].split(".dat")[0].split('-')[-1] for i in self.epsr_files]
            epsi_labels = [i.split("/")[-1].split(".dat")[0].split('-')[-1] for i in self.epsi_files]
            class return_epsilon:
                def __init__(self, epsr,epsi,eps_energies,npepsrx,npepsry,npepsrz,npepsix,npepsiy,npepsiz,epsr_labels,epsi_labels,alphax,alphay,alphaz):
                    self.epsr = epsr
                    self.epsi = epsi
                    self.eps_energies = eps_energies
                    self.npepsrx = npepsrx
                    self.npepsry = npepsry
                    self.npepsrz = npepsrz
                    self.npepsix = npepsix
                    self.npepsiy = npepsiy
                    self.npepsiz = npepsiz
                    self.epsr_labels = epsr_labels
                    self.epsi_labels = epsi_labels
                    self.alphax = alphax
                    self.alphay = alphay
                    self.alphaz = alphaz
            return return_epsilon(epsr,epsi,eps_energies,npepsrx,npepsry,npepsrz,npepsix,npepsiy,npepsiz,epsr_labels,epsi_labels,alphax,alphay,alphaz)

    def plot_eps(self,fig,ymin=None,ymax=None,xmin=None,xmax=None,lw=2,yshift=0,**kwargs):
        geps = self.get_eps
        epsrx = geps.npepsrx
        epsry = geps.npepsry
        epsrz = geps.npepsrz
        epsix = geps.npepsix
        epsiy = geps.npepsiy
        epsiz = geps.npepsiz
        epsr_labels = geps.epsr_labels
        epsi_labels = geps.epsi_labels

        gs = fig.add_gridspec(3, hspace=0)
        axs = gs.subplots(sharex=True, sharey=False)
        
        import matplotlib.colors as mcolors
        from matplotlib.collections import LineCollection
        import matplotlib.cm as cm
        colors = mcolors._colors_full_map

        cmap_x =  plt.colormaps['cool'] 
        cmap_y =  plt.colormaps['summer']       
        
        for px in range(1,epsrx.shape[1]):
            color_x = cmap_x(px / epsrx.shape[1])
            axs[0].plot(epsrx[:,0],epsrx[:,px],color=color_x,label=f"Re-{epsr_labels[px-1]}-x")
            
        for py in range(1,epsry.shape[1]):   
            color_y = cmap_y(py / epsry.shape[1])
            axs[0].plot(epsry[:,0],epsry[:,py],color=color_y,label=f"Re-{epsr_labels[py-1]}-y")
        
        for p in range(1,epsrx.shape[1]):
            color_x = cmap_x(p / epsrx.shape[1])
            axs[1].plot(epsix[:,0],epsix[:,p],color=color_x,label=f"Im-{epsi_labels[p-1]}-x")
            
        for p in range(1,epsry.shape[1]):
            color_y = cmap_y(p / epsry.shape[1])
            axs[1].plot(epsiy[:,0],epsiy[:,p],color=color_y,label=f"Im-{epsi_labels[p-1]}-y")
            
        for p in range(1,epsrz.shape[1]):
            color_x = cmap_x(p / epsrz.shape[1])
            axs[2].plot(epsrz[:,0],epsrz[:,p],color=color_x,label=f"Re-{epsr_labels[p-1]}-z")
            
        for p in range(1,epsiz.shape[1]):   
            color_y = cmap_y(p / epsiz.shape[1])
            axs[2].plot(epsiz[:,0],epsiz[:,p],color=color_y,label=f"Im-{epsi_labels[p-1]}-z")
        
        for ax in axs:
            ax.set_xlim([xmin,xmax])
            ax.set_ylim([ymin,ymax])
            ax.set_ylabel("$\epsilon$ $(\omega)$")
            ax.legend(ncol=2,loc=1,frameon=False)
            
        axs[2].set_xlabel("Energy (eV)")
        return axs
        
        
        
class Strain(object):
    def __init__(self,structure):
        self.structure = structure
    
    def uniaxial(self,strain,axis=0):
        """
        Aplica una deformación uniaxial a la estructura.
        strain: valor de la deformación (positivo para tensión, negativo para compresión)
        axis: dirección de la deformación (0 (default) para x, 1 para y, 2 para z)
        """
        newstr = self.structure.copy()
        cell   =   newstr.get_cell()
        cell[axis] *= (1 + (strain/100))
        newstr.set_cell(cell, scale_atoms=True)
        return newstr
    
    def biaxial(self,strain,axes=(0, 1)):
        """
        Aplica una deformación biaxial a la estructura.
        strain: valor de la deformación (positivo para tensión, negativo para compresión)
        axes: tupla con las dos direcciones de la deformación (por defecto, plano xy)
        """
        newstr = self.structure.copy()
        cell = newstr.get_cell()
        for axis in axes:
            cell[axis] *= (1 + (strain/100))
        newstr.set_cell(cell, scale_atoms=True)
        return newstr
    
    def anisoxy_strain(self,strainx,strainy):
        newstr = structure.copy()
        cell = newstr.get_cell()
        cell[0] *= (1 +(strainx/100))
        cell[1] *= (1 +(strainy/100))
        newstr.set_cell(cell, scale_atoms=True)
        return newstr
        