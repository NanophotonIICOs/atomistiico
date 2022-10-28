import dash
from dash import html
from pymatgen.core.lattice import Lattice
from pymatgen.core.structure import Structure
import crystal_toolkit.components as ctc
from crystal_toolkit.settings import SETTINGS
import dash_bootstrap_components as dbc
from opendata import data
from dash import Dash, dcc, html, Input, Output
from ase.io.trajectory import Trajectory
from pymatgen.core import Molecule
import pymatgen.io.ase as pyase 
from pymatgen.io.ase import AseAtomsAdaptor

app = dash.Dash(assets_folder=SETTINGS.ASSETS_PATH)
server = app.server

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


folders = data().complete_folders
allfiles = data().complete_files
file = data().return_data(allfiles[0])
traj = Trajectory(file)[-1]
atoms = pyase.Atoms(traj)

structure = AseAtomsAdaptor.get_structure(atoms)
# create our crystal structure using pymatgen

# create the Crystal Toolkit component
structure_component = ctc.StructureMoleculeComponent(structure, id="structure")

# add the component's layout to our app's layout
my_layout = html.Div(
    [
html.H1(children="Dr Raul's research group", style={'backgroundColor': colors['background'],'textAlign': 'center','color': colors['text'],'font-size': '30px',}),
html.Div(children='Select Folder', style={
        'font-style': 'italic',
        'font-weight': 'bold','width': '50%','display':'inline-block',
    }),
html.Div([
dcc.Dropdown(
                data().folders,
                'Select Structure',
                id='select-folder'
            ),
    ],style={'width': '50%','display':'inline-block',}
 ),
 html.Div(id='dropdown-container-output'),

 html.H1([structure_component.layout()],style={'width': '50%','display':'inline-block','align':'right'}),],
)


# # as explained in "preamble" section in documentation
ctc.register_crystal_toolkit(app,layout=my_layout)

@app.callback(
    Output('select-folder', 'value'),
    Input('select-file', 'value'),)
def display_output(values):
    return html.Div([
        html.Div('Dropdown {} = {}'.format(i + 1, value))
        for (i, value) in enumerate(data().get_list_samples(values))
    ])

if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=1115, debug=True)