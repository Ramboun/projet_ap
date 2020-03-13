import re
import copy
import sys
from enum import Enum
import json
import matplotlib.pyplot as plt
import time
import numpy as np
import random
import plotly.figure_factory as ff
import statistics

class Task:  
    # Classe définissant une tâche
    
    def __init__(self,ressource,duration,job_num):
        self.ressource = ressource
        self.job_num = job_num
        self.duration = duration
        self.start_time = None
        self.possible_start_time = 0
        
    def reset(self):
        # Remise à zéro des variables de la tâche
        self.start_time = None
        self.possible_start_time = 0
        
    def to_string(self):
        return str(self.ressource) + " " + str(self.duration)
        
    def start(self):
        # Démarre une tâche au plus tôt
        self.start_time = self.possible_start_time
                
    def update_possible_start_time(self,time):
        # Met à jour la date de démarrage possible
        if(self.possible_start_time < time):
            self.possible_start_time = time