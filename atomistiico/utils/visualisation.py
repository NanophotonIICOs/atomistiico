import pandas as pd
import peakutils
import plotly.express as px
import streamlit as st
from utils import  sidebar,utils
# import utils as utils
# from nano_lab import get_data

def visualisation(laboratory):
    chosen_sample = sidebar.choose_sample(laboratory)
    spectra = sidebar.choose_spectra_type()
    exp = get_data(laboratory, spectra, chosen_sample)
    exp_meas = sidebar.show_experiments(exp)
    data = utils.get_data_spectra(exp, exp_meas)

    
    # sidebar separating line
    col_left, col_right = st.columns([5, 2])
    with col_right:
        normalized = False

        plot_settings = st.expander("Plot settings", expanded=True)
        
            # Choose plot colors and templates
        with plot_settings:
            tsvalue = utils.tick_step()
            tscolor, tsfsize = utils.ticks()
            fig_width, fig_height = utils.fig_size()
            plots_color, template = utils.get_chart_vis_properties_vis()
            
        range_expander_name = 'Line profile pixel'
        range_expander = st.expander(range_expander_name, expanded=True)
            
        with range_expander:
            ypix = utils.pline(attrs)
        
        data_properties =  st.expander("Experimental Measurement Properties", expanded=False)
        with data_properties:
            utils.data_properties(attrs)
            
    # Data plotting
    with col_left:
        st.header('Plots')
    



