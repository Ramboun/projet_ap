from heuristic import *
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot

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

class RepetitionOrder():
    def __init__(self,order,jobs,nb_machines):
        self.nb_machines = nb_machines
        self.order = copy.copy(order)
        self.duration = None
        self.jobs = copy.deepcopy(jobs)
        if(self.jobs[0].__class__ == JobForHeuristic):
            for j in self.jobs:
                j.__class__ = Job
                j.cast_task()
        self.jobs_end_time = [0] * len(self.jobs)
        self.ressources_end_time = [0] * nb_machines
        self.temp_var_1 = None
        self.temp_var_2 = None
        self.compute()
        
        
    def compute(self):
        job_task_index = [0] * len(self.jobs)
        for i in self.order:
            end_time, ressource_used = self.jobs[i].start(self.ressources_end_time,self.jobs_end_time
                                                            ,job_task_index[i])
            job_task_index[i] += 1
            self.update_end_times(ressource_used,i,end_time)
        self.duration = max(self.jobs_end_time)
   
    def display_gantt(self):
        colors = {}
        list_colors = ['dodgerblue','seagreen','sienna','turquoise','orchid','gold','black','white','red'
                       ,'blue','green','yellow','purple']
        fig = go.Figure(
            layout = {
                'barmode': 'stack',
                'xaxis': {'automargin': True},
                'yaxis': {'automargin': True}}
        )
        for j in self.jobs:
            for t in j.tasks:
                show_legend = False
                if(str(t.ressource) not in colors.keys()):
                    color_picked = list_colors[0]
                    list_colors.remove(color_picked)
                    colors[str(t.ressource)] =  color_picked
                    show_legend = True

                fig.add_bar(x=[t.duration],
                    y=['Job ' + str(j.num)],
                    base=t.start_time,
                    orientation='h',
                    showlegend=show_legend,
                    name=str(t.ressource),
                    marker={'color': colors[str(t.ressource)]}) 
        fig.update_layout(
            title="Gantt chart",
            xaxis_title="Time",
            yaxis_title="Jobs"
        )
        fig.update_xaxes(showgrid=True, gridwidth=1)
        fig.show()
        
    def get_score(self):
        return 1/self.duration

    def update_end_times(self,ressource_used,job_num,end_time):
        self.ressources_end_time[ressource_used] = end_time
        self.jobs_end_time[job_num] = end_time
            
    def get_swapped(self,ind1,ind2):
        res = self.order.copy()
        c = res[ind1]
        res[ind1] = res[ind2]
        res[ind2] = c
        return res
        
    def get_2swap_voisinage(self):
        voisins = []
        for i in range(len(self.order)):
            for j in range(i,len(self.order)):
                if(self.order[i] != self.order[j]):
                    voisins.append(RepetitionOrder(self.get_swapped(i,j),self.jobs,self.nb_machines))
                    
        for i in range(len(self.order)):
            for j in range(len(self.order)):
                order = copy.copy(self.order)
                poped = order[i]
                order = np.delete(order,i)
                order = np.insert(order,j,poped)
                voisins.append(RepetitionOrder(order,self.jobs,self.nb_machines))
        return voisins
