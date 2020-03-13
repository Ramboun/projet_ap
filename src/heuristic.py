import re
import copy
import sys
from enum import Enum
import json
import matplotlib.pyplot as plt
import time
import numpy as np
import random
import statistics
from classes.Task import Task
from classes.Job import Job
from classes.State import STATE


def SPT(possible_tasks):
    # Prendre la tâche qui fini le plus tôt
    smallest_duration = sys.maxsize 
    best_task = None
    for t in possible_tasks:
        if t.duration < smallest_duration:
            smallest_duration = t.duration
            best_task = t
    return best_task

def LPT(possible_tasks):
    # Prendre la tâche qui fini le plus tard
    smallest_duration = 0
    best_task = None
    for t in possible_tasks:
        if t.duration > smallest_duration:
            smallest_duration = t.duration
            best_task = t
    return best_task

class TaskForHeuristic(Task):
    # Classe définissant un tâche pour l'heuristique
    
    def __init__(self,ressource,duration,job_num):
        super().__init__(ressource,duration,job_num)
        self.state = STATE.NOT_DONE
        
    def start(self,time):
        # Démarrage de la tâche
        self.start_time = time
        self.state = STATE.ON_GOING
        
    def update(self,time):
        # Mise à jour de la tâche lorsque le temps avance
        if(self.state == STATE.ON_GOING):
            if time >= self.start_time + self.duration:
                self.state = STATE.DONE
                return self.ressource
        return -1
                
    def is_done(self):
        # Renvoie true si la tâche est terminée
        return self.state == STATE.DONE
    
    def casted_task(self):
        # Cast la tâche heuristique en tâche
        return Task(self.ressource,self.duration, self.job_num)
        

class JobForHeuristic(Job):
    # Classe définissant un job pour l'heuristique
    def __init__(self,job_num):
        super().__init__(job_num)
        
    def get_next_task(self):
        # Renvoie la prochaine tâche à exécuté si aucune tâche n'est déjà en cours
        on_going = [task for task in self.tasks if task.state == STATE.ON_GOING]
        if  len(on_going) == 0:
            not_done_tasks = [task for task in self.tasks if task.state == STATE.NOT_DONE]
            if(len(not_done_tasks) != 0):
                return not_done_tasks[0]
        return None
            
    def update(self,time):
        # Met à jour toutes les tâches et renvoie les ressources qui ont été libérées
        res_to_free = []
        for t in self.tasks:
            res_to_free.append(t.update(time))
        return res_to_free
            
    def start(self,time):
        # Démarre la prochaine tâche
        t = next(task for task in self.tasks if task.state == STATE.NOT_DONE)
        if t != None:
            t.start(time)
            return t.ressource
        
    def is_done(self):
        # Renvoie true si le job est terminé
        return self.tasks[-1].is_done()

     
class InstanceHeuristic:
    # Classe d'une instance d'heuristique
    
    def __init__(self,instance_name,instance_path,info_path):
        
        # Récupération des différences paths
        self.instance_name = instance_name
        self.instances_path = instance_path
        self.instance_path = self.instances_path + instance_name  
        # Récupération des 
        with open(info_path, 'r') as f:
            instances_info = json.load(f)
            for i in instances_info:
                if i['name']==self.instance_name:
                    self.instance_info = i

        list_jobs = []
        n_machines = 0
        n_jobs = 0
        # Lecture de l'instance
        with open(self.instance_path,'r') as f:
            num_line = 0
            for line in f:
                if(line[0] != '#'):

                    re_line = re.sub(' +',';',line)
                    re_line = re.sub('\\n','',re_line)
                    split_line = re_line.split(';')
                    if (num_line == 0):
                        n_machines = int(split_line[1])
                        n_jobs = int(split_line[0])
                    else:
                        list_jobs.append(split_line)
                    num_line = num_line+1
        jobs = []
        for i in range(n_jobs):
            job = JobForHeuristic(i)
            for j in range(0,len(list_jobs[i]),2):
                job.add_task(TaskForHeuristic(int(list_jobs[i][j]),int(list_jobs[i][j+1]),i))
            jobs.append(job)
            
        self.n_machines = n_machines
        self.jobs=copy.deepcopy(jobs)
        self.machines_availability = [True]*n_machines
        self.time = 0
        self.order = np.array([]).astype(int)

    def get_max_tasks(self):
        nb_max=0
        for j in self.jobs:
            if(j.nb_task>nb_max):
                nb_max = j.nb_task
        return nb_max
    
    def check_possible_tasks(self):
        possible_tasks = []
        for j in self.jobs:
            next_task = j.get_next_task()
            if(next_task != None):
                if(self.machines_availability[next_task.ressource]):
                    possible_tasks = possible_tasks + [next_task]
        return possible_tasks
    
    def display_jobs(self):
        max_tasks_per_job = 0
        for j in self.jobs:
            if(max_tasks_per_job < len(j.tasks)):
                max_tasks_per_job = len(j.tasks)
        header=" "
        for t in range(max_tasks_per_job):
            header = header + " " + '{:^6}'.format("R D") + "  " 
        print(header)
        for j in self.jobs:
            print(j.to_string())
            
    def get_state_matrix(self):
        m = np.zeros((len(self.jobs),self.get_max_tasks()))
        for j_num,j in enumerate(self.jobs):
            for i,t in enumerate(j.tasks):
                if(t.state == STATE.ON_GOING):     
                    m[j_num][i] = 0             
                elif(t.state == STATE.DONE):
                    m[j_num][i] = 1           
                else:
                    m[j_num][i] = -1 
        return m
    
    def time_forward(self):
        self.time = self.time + 1
        for j in self.jobs:
            res_to_free = j.update(self.time)
            
            for r in res_to_free:
                if(r != -1):
                    self.machines_availability[r] = True
        
            
    def start_job(self,job_num):
        res_used = self.jobs[job_num].start(self.time)
        self.machines_availability[res_used] = False
        
    def is_done(self):
        done = True
        for j in self.jobs:
            done = done and j.is_done()
        return done
    
    def start_heuristic(self,fct=SPT,rand=0,display=False):
        if(display):
            matrix_state = self.get_state_matrix()
            fig, ax = plt.subplots()
            grid_x=[i+0.5 for i in range(matrix_state.shape[1])]
            ax.set_xticks(grid_x,minor=True)
            grid_y=[i+0.5 for i in range(matrix_state.shape[0])]
            ax.set_yticks(grid_y,minor=True)
            ax.grid(which='minor')
            ax.matshow(matrix_state, cmap='RdYlGn', vmin=-1, vmax=1)
            for i,jb in enumerate(self.jobs):
                for j,t in enumerate(jb.tasks):
                    text = ax.text(j, i, t.ressource,ha="center", va="center", color='black', fontsize=16)
            plt.xlabel('Tasks')
            plt.ylabel('Jobs')
            
        while not self.is_done():
            possible_tasks = self.check_possible_tasks()
            if(len(possible_tasks) > 0):
                if(random.random()<rand):
                    highest_prio_task = random.choice(possible_tasks)
                else:
                    highest_prio_task = fct(possible_tasks)
                self.start_job(highest_prio_task.job_num)
                self.order = np.append(self.order,highest_prio_task.job_num)
            else:
                self.time_forward()
                
                if(display):
                    matrix_state = self.get_state_matrix()
                    ax.matshow(matrix_state, cmap='RdYlGn', vmin=-1, vmax=1)
                    ax.set_title("TIME : "+str(self.time))
                    plt.pause(0.01)
  
