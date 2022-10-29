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
from jupyter_dash import JupyterDash


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


structure_component = ctc.StructureMoleculeComponent(
    show_compass=False,
    bonded_sites_outside_unit_cell=True,
    scene_settings={"zoomToFit2D": True},
)


my_layout = html.Div(
    [
#html.H1(children="Dr Raul's research group", style={'backgroundColor': colors['background'],'textAlign': 'center','color': colors['text'],'font-size': '30px',}),
# html.Div(children='Select Folder', style={
#         'font-style': 'italic',
#         'font-weight': 'bold','width': '50%','display':'inline-block',
#     }),
html.Div([
  dcc.Dropdown(id='folder-container',
                options=[{'label':folder, 'value':folder } for folder in data().complete_folders
]),
    ],style={'width': '50%','display':'inline-block',}
 ),
html.Div([dcc.Dropdown(id='file-select')],style={'width': '50%','display':'inline-block',}),
structure_component.layout()],
)


# # as explained in "preamble" section in documentation

@app.callback(Output('file-select','options'),
               Input('folder-container','value'))
def display_dropdowns(value):
    return [i for i in data().get_list_samples(value)]
@app.callback(Output('struct','imageRequest'),
              Input('file-select','value'))
def return_structure(value):
    if value:
        structure_name = value
        traj = Trajectory(structure_name)[-1]
        atoms = pyase.Atoms(traj)
        structure = AseAtomsAdaptor.get_structure(atoms)
        structure_component = ctc.StructureMoleculeComponent(structure, id="struct")
    else: 
         default_structure=Structure(Lattice.cubic(5), ["K", "Cl"], [[0, 0, 0], [0.5, 0.5, 0.5]]),
         structure_component = ctc.StructureMoleculeComponent(default_structure, id="struct")

    return structure_component.layout()


ctc.register_crystal_toolkit(app,layout=my_layout)


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=1115, debug=True)