import py3Dmol
import numpy as np
from atomistiico.utils.rjson import pjson
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
    def __init__(self,path) -> py3Dmol:
        self.data = pjson(path)
        self.structure = self.data['xyz']
        self.atoms = None
    
    def show_structure(self,widt=500,height=500):
        self.atoms = py3Dmol.view(width=widt,height=height)
        self.atoms.addModel(self.structure,'xyz',{'doAssembly':True,
                                 'duplicateAssemblyAtoms':True,
                                 'normalizeAssembly':True})
        self.atoms.setStyle({'sphere':{'colorscheme':'Jmol','scale':0.3},
                    'stick':{'colorscheme':'Jmol', 'radius':0.15}})
        self.atoms.addUnitCell()
        
        self.ase_atoms = atoms_from_xyz_string(self.structure)
        for i, atom in enumerate(self.ase_atoms):
            self.atoms.addLabel(atom.symbol, {'position': {'x': atom.position[0], 'y': atom.position[1], 'z': atom.position[2]}, 'backgroundColor': 'none', 'backgroundOpacity': 0., 'fontColor': 'black', 'fontSize': 17})
        
        self.atoms.zoomTo()
        self.atoms.render()
        return self.atoms.show()