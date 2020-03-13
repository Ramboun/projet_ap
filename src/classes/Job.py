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

class Job:
    # Objet définissant un job
    
    def __init__(self,job_num):
        self.tasks = []
        self.num = job_num
        self.nb_task = 0
        
    def add_task(self,task):
        # Rajoute une tâche au job
        self.tasks.append(task)
        self.nb_task += 1
        
    def cast_task(self):
        # Transforme les tâche d'heuristique en tâche
        for t in self.tasks:
            t = t.casted_task()
        
    def reset(self):
        # Remet à zero l'état du job
        for t in self.tasks:
            t.reset()
        
    def init_possible_start(self):
        # Initialise les temps possible de démarrage des tâches
        delay = 0
        for t in self.tasks:
            t.possible_start= delay
            delay = delay + t.duration
        
    def to_string(self):
        res = "|"
        for t in self.tasks:
            res = res + " " + '{:^6}'.format(t.to_string()) + " |" 
        return res
    
    def start(self, ressources_availability_array, jobs_availability_array, task_ind):
        # Démarre la tâche task_ind au plus tôt possible
        t = self.tasks[task_ind]
        # Démarrage dès que le job ET la ressource sont disponibles
        min_start_time = max(ressources_availability_array[t.ressource],jobs_availability_array[self.num])
        t.start_time = min_start_time
        return t.duration+t.start_time , t.ressource
    
    def update_possible_time_by_ressource(self,ressource,time):
        # Mets à jour les temps possibles de démarrage en fonction de la ressource utilisé et la date de fin
        for t in self.tasks:
            if(t.ressource == ressource):
                t.update_possible_start_time(time)
    
    def get_end_time(self):
        # Renvoie la date de fin du job
        return self.tasks[-1].start_time + self.tasks[-1].duration