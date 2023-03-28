from setuptools import setup, find_packages

setup(
    name='atomistiico',
    version='0.1',
    description='Repository to analyzing atomistic simulations from DFTs and many-body quantum models',
    author='O. Ruiz-Cigarrillo, A.M. Martinez-Martinez',
    author_email='ruizoscar.1393@gmail.com, a276775@alumnos.uaslp.mx',
    url='https://github.com/NanophotonIICOs/atomistiico',
    packages=find_packages(''),
    package_dir={'': '.'},
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'tqdm',
        'numba',
        'scipy',
        'pylibxc2',
        'Flask',
        'pytest',
        'spglib',
        'ase',
        'gpaw',
        'Ipython',
        'tabulate',
        'pandas',
        'h5py',
        'ipykernel',
        'specutils',
        'peakutils',
        'py3dmol',
        'ipympl',
        'plotly==5.13.1',
        'streamlit',
        'pyiron',
        'pymongo'
    ],
)


