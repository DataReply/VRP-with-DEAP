__author__ = 'Tomasz Godzik'

from utils.evolution import *
from utils.reader import *
from utils.paint import *
from deap import base
from deap import creator
from deap import tools
import time
import sys
import multiprocessing
import pickle

#simulation parameters
instance = "C101.txt"

#read the problem from file
problem = from_file(["./solomon_25/" + instance])[0]

#count the number of customers
customers_num = len(problem.customers.keys())

# create fitness and individual
creator.create("FitnessSolution", base.Fitness, weights=(-0.1, -1.0))
creator.create("Individual", list, fitness=creator.FitnessSolution)

#create list of all customers
customer = range(1, customers_num + 1)

#creating new individuals
toolbox = base.Toolbox()

#enable multiprocessing
if ("-m" in sys.argv) or ("--multiprocessing" in sys.argv):
        pool = multiprocessing.Pool(processes=4)
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
toolbox.register("select", tools.selNSGA2)


#Main part of program - for scoop
def main():
    start_time = time.time()
    #We create the population
    pop = toolbox.population(n=300)

    #How many turns?
    ngen = 600

    #evaluate the first population
    for i in pop:
        i.fitness.values = evaluate(problem, i)

    # create pareto hall of fame
    hall = tools.ParetoFront()

    #cross possibility
    crs = 0.3
    #start simulation
    for g in range(ngen):
        # Select the next generation individuals - half
        selected = toolbox.select(pop, len(pop) / 2)
        # Clone the selected individuals
        offspring = map(toolbox.clone, selected)

        # Apply crossover on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < crs:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        # Apply mutation on the offspring
        for mutant in offspring:
            toolbox.mutate(mutant)
            del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # The population is entirely replaced by the offspring and the selected
        pop[:] = offspring + selected
        hall.update(offspring)

    print "Execution stopped after : " + str(time.time() - start_time)
    #Print the hall of fame
    for i in hall:
        i.fitness.values = calculate_dist(problem, i)
        print i.fitness
        print i

    if ("-d" in sys.argv) or ("--draw" in sys.argv):
        draw_all(hall, problem)

    if ("-s" in sys.argv) or ("--save" in sys.argv):
        dump_file = open(instance + ".solution", "wb")
        pareto_list = []
        for i in hall:
            pareto_list.append([j for j in i])
        pickle.dump(pareto_list, dump_file)


if __name__ == '__main__':
    main()