import sys

if sys.version_info[0] == 2:
    raise ImportError('ASE requires Python3. This is Python2.')



# from atomistiico.aiico_gpaw import Bands
from atomistiico.aiico_qe import Qe