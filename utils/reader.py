__author__ = 'Tomasz Godzik'
import re
import random


class Customer:
    def __init__(self, x, y, demand, ready, due, service):
        self.x = x
        self.y = y
        self.ready = ready
        self.demand = demand
        self.due = due
        self.service = service

    def __str__(self):
        return "(%d, %d) %d, %d - %d, %d" % (self.x, self.y, self.demand, self.ready, self.due, self.service)


class Problem:
    customers = {}

    def __init__(self):
        pass

    def __str__(self):
        ret = "name: %s, vehicles: %d, capacity: %d \ndepot: (%d,%d) \n" % (
        self.name, self.vehicles, self.capacity, self.depotx, self.depoty)
        for (key, value) in self.customers.items():
            ret += str(key) + ": " + str(value) + "\n"

        return ret


def parse_other(lines):
    problem = Problem()
    for line in lines:
        matched = re.findall("[0-9\.]+", line)
        if len(matched) == 4:
            problem.name = matched[0]
            problem.vehicles = int(matched[1])
        elif len(matched) == 2:
            problem.capacity = int(matched[1])
        elif len(matched) > 4:
            if int(matched[0]) == 0:
                problem.depotx = float(matched[1])
                problem.depoty = float(matched[2])
            else:
                problem.customers[int(matched[0])] = Customer(float(matched[1]), float(matched[2]), float(matched[4]),
                                                              int(matched[8]), int(matched[9]), float(matched[3]))
    return problem


def from_file_other(arg_list):
    return_list = []
    for name in arg_list:
        opened_file = open(name)
        vrp = parse(opened_file.readlines())
        return_list.append(vrp)
    return return_list


def parse(lines):
    problem = Problem()
    for line in lines:
        matched = re.findall("[0-9]+", line)
        if len(matched) == 1:
            problem.name = matched[0]
        elif len(matched) == 2:
            problem.vehicles = int(matched[0])
            problem.capacity = int(matched[1])
        elif len(matched) > 2:
            if int(matched[0]) == 0:
                problem.depotx = int(matched[1])
                problem.depoty = int(matched[2])
            else:
                problem.customers[int(matched[0])] = Customer(int(matched[1]), int(matched[2]), int(matched[3]),
                                                              int(matched[4]), int(matched[5]), int(matched[6]))
    return problem


def from_file(arg_list):
    return_list = []
    for name in arg_list:
        opened_file = open(name)
        vrp = parse(opened_file.readlines())
        return_list.append(vrp)
    return return_list


def randomize_list(xs, n):
    n = random.randint(1, n)
    ys = list(xs)
    random.shuffle(ys)
    size = len(ys) / n
    leftovers = ys[size * n:]
    for c in xrange(n):
        if leftovers:
            extra = [leftovers.pop()]
        else:
            extra = []
        yield ys[c * size:(c + 1) * size] + extra


