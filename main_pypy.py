__author__ = 'Tomasz Godzik'

from utils.evolution import *
from utils.reader import *
from deap import base
from deap import creator
from deap import tools
import time
import multiprocessing
import pickle
import sys

#simulation parameters
instance = "RC101.txt"  # R101.txt, RC101.txt, C101.txt
start_population = 300  # populacja 500
ngen = 1000  # ngen = 600
sim_weights = (-0.001, -1.0)  # weights (-1.0, -1.0), (-0.1, -1.0), (-0.01, -1.0)
swap_rate = 0.15  # 0.1, 0.2
inverse_rate = 0.15  # 0.1, 0.2
insert_rate = 0.15  # 0.1, 0.2
displace_rate = 0.15  # 0.1, 0.2
crs = 0.7  # 0.5, 0.7, 1.0
pop_part = 1.0  #
function = tools.selNSGA2  # tools.selNSGA2

#string that is prined to a file.
result_string = "%s; %d; %d; %f %f; %f; %f; %f; %f; %f; %s; " % (instance, start_population, ngen,
                                                                 sim_weights[0], sim_weights[1],
                                                                 swap_rate, inverse_rate, insert_rate,
                                                                 displace_rate, crs, function.__name__)


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

#2001
#Main part of program - for multiprocessing
def main():
    #random.seed(3311)
    start_time = time.time()

    #create the population
    pop = toolbox.population(n=start_population)

    #evaluate the first population
    for i in pop:
        i.fitness.values = evaluate(problem, i)

    #create pareto hall of fame
    hall = tools.ParetoFront(pareto_similar)

    #start simulation
    for g in range(ngen):

        #sys.stdout.write(str(g) + " ")

        #select individuals for mating
        selected = toolbox.select(pop, int(len(pop) * pop_part))
        #clone the selected individuals
        offspring = map(toolbox.clone, selected)

        #apply crossover on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < crs:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        #apply mutation on the offspring
        for mutant in offspring:
            toolbox.mutate(mutant, swap_rate, inverse_rate, insert_rate, displace_rate)
            del mutant.fitness.values

        #evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        #the population reduced back
        pop[:] = toolbox.select(pop + offspring, start_population)
        hall.update(offspring)

        #print percentage
        cur_gen = int(((g + 1) / float(ngen)) * 100)
        sys.stdout.write("\r%d%%" % cur_gen)
        sys.stdout.flush()

    print "\nExecution stopped after : " + str(time.time() - start_time)

    #print the hall of fame

    hall_string = ""
    inds_string = ";"
    for i in hall:
        hall_string += "(d : %f e: %f n: %d)" % (
        calculate_dist(problem, i)[0], i.fitness.values[0], i.fitness.values[1])
        inds_string += str(i) + ";"

    if ("-s" in sys.argv) or ("--save" in sys.argv):
        dump_file = open(instance + ".solution", "wb")
        pareto_list = []
        for i in hall:  # also check if valid solution
            pareto_list.append([j for j in i])
        pickle.dump(pareto_list, dump_file)

    for i in hall:
        print calculate_dist(problem, i)[0], i.fitness.values[0], i.fitness.values[1]
        print str(i) + ";"
    return hall_string + inds_string


if __name__ == '__main__':

    main()

