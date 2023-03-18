import streamlit as st
from utils import utils
from PIL import Image


def main_page():
    atiico_logo = utils.show_atomistiico_logo(width=40, padding=[0, 0, 0, 0], margin=[0, 0, 0, 30])
    st.markdown(atiico_logo, unsafe_allow_html=True)
    
    cols = st.columns((1, 10, 1))
    with cols[1]:
        st.header("AtomistIICO")
        st.subheader("Analyzing atomistic simulations from DFTs and many-body quantum models")

    cols = st.columns((3, 3, 1))
    with cols[1]:
        st.subheader("By")
    
    iico_logo = utils.show_iico_logo(width=50, padding=[0, 0, 0, 0], margin=[0, 0, 0, 30])
    st.markdown(iico_logo, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("")
    st.markdown("")
