from setuptools import setup, find_packages

setup(
    name='atomistiico',
    version='0.2',
    description='Repository to analyzing atomistic simulations from DFTs and many-body quantum models',
    author='O. Ruiz-Cigarrillo',
    author_email='ruizoscar.1393@gmail.com',
    url='https://github.com/NanophotonIICOs/atomistiico',
    packages=find_packages(),
    #package_dir={'': '.'},
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'scipy',
        'pylibxc2',
        'pytest',
        'spglib',
        'ase',
        'gpaw',
        'numba',
        'Ipython',
        'tabulate',
        'pandas',
        'h5py',
        'ipykernel',
        'specutils',
        'peakutils',
        'py3dmol',
        'ipympl',
    ],
)


