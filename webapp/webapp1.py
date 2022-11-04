import dash
from dash import html,dcc

# standard Dash imports for callbacks (interactivity)
from dash.dependencies import Input, Output
from pymatgen.core.lattice import Lattice
from pymatgen.core.structure import Structure
from pymatgen.io.ase import AseAtomsAdaptor
import crystal_toolkit.components as ctc
from crystal_toolkit.settings import SETTINGS
from ase.io.trajectory import Trajectory
from ase.visualize import view
from opendata import data
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO


app = dash.Dash(prevent_initial_callbacks=True)
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


# structure_component = ctc.StructureMoleculeComponent(
#     show_compass=True,
#     bonded_sites_outside_unit_cell=True,
#     scene_settings={"zoomToFit2D": True}, id="my_structure"
# )
structure_component = ctc.StructureMoleculeComponent( show_compass=False,
    bonded_sites_outside_unit_cell=True,
    scene_settings={"zoomToFit2D": False},id="my_structure")


# def get_struct(value):
#     if value:
#         structure_name = value
#         print(value)
#     else:
#         structure_name = '/media/rbnfiles/dft/pts2/teststruct/path_opt_PtSe2.traj'
#     traj = Trajectory(structure_name)[-1]
#     atoms = pyase.Atoms(traj)
#     structure = AseAtomsAdaptor.get_structure(atoms)
#     structure_component = ctc.StructureMoleculeComponent(structure)
#     return  structure_component


my_layout = html.Div(
[
html.H1(
        children="R. Balderas-Navarro research group", 
        style={'backgroundColor': colors['background'],'textAlign': 'center','color': colors['text'],'font-size': '30px',}
        ),
html.Div([
            dcc.Dropdown(id='folder-container',
                    options=[{'label':folder, 'value':folder } for folder in data().complete_folders
                        ]),
         ],style={'width': '50%','display':'inline-block',}
        ),
html.Div(
            [dcc.Dropdown(id='file-select')],
            style={'width': '50%','display':'inline-block',}
        ),
html.H1("Structure"),
structure_component.layout(),
# dcc.Slider(id='my-slider'),
]
)



@app.callback(Output('file-select','options'),
               Input('folder-container','value'))
def display_dropdowns(value):
    return [i for i in data().get_list_samples(value)]


@app.callback(Output(structure_component.id(),"data"),
              Input("file-select","value"))
def update_structure(value):
    atoms = Trajectory(value)[0:2]
    structure = AseAtomsAdaptor.get_structure(atoms)
    structure_component = ctc.StructureMoleculeComponent(structure,id="my_structure")
    return  structure


ctc.register_crystal_toolkit(app=app, layout=my_layout)
if __name__ == "__main__":
    app.run_server(host='localhost', port=3333, debug=True)