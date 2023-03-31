import py3Dmol
import numpy as np
from atomistiico.utils.out_json import out_json

import io
import ase.io



def atoms_from_xyz_string(xyz_string):
    """
    Parameters:
    xyz_string (str): Cadena de texto en formato XYZ.

    Returns:
    ase.Atoms: Objeto Atoms de ASE.
    """
    with io.StringIO(xyz_string) as f:
        atoms = ase.io.read(f, format='xyz')
    return atoms

class Show:
    def __init__(self,path):
        self.data = out_json(path)
        self.structure = self.data.get_xyz
    
    def show_structure(self,background):
        self.viewer = py3Dmol.view(width=500)
        self.viewer.addModel(self.structure,'xyz',{'doAssembly':True,
                                 'duplicateAssemblyAtoms':True,
                                 'normalizeAssembly':True})
        self.viewer.setStyle({'sphere':{'colorscheme':'Jmol','scale':0.3},
                    'stick':{'colorscheme':'Jmol', 'radius':0.15}})
        
        self.ase_atoms = atoms_from_xyz_string(self.structure)
        for i, atom in enumerate(self.ase_atoms):
            self.viewer.addLabel(atom.symbol, {'position': {'x': atom.position[0], 'y': atom.position[1], 'z': atom.position[2]}, 'backgroundColor': 'none', 'backgroundOpacity': 0., 'fontColor': 'black', 'fontSize': 17})
        self.viewer.setBackgroundColor(background)
        self.viewer.zoomTo()
        self.viewer.render()
        return self.viewer