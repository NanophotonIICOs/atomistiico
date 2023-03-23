import streamlit as st
import pandas as pd
import plotly.express as px
from atomistiico_utils import  sidebar,utils
import os
import streamlit.components.v1 as components
from atomistiico.visual.visual_structure import Show,atoms_from_xyz_string
# import utils as utils
# from nano_lab import get_data
import py3Dmol

def show_structure(structure,molformat='xyz',style='stick',background='none'):
        xyzview = py3Dmol.view()
        xyzview.addModel(structure,molformat,{'doAssembly':True,
                                 'duplicateAssemblyAtoms':True,
                                 'normalizeAssembly':True})
        xyzview.setStyle({'sphere':{'colorscheme':'Jmol','scale':0.3},
                    'stick':{'colorscheme':'Jmol', 'radius':0.15}})
        
        
        ase_atoms = atoms_from_xyz_string(structure)
        for i, atom in enumerate(ase_atoms):
             xyzview.addLabel(atom.symbol, {'position': {'x': atom.position[0], 'y': atom.position[1], 'z': atom.position[2]}, 'backgroundColor': 'none', 'backgroundOpacity': 0., 'fontColor': 'black', 'fontSize': 17})
        xyzview.setBackgroundColor(background)
        xyzview.zoomTo()
        return xyzview



def get_path():
    import os
    path = os.getenv('PATH')
    path_list = path.split(os.pathsep)
    for i in path_list:
            if 'samples' in i:
                find_path=i
    return find_path
def show_structures():
    # sidebar separating line
    col_left, col_right = st.columns([5, 2])
    with col_right:
        #get_path = sidebar.charge_path()
        #st.dataframe()
        pass

    # Data plotting
    with col_left:
        st.header('Files')
        getpath = get_path()
        samples = os.listdir(get_path())
        ssample = st.selectbox('Select sample',(f'{file}' for file in samples))
        paths = os.listdir(f"{get_path()}/{ssample}")
        spath = st.selectbox('Select path',(f'{file}' for file in paths))
        filepath = os.listdir(f"{get_path()}/{ssample}/{spath}")
        sfile =  st.selectbox('Select file',(f'{file}' for file in filepath if ".json" in file))
        afile = f"{get_path()}/{ssample}/{spath}/{sfile}"
        sstruct= Show(afile).structure        
        struct = show_structure(sstruct)
        components.html(struct._make_html(), height =400,width=700)

        
        
        
        
        
        
    



