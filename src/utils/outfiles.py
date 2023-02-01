import json
import os 
from utils import make_dir
from typing import Any, Dict

def calc2json(results:Dict[str, Any],filename,dirsave="json"): 
    make_dir(dirsave)
    if ".gpw" in filename:
        filename = f"{dirsave}/{filename.split('.gpw')[0]}.json"
    else:
        filename = f"{dirsave}/{filename}.json"
        
    json_data = json.dumps(results)
    with open(filename, "w") as f:
         f.write(json_data)
        
    
