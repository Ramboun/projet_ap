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

from classes.RepetitionOrder import *

def correct_order(order,jobs):
    jobs_sizes = [len(j.tasks) for j in jobs]
    jobs_tasks_counter = [0] * len(jobs_sizes)
    indexes_to_delete = []
    for i,e in enumerate(order):
        if(jobs_tasks_counter[e] == jobs_sizes[e]):
            indexes_to_delete.append(i)
        else:
            jobs_tasks_counter[e] += 1
            
    order = np.delete(order,indexes_to_delete)
    
    for i in range(len(jobs_sizes)):
        while jobs_tasks_counter[i] < jobs_sizes[i]:
            order = np.append(order,i)
            jobs_tasks_counter[i] += 1
    return order


def order_fusion(order_1,order_2,jobs):
    size_of_order = len(order_1)
    new_order = np.concatenate((order_1[0:size_of_order//2],order_2[size_of_order//2:-1]),axis=0)
    new_order = correct_order(new_order,jobs)
    return new_order
    
def mutate(order):
    mutation_done = False
    while not mutation_done:
        swap_1 = random.randint(0,len(order)-1)
        swap_2 = random.randint(0,len(order)-1)
        if(order[swap_1] != order[swap_2]):
            temp_var = order[swap_1]
            order[swap_1] = order[swap_2]
            order[swap_2] = temp_var
            mutation_done = True
    return order

def get_mutated_orders(order_list,mutation_chance):
    for o in order_list:
        if(random.random() < mutation_chance):
            o = mutate(o)
    return order_list

def order_list_to_population(order_list,jobs,nb_machines):
    population = []
    for o in order_list:
        population.append(RepetitionOrder(o,jobs,nb_machines))
    return population

def get_best_subpopulation(population,size):
    population_copie = copy.copy(population)
    new_population = []
    while len(new_population) != size:
        best_of_pop = get_best_voisin(population_copie)
        population_copie.remove(best_of_pop)
        new_population.append(best_of_pop)
    return new_population

def get_best_voisin(population):
    if(len(population)>=1):
        best_voisin = population[0]
        best_perf = population[0].duration
        for v in population:
            if(v.duration <= best_perf):
                best_voisin = v
                best_perf = v.duration
        return best_voisin
    else: 
        return None
    
def get_mean_duration(population):
    mean_duration = 0
    for p in population:
        mean_duration += p.duration
    return mean_duration/len(population)

def get_min_duration(population):
    min_duration = 100000000000
    for p in population:
        if(p.duration < min_duration):
            min_duration = p.duration
    return min_duration

def get_max_duration(population):
    max_duration = 0
    for p in population:
        if(p.duration > max_duration):
            max_duration = p.duration
    return max_duration