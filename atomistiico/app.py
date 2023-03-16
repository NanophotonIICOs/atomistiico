import streamlit as st 
import numpy as np
import matplotlib.pyplot as plt
import py3Dmol


files = []
for i,file in enumerate(sorted(glob.glob("*.xyz"))):
    print(f"{i} ---> {file}")
    files.append(file)

def show_structure(file):
    pts = open(file).read()
    view = py3Dmol.view(width=800,height=500)
    view.addModel(pts,'xyz',{'doAssembly':True,
                                 'duplicateAssemblyAtoms':True,
                                 'normalizeAssembly':True})
    view.setStyle({'sphere':{'colorscheme':'Jmol','scale':0.25},
                    'stick':{'colorscheme':'Jmol', 'radius':0.15}})
    view.addUnitCell()
    view.zoomTo()
    view.zoom(1.75,1.75)
    view.addSurface(py3Dmol.VDW,{'opacity':1,'colorscheme':{'prop':'b','gradient':'sinebow','min':0,'max':70}})
    
    return view.show()

import os
import sentry_sdk
import streamlit as st
from utils import (authors, main_page, sidebar, visualisation)

# from https://github.com/czubert/SERSitiVIS

if os.path.isfile(".streamlit/secrets.toml"):
    if 'sentry_url' in st.secrets:
        sentry_sdk.init(
            st.secrets['sentry_url'],
    
            traces_sample_rate=0.001,
        )
    else:
        print('sentry not running')
else:
    print('Ok!')


def main():
    sidebar.sidebar_head()
    list_options =['Main Page', 'RBN Lab']
    analysis_type = st.sidebar.selectbox("Choose Laboratory",list_options,disabled=False )

    if analysis_type == 'Main Page':
        main_page.main_page()
    if analysis_type == 'RBN Lab':
        laboratory = "computational-lab"
        
    authors.show_developers()


if __name__ == '__main__':
    main()

#SEILYFXLN8Z8BWO0
# python setup.py sdist
