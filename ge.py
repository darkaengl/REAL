from grape import grape
from grape import algorithms
import re
from ast import literal_eval
import warnings

from os import path
import pandas as pd
import numpy as np
from deap import creator, base, tools
import random

from scripts.simulations.util import falsifier, evaluate
from scripts.templates.old.scenic_template import get_scenic_code
import multiprocessing

import os 
import mlflow

def evaluate_(ind, dummy):

    return 10,



# os.environ["MLFLOW_TRACKING_URI"] = "http://127.0.0.1:5000"

# # Set our tracking server uri for logging
# mlflow.set_tracking_uri(uri="http://127.0.0.1:5000")


# warnings.filterwarnings('ignore')

GRAMMAR_FILE = 'old.bnf'
BNF_GRAMMAR = grape.Grammar(r"./scripts/templates/old/" + GRAMMAR_FILE)

RANDOM_SEED = 42

toolbox = base.Toolbox()

# define a single objective, minimising fitness strategy:
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

creator.create('Individual', grape.Individual, fitness=creator.FitnessMin)

toolbox.register("populationCreator", grape.sensible_initialisation, creator.Individual) 
# toolbox.register("populationCreator", grape.random_initialisation, creator.Individual) 
#toolbox.register("populationCreator", grape.PI_Grow, creator.Individual) 

toolbox.register("evaluate", evaluate_)

# Tournament selection:
toolbox.register("select", tools.selTournament, tournsize=7) #selLexicaseFilter

# Single-point crossover:
toolbox.register("mate", grape.crossover_onepoint)

# Flip-int mutation:
toolbox.register("mutate", grape.mutation_int_flip_per_codon)

# pool = multiprocessing.Pool(32)
# toolbox.register("map", pool.map)

POPULATION_SIZE = 100
MAX_INIT_TREE_DEPTH = 6
MIN_INIT_TREE_DEPTH = 4

MAX_GENERATIONS = 200
P_CROSSOVER = 0.8
P_MUTATION = 0.01
ELITE_SIZE = 0#round(0.01*POPULATION_SIZE) #it should be smaller or equal to HALLOFFAME_SIZE
HALLOFFAME_SIZE = 1#round(0.01*POPULATION_SIZE) #it should be at least 1

MIN_INIT_GENOME_LENGTH = 95#*6
MAX_INIT_GENOME_LENGTH = 115#*6
random_initilisation = False #put True if you use random initialisation

CODON_CONSUMPTION = 'lazy'
GENOME_REPRESENTATION = 'list'
MAX_GENOME_LENGTH = None#'auto'

MAX_TREE_DEPTH = 35 #equivalent to 17 in GP with this grammar
MAX_WRAPS = 0
CODON_SIZE = 255

# random.seed(RANDOM_SEED) 

population = toolbox.populationCreator(pop_size=POPULATION_SIZE, 
                                       bnf_grammar=BNF_GRAMMAR, 
                                       min_init_depth=MIN_INIT_TREE_DEPTH,
                                       max_init_depth=MAX_INIT_TREE_DEPTH,
                                       codon_size=CODON_SIZE,
                                       codon_consumption=CODON_CONSUMPTION,
                                       genome_representation=GENOME_REPRESENTATION
                                        )

def replace_with_value(match):
            return match.group(2)


for ind in population:

    # print(ind.phenotype,'\n')
    text = ind.phenotype
    matches = re.findall(r'({.*?})', text)
    matches = [item.strip('{}').strip(' ').split(':') for item in matches]
    param_dict = {key.strip(' '): value.strip(' ') for key, value in matches}
    param_dict['mitigation'] = None
    # Substitute each {key : value} with just the value
    rule = re.sub(r'\{\s*(\w+)\s*:\s*([\w\.\d]+)\s*\}', replace_with_value, text)
    print(rule)
    # print(param_dict)

    # code = get_scenic_code(params=param_dict)
    # print(code)
    # break

    

# # define the hall-of-fame object:
# hof = tools.HallOfFame(HALLOFFAME_SIZE)

# # prepare the statistics object:
# stats = tools.Statistics(key=lambda ind: ind.fitness.values)
# stats.register("avg", np.nanmean)
# stats.register("std", np.nanstd)
# stats.register("min", np.nanmin)
# stats.register("max", np.nanmax)

# REPORT_ITEMS = ['gen', 'invalid', 'avg', 'std', 'min', 'max', 
#                 'fitness_test',
#                 'best_ind_length', 'avg_length', 
#                 'best_ind_nodes', 'avg_nodes', 
#                 'best_ind_depth', 'avg_depth', 
#                 'avg_used_codons', 'best_ind_used_codons', 
#                  'behavioural_diversity',
#                 'structural_diversity', 'fitness_diversity',
#                 'selection_time', 'generation_time']

# # perform the Grammatical Evolution flow:
# population, logbook = algorithms.ge_eaSimpleWithElitism(population, toolbox, cxpb=P_CROSSOVER, mutpb=P_MUTATION,
#                                             ngen=MAX_GENERATIONS, elite_size=ELITE_SIZE,
#                                             bnf_grammar=BNF_GRAMMAR,
#                                             codon_size=CODON_SIZE,
#                                             max_tree_depth=MAX_TREE_DEPTH,
#                                             max_genome_length=MAX_GENOME_LENGTH,
#                                             codon_consumption=CODON_CONSUMPTION,
#                                             report_items=REPORT_ITEMS,
#                                             genome_representation=GENOME_REPRESENTATION,
#                                             stats=stats, halloffame=hof, verbose=False)

