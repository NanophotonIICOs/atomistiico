import dash
from dash import html,dcc

# standard Dash imports for callbacks (interactivity)
from dash.dependencies import Input, Output, State
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
    scene_settings={"zoomToFit2D": True},
    id="my_structure")


def get_struct(value,step):
    allatoms =  Trajectory(value)
    try:
        atoms = allatoms[step]
        structure = AseAtomsAdaptor.get_structure(atoms)
        trajslides = len(allatoms)
    except (UnboundLocalError, IndexError):
        pass
    class Results(): pass
    results = Results()
    results.structure = structure
    results.trajslides = trajslides
    return results


deformation_button = html.Button("Deformation Structure", id="change_structure_button",n_clicks=0)

# refresh_button = html.Button("Deformation Structure", id="change_structure_button",n_clicks=0)

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
html.H1([deformation_button]),
html.H1("Structure"),
structure_component.layout(size='700px'),
# html.H3("Options Layout"),
# structure_component.options_layout(),
# html.H1(id='lenstructure')
# dcc.Slider(id='my-slider'),
]
)



@app.callback(Output('file-select','options'),
               Input('folder-container','value'))
def display_dropdowns(value):
    return [i for i in data().get_list_samples(value)]


@app.callback(Output(structure_component.id(),"data"),
              Input("file-select","value"),
              Input("change_structure_button", "n_clicks"),
               prevent_initial_call=True
              )
def update_structure(value,n_clicks):
    
    # atoms = Trajectory(value)[0:2]
    # structure = AseAtomsAdaptor.get_structure(atoms)
    # structure_component = ctc.StructureMoleculeComponent(structure,id="my_structure")
    # return  structure
    return get_struct(value,int(n_clicks)).structure

# @app.callback(
#     output=[Output(structure_component.id(),"data")],
#     inputs=dict(
#                (Input("file-select","value"), Input("change_structure_button", "n_clicks")),       
#               ))
# def update_structure(value,n_clicks):
    
#     # atoms = Trajectory(value)[0:2]
#     # structure = AseAtomsAdaptor.get_structure(atoms)
#     # structure_component = ctc.StructureMoleculeComponent(structure,id="my_structure")
#     # return  structure
#     return get_struct(value,n_clicks).structure


ctc.register_crystal_toolkit(app=app, layout=my_layout)
if __name__ == "__main__":
    app.run_server(host='localhost', port=3333, debug=True)