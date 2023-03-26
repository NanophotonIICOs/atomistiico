import base64
import plotly.express as px
import plotly.io as pio
import numpy as np
import streamlit as st
import pandas as pd
import peakutils
import glob
from datetime import date
from datetime import datetime
from pathlib import Path
from pathlib import Path
import os
# iconpath1 = Path(__file__).parent / "seda_icons/logo_iico_azul.png"
# iconpath2 = Path(__file__).parent / "seda_icons/puppy_icon.png"
icons_path = os.path.abspath(os.path.dirname(__file__))
iconpathiico = os.path.join(icons_path, "icons/logo_iico_azul.png")
iconpathatiico = os.path.join(icons_path, "icons/atiico_icon.png")


def trim_spectra(df):
    # trim raman shift range
    min_, max_ = int(float(df.index.min())), int(float(df.index.max())) + 1
    min_max = st.slider('Custom range', min_value=min_, max_value=max_, value=[min_, max_])
    min_rs, max_rs = min_max  #.split('__')
    min_rs, max_rs = float(min_rs), float(max_rs)
    mask = (min_rs <= df.index) & (df.index <= max_rs)
    return df[mask]


def show_iico_logo(width, padding, margin):
    with open(iconpathiico,'rb') as f:
        data = f.read()
    link = 'https://www.iico.uaslp.mx/#gsc.tab=0'
    padding_top, padding_right, padding_bottom, padding_left = padding
    margin_top, margin_right, margin_bottom, margin_left = margin
    
    bin_str = base64.b64encode(data).decode()
    html_code = f'''
                <a href="{link}" target = _blank>
                    <img src="data:image/png;base64,{bin_str}"
                    style="
                     margin: auto;
                     width: {width}%;
                     margin-top: {margin_top}px;
                     margin-right: {margin_right}px;
                     margin-bottom: {margin_bottom}px;
                     margin-left: {margin_left}%;
                     padding-top: {margin_top}px;
                     padding-right: {padding_right}px;
                     padding-bottom: {padding_bottom}px;
                     padding-left: {padding_left}%;
                     "/>
                 </a>
                '''
    return html_code


def show_atomistiico_logo(width, padding, margin):
    padding_top, padding_right, padding_bottom, padding_left = padding
    margin_top, margin_right, margin_bottom, margin_left = margin
    
    with open(iconpathatiico,'rb') as f:
        data = f.read()
    link = 'https://github.com/NanophotonIICOs/atomistiico'
    bin_str = base64.b64encode(data).decode()
    html_code = f'''
                <a href="{link}" target = _blank>
                <img src="data:image/png;base64,{bin_str}"
                style="
                     margin: auto;
                     width: {width}%;
                     margin-top: {margin_top}px;
                     margin-right: {margin_right}px;
                     margin-bottom: {margin_bottom}px;
                     margin-left: {margin_left}%;
                     padding-top: {margin_top}px;
                     padding-right: {padding_right}px;
                     padding-bottom: {padding_bottom}px;
                     padding-left: {padding_left}%;
                     "/>
                '''

    return html_code


def choose_template():
    """
    Choose default template from the list
    :return: Str, chosen template
    """
    template = st.selectbox(
        "Chart template",
        list(pio.templates), index=2, key='new')

    return template


def get_chart_vis_properties():
    palettes = {
        'qualitative': ['Alphabet', 'Antique', 'Bold', 'D3', 'Dark2', 'Dark24', 'G10', 'Light24', 'Pastel',
                        'Pastel1', 'Pastel2', 'Plotly', 'Prism', 'Safe', 'Set1', 'Set2', 'Set3', 'T10', 'Vivid',
                        ],
        'diverging': ['Armyrose', 'BrBG', 'Earth', 'Fall', 'Geyser', 'PRGn', 'PiYG', 'Picnic', 'Portland', 'PuOr',
                      'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'Tealrose', 'Temps', 'Tropic', 'balance',
                      'curl', 'delta', 'oxy','Plotly3',
                      ],
        'sequential': ['Aggrnyl', 'Agsunset', 'Blackbody', 'Bluered', 'Blues', 'Blugrn', 'Bluyl', 'Brwnyl', 'BuGn',
                       'BuPu', 'Burg', 'Burgyl', 'Cividis', 'Darkmint', 'Electric', 'Emrld', 'GnBu', 'Greens', 'Greys',
                       'Hot', 'Inferno', 'Jet', 'Magenta', 'Magma', 'Mint', 'OrRd', 'Oranges', 'Oryel', 'Peach',
                       'Pinkyl', 'Plasma', 'Plotly3', 'PuBu', 'PuBuGn', 'PuRd', 'Purp', 'Purples', 'Purpor', 'Rainbow',
                       'RdBu', 'RdPu', 'Redor', 'Reds', 'Sunset', 'Sunsetdark', 'Teal', 'Tealgrn', 'Turbo', 'Viridis',
                       'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'algae', 'amp', 'deep', 'dense', 'gray', 'haline', 'ice',
                       'matter', 'solar', 'speed', 'tempo', 'thermal', 'turbid',
                       ]
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        palette_type = st.selectbox("Type of color palette", list(palettes.keys()), 0)
    with col2:
        palette = st.selectbox("Color palette", palettes[palette_type], index=0)
        if st.checkbox('Reversed', False):
            palette = palette + '_r'
    with col3:
        template = choose_template()

    palette_module = getattr(px.colors, palette_type)
    palette = getattr(palette_module, palette)

    return palette, template


def get_chart_vis_properties_vis():
    palettes = {
        'sequential': ['Plotly3','Aggrnyl', 'Agsunset', 'Blackbody', 'Bluered', 'Blues', 'Blugrn', 'Bluyl', 'Brwnyl', 'BuGn',
                       'BuPu', 'Burg', 'Burgyl', 'Cividis', 'Darkmint', 'Electric', 'Emrld', 'GnBu', 'Greens', 'Greys',
                       'Hot', 'Inferno', 'Jet', 'Magenta', 'Magma', 'Mint', 'OrRd', 'Oranges', 'Oryel', 'Peach',
                       'Pinkyl', 'Plasma', 'Plotly3', 'PuBu', 'PuBuGn', 'PuRd', 'Purp', 'Purples', 'Purpor', 'Rainbow',
                       'RdBu', 'RdPu', 'Redor', 'Reds', 'Sunset', 'Sunsetdark', 'Teal', 'Tealgrn', 'Turbo', 'Viridis',
                       'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'algae', 'amp', 'deep', 'dense', 'gray', 'haline', 'ice',
                       'matter', 'solar', 'speed', 'tempo', 'thermal', 'turbid',
                       ],
        'qualitative': ['Alphabet', 'Antique', 'Bold', 'D3', 'Dark2', 'Dark24', 'G10', 'Light24', 'Pastel',
                        'Pastel1', 'Pastel2', 'Plotly', 'Prism', 'Safe', 'Set1', 'Set2', 'Set3', 'T10', 'Vivid',
                        ],
        'diverging': ['Armyrose', 'BrBG', 'Earth', 'Fall', 'Geyser', 'PRGn', 'PiYG', 'Picnic', 'Portland', 'PuOr',
                      'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'Tealrose', 'Temps', 'Tropic', 'balance',
                      'curl', 'delta', 'oxy',
                      ],
        
    }
    print_widget_labels('Colors')
    palette_type = st.selectbox("Type of color palette", list(palettes.keys()) + ['custom'], 0)
    if palette_type == 'custom':
        palette = st.text_area('Hexadecimal colors', '#DB0457 #520185 #780A34 #49BD02 #B25AE8',
                               help='Type space separated hexadecimal codes')
        palette = palette.split()
    else:
        palette = st.selectbox("Color palette", palettes[palette_type], index=0)
        palette_module = getattr(px.colors, palette_type)
        palette = getattr(palette_module, palette)

    if st.checkbox('Reversed', True):
        palette = palette[::-1]


    print_widgets_separator(1)
    print_widget_labels('Template')
    template = choose_template()
    print_widgets_separator(1)

    return palette, template


# def axis_step(value):
def print_widgets_separator(n=1, sidebar=False):
    """
    Prints customized separation line on sidebar
    """
    html = """<hr style="height:1px;
            border:none;color:#fff;
            background-color:#999;
            margin-top:5px;
            margin-bottom:10px"
            />"""

    for _ in range(n):
        if sidebar:
            st.sidebar.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown(html, unsafe_allow_html=True)


def print_widget_labels(widget_title, margin_top=5, margin_bottom=10):
    """
    Prints Widget label on the sidebar and lets adjust its margins easily
    :param widget_title: Str
    """
    st.markdown(
        f"""<p style="font-weight:500; margin-top:{margin_top}px;margin-bottom:{margin_bottom}px">{widget_title}</p>""",
        unsafe_allow_html=True)

    
def get_structure_properties():
    print_widget_labels('Background')
    background_window = st.checkbox('None')
    
    if not background_window:
        b_window='white'
    else:
        b_window='none'
        
    return b_window


def error_alert():
    st.warning("Error in file",icon="⚠️")
    
    
            
        
        
