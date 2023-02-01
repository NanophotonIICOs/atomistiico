import os 


def make_dir(folder):
    if os.path.exists(folder):
        #print(f"{folder} dir already exist!")
        pass
    else:
        print(f"{folder} dir it's created!")
        os.mkdir(folder)