import json
import os 
from utils import create_dir
from typing import Any, Dict


def calc2json(results:Dict[str, Any],filename,dir="json"): 
    create_dir(dir)
    if ".gpw" in filename:
        filename = f"{dir}/{filename.split('.gpw')[0]}.json"
    else:
        filename = f"{dir}/{filename}.json"
        
    json_data = json.dumps(results)
    with open(filename, "w") as f:
         f.write(json_data)
    print(f"{filename} was created!")
    
    
