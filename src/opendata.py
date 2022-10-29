import matplotlib
import numpy as np 
from matplotlib import pyplot as plt
from glob import glob
import os

path = "/media/rbnfiles/dft/pts2/"

class data:
    def __init__(self):
        self.path  = "/media/rbnfiles/dft/pts2/"
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
                for filesinto in glob(folderi+'/*.traj'):
                    #self.folder_samples.append(filesinto.split(self.path)[-1].split('/')[-1])
                    self.folder_samples.append(filesinto)
        return self.folder_samples


    def return_data(self,file):
        for files in self.complete_files:
            if file in files:
                self.select_file = file
                break
        return self.select_file
        

            
