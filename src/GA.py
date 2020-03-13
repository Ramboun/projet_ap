from heuristic import *
from classes.RepetitionOrder import *
from utils import *

import argparse
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

def get_best_fighters(rep_order_1,rep_order_2,comeback_chance=0,best_duration=None):
    if best_duration:
        if(rep_order_1.duration < best_duration):
            return rep_order_1
        if(rep_order_2.duration < best_duration):
            return rep_order_2
    if(rep_order_1.duration < rep_order_2.duration and random.random() > comeback_chance):
        return rep_order_1
    else:
        return rep_order_2

def get_crossover(base_population):
    population = copy.copy(base_population)
    pair_list = []
    new_list_of_order = []
    while len(population)>=2:
        element_1 = population.pop(random.randint(0,len(population)-1))
        element_2 = population.pop(random.randint(0,len(population)-1))
        pair_list.append([element_1,element_2])
        pair_list.append([element_2,element_1])
    for pair in pair_list:
        new_list_of_order.append(order_fusion(pair[0].order,pair[1].order,pair[0].jobs))
    return new_list_of_order

def FFA(population, size,comeback_chance,best_duration=None):
    new_population = []
    while len(new_population) != size:
        winner = get_best_fighters(random.choice(population),random.choice(population),comeback_chance,best_duration=best_duration)
        new_population.append(winner)
    return new_population
                             
def my_own_GA(population,size=None,mutation_chance=0.2,comeback_chance=0,best_duration=None):
    if not size :
        size=len(population)
    new_population = FFA(population,size=size,comeback_chance=comeback_chance,best_duration=best_duration) 
    children = get_crossover(new_population)
    children = get_mutated_orders(children,mutation_chance=mutation_chance)
    children = order_list_to_population(children,population[0].jobs,population[0].nb_machines)
    return children

def get_args(argv):
    parser = argparse.ArgumentParser()
    # Required arguments.
    parser.add_argument(
        "--instance_name",
        default= "ft06",
        help="Input video file.", )
    # Optional arguments.
    parser.add_argument(
        "--JSPLIB",
        default='../JSPLIB/',
        help="threshold for tracking", )
    args = parser.parse_args()
    return args

args = get_args(sys.argv)
instance_path = args.JSPLIB + 'instances/'
instance_info_path = args.JSPLIB + 'instances.json'
instance = InstanceHeuristic(args.instance_name,instance_path,instance_info_path)
print('Début heuristique')
instance.start_heuristic(fct=LPT,rand=0.1,display=False)
rep_order = RepetitionOrder(instance.order,instance.jobs,instance.n_machines) 
print("Descente directe : ",rep_order.order)
print("Durée : ",rep_order.duration)
print("Fin heuristique")

best_voisin = rep_order
nb_iteration = 1000
print("Début descente directe")
for i in range(nb_iteration):
    voisins = best_voisin.get_2swap_voisinage()
    if((best_voisin.order == get_best_voisin(voisins).order).all()):
        print("Convergence terminée")
        break
    else:
        best_voisin = get_best_voisin(voisins)
        print('Meilleur temps trouvé :',best_voisin.duration)

print("Descente directe : ",best_voisin.order)
print("Durée : ",best_voisin.duration)

print("Début exploration génétique")
optimum = instance.instance_info['optimum']
nb_iter = 100
nb_iter_GA = 10000
population_size=100

mutation_chance_max = 0.5
mutation_chance_min= 0.1
mutation_chance = 0.2
mutation_increase_rate_start = 1.0
mutation_decrease_rate = 0.999
mutation_increase_rate = mutation_increase_rate_start


comeback_chance_max = 0.5
comeback_chance_min= 0.2
comeback_chance = 0.2
comeback_increase_rate_start = 1.00
comeback_increase_rate = comeback_increase_rate_start


optimum_found=False

time_start = time.time()

population = best_voisin.get_2swap_voisinage()
population = get_best_subpopulation(population,population_size)
new_population = population
    
for j in range(nb_iter_GA):
    new_population = my_own_GA(new_population,
                               size=population_size,
                               mutation_chance=mutation_chance,
                               comeback_chance=comeback_chance,
                               best_duration=best_voisin.duration)
    best_of_pop = get_best_voisin(new_population)
    
    if(comeback_chance>comeback_chance_max or comeback_chance<comeback_chance_min):
        comeback_increase_rate = 2-comeback_increase_rate
        
    if(mutation_chance>mutation_chance_max or mutation_chance<mutation_chance_min):
        if(mutation_chance>mutation_chance_max):
            mutation_increase_rate = mutation_decrease_rate
        else:
            mutation_increase_rate = mutation_increase_rate_start
            
    if(best_of_pop.duration < best_voisin.duration):
        print('Meilleur temps trouvé :',best_of_pop.duration)
        comeback_increase_rate = comeback_increase_rate_start
        comeback_chance = comeback_chance_min
        mutation_increase_rate = mutation_increase_rate_start
        mutation_chance = mutation_chance_min
        best_voisin = best_of_pop
        
        print("Début descente directe")
        for i in range(nb_iteration):
            voisins = best_voisin.get_2swap_voisinage()
            if((best_voisin.order == get_best_voisin(voisins).order).all()):
                print("Convergence terminée")
                break
            else:
                best_voisin = get_best_voisin(voisins)
                print('Meilleur temps trouvé :',best_voisin.duration)
        
        print("Descente directe : ",best_voisin.order)
        print("Durée : ",best_voisin.duration)
        population = best_voisin.get_2swap_voisinage()
        population = get_best_subpopulation(population,population_size)
        new_population = population
    else:
        comeback_chance *= comeback_increase_rate
        mutation_chance *= mutation_increase_rate

    if(best_voisin.duration == optimum):
        optimum_found = True
        break
    if(j%50==0):
        mean_duration = get_mean_duration(new_population)
        print("Iteration : {}, moyenne des durée : {}".format(j,mean_duration))

time_end = time.time()
if(optimum_found): print("Optimum trouvé après {} itérations".format(j))
else: print("Optimum non trouvé après {} itérations".format(j))
print("Temps : ", time_end-time_start)
print("Durée final", best_voisin.duration)
print("Ordre final", best_voisin.order)
best_voisin.display_gantt()