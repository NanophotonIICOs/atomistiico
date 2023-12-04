import streamlit as st 
import numpy as np
import matplotlib.pyplot as plt
import glob
import py3Dmol

import os
# import sentry_sdk
import streamlit as st
from atomistiico_utils import (authors, main_page, sidebar, visualisation)

# from https://github.com/czubert/SERSitiVIS
# Inicializar el AutoReloader con la clase que quieres actualizar automáticamente


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
    list_options =['Main Page', 'Data Analysis']
    analysis_type = st.sidebar.selectbox("Analysis Section",list_options,disabled=False )
    
    if analysis_type == 'Main Page':
        main_page.main_page()
    if analysis_type == 'Data Analysis':
       visualisation.show_structures()
        
    authors.show_developers()


if __name__ == '__main__':
    main()

#SEILYFXLN8Z8BWO0
# python setup.py sdist
