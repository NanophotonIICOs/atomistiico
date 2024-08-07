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
    return lf_value,np.asarray(times)
    
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
                 path_relax="relax/",
                 path_kpts=[],
                 out='.',
                 nspin=1):
        self.prefix = prefix
        self.path_data = path_data
        self.path_files = path_files
        self.path_relax = path_relax
        self.out = out
        self.nspin = nspin
        self.path_kpts = path_kpts
        self.xc_kpts = []
        # read schema-xml to get information
        self.datafile_xml = try_open_file(f"{self.out}/{self.prefix}.save/data-file-schema.xml", "No Schema File")           
        self.relax_file = try_glob_file(f'{self.path_relax}/{self.prefix}*.out', "No Relax File")

    #--------------------------------- to render relax animation -------------------------------------
    
    def extract_atom_positions(self,file_path):
        natoms = int(find_line_2(file_path,"number of atoms").split()[-1])
        with open(file_path, 'r') as file:
            content = file.read()

        # Using a modified regular expression pattern to find the ATOMIC_POSITIONS (crystal) section
        snatom = "\n[^\n]*"*natoms
        pattern = re.compile(fr'ATOMIC_POSITIONS \(angstrom\){snatom}', re.DOTALL)
        matches = pattern.findall(content)
        
        if matches:
            # atomic_positions_lines = matches.group().strip().split('\n')
            tot_arr_pos = []
            for i in matches:
                row_int_arr = []
                for pos in i.split('\n')[1:]:
                    # print(np.array(pos.split()[1:],dtype=float))
                    row_int_arr.append(pos.split()[1:])
                tot_arr_pos.append(np.array(row_int_arr,dtype=float))
            
            return tot_arr_pos
        else:
            print("No match found for the pattern.")
            
    def construct_atoms(self):
        cell_struct = []
        for a in  self.datafile_xml .findall("input/atomic_structure/cell/"):
            cell_struct.append([float(i)*0.529177 for i in a.text.split()])
        
        atom_species=[]
        atom_pos   = []
        for atom in  self.datafile_xml .findall("input/atomic_structure/atomic_positions/atom"):
            atom_species.append(atom.get('name'))
            atom_pos.append([float(i)*0.529177 for i in atom.text.split()])
        new_struct = Atoms(''.join(atom_species),pbc=True)
        new_struct.set_cell(cell_struct)
        new_struct.set_positions(atom_pos)
        return new_struct, atom_species
        
        
    def render(self,bonds_length=3.0):
        initial_struct,atom_species = self.construct_atoms()
        new_pos = initial_struct.copy()
        ar = self.extract_atom_positions(self.relax_file)
        
        path_actual = "./render"
        if os.path.exists(path_actual):
            print("Render path already exist!")
        else:
            print("Create renderr dir to save rleax images!")
            os.makedirs(path_actual)

        for l in range(0,len(ar)):
            bondatoms = []
            new_pos.set_positions(ar[l])
            symbols = new_pos.get_chemical_symbols()
            for i in range(len(new_pos)):
                for j in range(i):
                    if (symbols[i] != symbols[j] == atom_species[0] and
                            new_pos.get_distance(i, j) < bonds_length):
                        bondatoms.append((i, j))
                    elif (symbols[i] != symbols[j] == atom_species[1] and
                        new_pos.get_distance(i, j) < bonds_length):
                        bondatoms.append((i, j))
            
            pov_name = f'{self.prefix}-relax-{l}' + '.pov'
            renderer = write_pov(pov_name, new_pos,
                                rotation=('0x,0y,0z'),
                                radii=0.4,
                                show_unit_cell=0,
                                povray_settings=dict(transparent=True,
                                                    camera_type='perspective',
                                                    canvas_width=720,
                                                    bondlinewidth=0.1,
                                                    bondatoms=bondatoms,
                                                    #textures=textures
                                                    ))
            renderer.render()
            print(f"Create {self.prefix}-relax-{l}")
            
        ini_files = glob.glob("*.ini")
        pov_files = glob.glob("*.pov")
        for i in tqdm(ini_files, desc="Delete ini files"):
            os.remove(i)
        for i in tqdm(pov_files, desc="Delete pov files"):
            os.remove(i)
            
        print(f"Move relax render image to {path_actual}...")
        import shutil
        render_images = glob.glob("./*.png")
        for i in tqdm(render_images):
            shutil.move(i,f"{path_actual}/{i}")
            
                    
    #--------------------------------- Extract info to relax out -------------------------------------------------
    
    def get_info_relax(self,plot=False):
        _,tot_en = find_line(self.relax_file ,"total energy              =")
        _,fe   = find_line(self.relax_file,"the Fermi energy is")
        if tot_en.size>0:
            print(f"Last term tot_en:{tot_en[-1]}")
        if fe.size>0:
            print(f"Last term fe:{fe[-1]}")
            
        if plot:
            fig,(ax1,ax2) = plt.subplots(2,1,figsize=(10,5))
            if len(fe)>0:
                ax2.plot(fe[:,0],fe[:,1],':ro')
                ax2.set_ylabel("Fermi Energy")
                ax2.set_xlabel("Iterations")
                ax2.set_xticks(fe[:,0])
                for i,j in enumerate(fe[:,0]):
                    ax2.axvline(j, linewidth=0.75,ls='--',color='k', alpha=0.5)
                    ax2.hlines(y=fe[i,1] ,xmin=0,xmax=fe[i,0], linewidth=0.75,ls='--',color='k', alpha=0.5)
                ax2.set_xlim(0,len(fe)+1)
            ax1.plot(tot_en[:,0],tot_en[:,1],'-ob')
            ax1.set_xlabel("Iterations")
            ax1.set_ylabel("Total Energy")
            for i in tot_en[:,0]:
                ax1.axvline(i, linewidth=0.75,ls='--',color='k', alpha=0.5)
            plt.show()


                

            
    
    