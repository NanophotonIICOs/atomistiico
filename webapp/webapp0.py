import json
import logging
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image
from ase.io.trajectory import Trajectory
from ase.visualize import view
from opendata import data
from glob import glob
def main(df):
    st.title('Atomistic Analysis')
    st.subheader("Raul's research group")
    st.markdown(
    """
    <br><br/>
    Atomistic analysis from purposed structures to study magnetic properties. 
    """
    , unsafe_allow_html=True)


def strcutures():
    st.sidebar.markdown('# Choose Your structure')
    folders = st.sidebar.selectbox("Structure:",data().folders)
    trajs = st.sidebar.selectbox("Traj file: ",data().get_list_samples(folders))


if __name__ == '__main__':

    logging.basicConfig(level=logging.CRITICAL)

    df = strcutures()

    main(df)