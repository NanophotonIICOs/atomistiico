from setuptools import setup, find_packages

setup(
    name='atomistiico',
    version='1.0',
    description='Repository to analyzing atomistic simulations from DFTs and many-body quantum models',
    author=[
            ('O. Ruiz-Cigarrillo', 'ruizoscar.1393@gmail.com'),
            ('A.M Martinez-Martinez', '')
    ],
    url='https://github.com/NanophotonIICOs/atomistic-analysis',
    packages=find_packages('atomistiico'),
    package_dir={'': 'atomistiico'},
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'tqdm',
        'numba',
        'scipy',
        'Ipython',
        'tabulate',
        'pandas',
        'h5py',
        'ipykernel',
        'astropy',
        'lumispy',
        'specutils',
        'peakutils',
        'ase',
        'gpaw',
        'py3dmol',
        'py4dstem',
        'ipympl',
        'abtem',
        'plotly==5.13.1',
        'streamlit',
        'dash'
    ],
)
