__author__ = 'Tomasz Godzik'

from utils.evolution import *
from utils.reader import *
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import time
import multiprocessing
import pickle
import sys

#simulation parameters
instance = "C101.txt"  # R101.txt, RC101.txt
sim_weights = (-1.0, -0.1)  # weights (-1.0, -1.0), (-0.1, -1.0), (-0.01, -1.0)
function = tools.selNSGA2  # tools.selNSGA2  # tools.selSPEA2

#string that is prined to a file.

result_string = ""
#read the problem from file
problem = from_file(["./solomon/" + instance])[0]

#count the number of customers
customers_num = len(problem.customers.keys())

# create fitness and individual
creator.create("FitnessSolution", base.Fitness, weights=sim_weights)
creator.create("Individual", list, fitness=creator.FitnessSolution)

#create list of all customers
customer = range(1, customers_num + 1)

#create new individuals
toolbox = base.Toolbox()

#using multiprocessing
if ("-m" in sys.argv) or ("--multiprocessing" in sys.argv):
    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)

toolbox.register("attr", randomize_list, customer, problem.vehicles)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.attr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#Register evaluation function
toolbox.register("evaluate", evaluate, problem)
#Register cross function
toolbox.register("mate", cross_over, problem)
#Register mutation function
toolbox.register("mutate", mutate, problem.vehicles)
#Register selection function
toolbox.register("select", function)


#Main part of program - for multiprocessing
def main():
    start_time = time.time()

    random.seed(64)
    NGEN = 2000
    MU = 200
    LAMBDA = 100
    CXPB = 0.5
    MUTPB = 0.5

    pop = toolbox.population(n=MU)
    hall = tools.ParetoFront()

    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
                              halloffame=hall)

    print "\nExecution stopped after : " + str(time.time() - start_time)

    #print the hall of fame

    hall_string = ""
    inds_string = ";"
    for i in hall:
        hall_string += "(d : %f e: %f n: %d)" % (calculate_dist(problem, i)[0], i.fitness.values[0], i.fitness.values[1])
        inds_string += str(i) + ";"

    if ("-s" in sys.argv) or ("--save" in sys.argv):
        dump_file = open(instance + ".solution", "wb")
        pareto_list = []
        for i in hall:  # also check if valid solution
            pareto_list.append([j for j in i])
        pickle.dump(pareto_list, dump_file)

    for i in pop:
        if i.fitness.values[0] < 100000.0:
            print calculate_dist(problem, i)[0], i.fitness.values[0], i.fitness.values[1]
            print str(i) + ";"
    return hall_string + inds_string


if __name__ == '__main__':
    results_file = open("results.csv", "a")

    result_string += main()

    #print result_string
    #results_file.write(result_string + "\n")
    #results_file.close()
