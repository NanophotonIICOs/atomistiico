import streamlit as st
from utils import utils
# from constants import LABELS
import os
from PIL import Image

icons_path = os.path.abspath(os.path.dirname(__file__))
iconpath = os.path.join(icons_path, "icons/atiico_icon.png")

imicon = Image.open(iconpath)

def sidebar_head():
    """
    Sets Page title, page icon, layout, initial_sidebar_state
    Sets position of radiobuttons (in a row or one beneath another)
    Shows logo in the sidebar
    """
    st.set_page_config(
        page_title="AtomistIICO",
        page_icon=imicon,
        layout="wide",
        initial_sidebar_state="auto"
    )
    st.set_option('deprecation.showfileUploaderEncoding', False)
    #puppy logo
    html_code = utils.show_atomistiico_logo(100, [0, 0, 0, 0], margin=[0, 0, 0, 0])
    st.sidebar.markdown(html_code, unsafe_allow_html=True)
    st.sidebar.markdown('')
    st.sidebar.markdown('')


def print_widget_labels(widget_title, margin_top=5, margin_bottom=10):
    """
    Prints Widget label on the sidebar and lets adjust its margins easily
    :param widget_title: Str
    """
    st.sidebar.markdown(
        f"""<p style="font-weight:500; margin-top:{margin_top}px;margin-bottom:{margin_bottom}px">{widget_title}</p>""",
        unsafe_allow_html=True)


def choose_sample(laboratory):
    samples = utils.samples(laboratory)
    s_samples = st.sidebar.selectbox(
        "Sample",
        samples,
        index=3
        )
    return s_samples



