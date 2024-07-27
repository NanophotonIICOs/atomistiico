import py3Dmol
def write_xyz(atoms):
    """
    Genera una cadena de texto en formato XYZ a partir de una estructura atómica de ASE.

    Parameters:
    atoms (ase.Atoms): Estructura atómica de ASE.

    Returns:
    str: Cadena de texto en formato XYZ.
    """
    xyz_string = f"{len(atoms)}\n\n"
    for atom in atoms:
        xyz_string += f"{atom.symbol} {atom.position[0]} {atom.position[1]} {atom.position[2]}\n"
    return xyz_string


def show_atoms(atoms):
    axyz = write_xyz(atoms)
    xyzview = py3Dmol.view(width=350,height=350)
    model=xyzview.addModel(axyz,'xyz',{'doAssembly':True,
                                    'duplicateAssemblyAtoms':True,
                                    'normalizeAssembly':True})
    xyzview.setStyle({'sphere':{'colorscheme':'Jmol','scale':0.2},
                        'stick':{'colorscheme':'Jmol', 'radius':0.1}})
    # xyzview.addSurface(py3Dmol.VDW,{'opacity':.5,'colorscheme':{'prop':'b','gradient':'sinebow','min':0,'max':10}})
    xyzview.addUnitCell()
    for i, atom in enumerate(atoms):
        xyzview.addLabel(atom.symbol, {'position': {'x': atom.position[0], 'y': atom.position[1], 'z': atom.position[2]}, 'backgroundColor': 'none', 'backgroundOpacity': 0., 'fontColor': 'black', 'fontSize': 17})
    xyzview.zoomTo()
    xyzview.render()
    xyzview.addBox({'center':'{x:0,y:0,z:0}','dimensions': '{w:10,h:10,d:10}','color':'magenta'})
    xyzview.show()
    