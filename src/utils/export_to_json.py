import json
import os 
from utils import create_dir


def outjson(results,filename,dir="json"): 
    create_dir(dir)
    if ".gpw" in filename:
        filename = f"{dir}/{filename.split('.gpw')[0]}.json"
    else:
        filename = f"{dir}/{filename}.json"
        
    json_data = json.dumps(results)
    with open(filename, "w") as f:
         f.write(json_data)
    f.close()
    print(f"{filename} was created!")
    