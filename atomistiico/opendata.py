import matplotlib
import numpy as np 
from matplotlib import pyplot as plt
from glob import glob
import os
import pandas as pd

class data:
    def __init__(self,path):
        self.path  = path
        self.folders = []
        self.files = []
        self.complete_folders= []
        self.complete_files = []
        for folder in glob(self.path+"*"):
            self.folders.append(folder.split('/')[-1])
            self.complete_folders.append(folder)
        for folder in  self.complete_folders:
            for filesinto in glob(folder+'/*.traj'):
                self.complete_files.append(filesinto)

    def get_list_samples(self,folder):
        npath = self.path+'/'+folder
        self.folder_samples=[]
        for folderi in self.complete_folders:
            if folder in folderi:
                for (path,dir,files) in os.walk(folder):
                    for filesinto in glob(path+'/*.traj'):
                    #self.folder_samples.append(filesinto.split(self.path)[-1].split('/')[-1])
                        self.folder_samples.append(filesinto)

        return self.folder_samples
    
    def get_fdata(self):
        folders = []
        for i in os.listdir(self.path):
            if not '.' in i:
                 cpath = f"{self.path}/{i}"
                 folders.append(cpath)
        fdf = pd.DataFrame(folders,columns=["Directory"])
        return folders
        
        


    def return_data(self,file):
        for files in self.complete_files:
            if file in files:
                self.select_file = file
                break
        return self.select_file
        

            
