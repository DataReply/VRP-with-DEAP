__author__ = 'Tomasz Godzik'

import math
import random


def dist(x1, x2, y1, y2):
    return math.sqrt(
        math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))


#calculate a time cost of a route
def evaluate_route(route, problem, penalty=True, penalty_cost=10000):
    #total distance
    cost = 0
    time = 0
    additional = 0
    current_cargo = problem.capacity
    current_x = problem.depotx
    current_y = problem.depoty
    for i in route:
        #check if we have enough cargo (check if possible - multiple goes?)
        if current_cargo > problem.customers[i].demand:
            #calculate the distance from one customer to another
            time += dist(problem.customers[i].x, current_x, problem.customers[i].y, current_y)
        else:
            # cost of going back to customer
            time += dist(problem.depotx, current_x, problem.depoty, current_y)
            time += dist(problem.customers[i].x, problem.depotx, problem.customers[i].y, problem.depoty)
            current_cargo = problem.capacity

        #drop cargo
        current_cargo -= problem.customers[i].demand

        #change current location
        current_x = problem.customers[i].x
        current_y = problem.customers[i].y

        #if we have to wait

        time = max(problem.customers[i].ready, time)
        #if we are late, add penalty
        additional += max(0, (time - problem.customers[i].due) * penalty_cost)

        #time it takes to drop it
        time += problem.customers[i].service

    time += dist(current_x, problem.depotx, current_y, problem.depoty)
    if penalty:
        return time + additional
    else:
        return time


#calculate the total distance traveled on one route
def total_dist(route, problem):
    #total distance
    cost = 0
    current_cargo = problem.capacity
    current_x = problem.depotx
    current_y = problem.depoty
    for i in route:
        #check if we have enough cargo (check if possible - multiple goes?)
        if current_cargo > problem.customers[i].demand:
            #calculate the distance from one customer to another
            cost += dist(problem.customers[i].x, current_x, problem.customers[i].y, current_y)
        else:
            # cost of going back to customer
            cost += dist(problem.depotx, current_x, problem.depoty, current_y)
            cost += dist(problem.customers[i].x, problem.depotx, problem.customers[i].y, problem.depoty)
            current_cargo = problem.capacity

        #drop cargo
        current_cargo -= problem.customers[i].demand

        #change current location
        current_x = problem.customers[i].x
        current_y = problem.customers[i].y

    cost += dist(current_x, problem.depotx, current_y, problem.depoty)
    return cost


#we calculate the fitness function
def evaluate(problem, ind):
    a = len(ind)
    b = 0
    for i in ind:
        b += evaluate_route(i, problem)
    return b, a


#we calculate the total distance covered
def calculate_dist(problem, ind):
    a = len(ind)
    b = 0
    for i in ind:
        b += total_dist(i, problem)
    return b, a


def mutate_swap(ind):
    route1 = random.randint(0, len(ind) - 1)
    route2 = random.randint(0, len(ind) - 1)

    client1 = random.randint(0, len(ind[route1]) - 1)
    client2 = random.randint(0, len(ind[route2]) - 1)

    tmp = ind[route1][client1]
    ind[route1][client1] = ind[route2][client2]
    ind[route2][client2] = tmp

    return ind,


def mutate_inverse(ind):
    which = random.randint(0, len(ind) - 1)
    ind[which] = ind[which][::-1]
    return ind,


def mutate_insert(ind, max_vehicles):
    route = random.randint(0, len(ind) - 1)
    client = random.randint(0, len(ind[route]) - 1)
    found = ind[route][client]

    if random.random() < (1.0 / (2.0 * len(ind))) and len(ind) < max_vehicles:
        ind.append([found])
    else:
        new_route = random.randint(0, len(ind) - 1)
        place = random.randint(0, len(ind[new_route]))
        ind[new_route].insert(place, found)

    ind[route].remove(found)

    if len(ind[route]) == 0:
        ind.remove(ind[route])

    return ind,


def mutate_displace(ind, max_vehicles):
    route = random.randint(0, len(ind) - 1)
    rfrom = random.randint(0, len(ind[route]) - 1)
    rto = random.randint(rfrom + 1, len(ind[route]))
    subroute = ind[route][rfrom:rto]
    ind[route] = ind[route][0:rfrom] + (ind[route][rto:len(ind[route])])

    if random.random() < (1.0 / (2.0 * len(ind))) and len(ind) < max_vehicles:
        ind.append(subroute)
    else:
        new_route = random.randint(0, len(ind) - 1)
        place = random.randint(0, len(ind[new_route]))
        ind[new_route] = ind[new_route][0:place] + subroute + ind[new_route][place:len(ind[new_route])]

    if len(ind[route]) == 0:
        ind.remove(ind[route])
    return ind,


def mutate(max_v, ind, swap_rate=0.1, inverse_rate=0.5, insert_rate=0.1, displace_rate=0.15):
    if random.random() <= swap_rate:
        ind, = mutate_swap(ind)
    if random.random() <= inverse_rate:
        ind, = mutate_inverse(ind)
    if random.random() <= insert_rate:
        ind, = mutate_insert(ind, max_v)
    if random.random() <= displace_rate:
        ind, = mutate_displace(ind, max_v)
    return ind,

# czy to dobrze dziala
def cross_over(problem, ind1, ind2):
    route = random.randint(0, len(ind1) - 1)
    rfrom = random.randint(0, len(ind1[route]) - 1)
    rto = random.randint(rfrom + 1, len(ind1[route]))
    subroute = ind1[route][rfrom:rto]
    whereto = (0, 0)
    min_dist = dist(problem.customers[ind2[0][0]].x, problem.customers[subroute[0]].x, problem.customers[ind2[0][0]].y,
                    problem.customers[subroute[0]].y)
    for i in ind2:
        for j in i:
            if j in subroute:
                i.remove(j)
            else:
                tmp_dist = dist(problem.customers[j].x, problem.customers[subroute[0]].x, problem.customers[j].y,
                                problem.customers[subroute[0]].y)
                if tmp_dist < min_dist:
                    min_dist = tmp_dist
                    whereto = (ind2.index(i), i.index(j))
        if len(i) == 0:
            ind2.remove(i)

    ind2[whereto[0]] = ind2[whereto[0]][0:whereto[1]] + subroute + ind2[whereto[0]][whereto[1]:len(ind2[whereto[0]])]
    return ind1, ind2

#function to tell apart 2 solutions
def pareto_similar(ind1, ind2):
    for i in ind1:
        if ind2.count(i) == 0:
            return False
    return True