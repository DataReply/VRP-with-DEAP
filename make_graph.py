__author__ = 'Tomasz Godzik'

name = "RC101.txt"
from utils.reader import *
import pickle
from utils import evaluate
import pygal
from pygal.style import LightStyle

file_solution = open(name + ".solution")

hall = pickle.load(file_solution)


def generate(listing):
    problem = from_file(["./solomon/" + name])[0]
    for ind in hall:
        tmp = evaluate(problem, ind)
        yield tmp[1], tmp[0]

to_plot = [i for i in generate(hall)]

#print to_plot

xy_chart = pygal.XY(style=LightStyle)
xy_chart.title = 'Pareto front'
xy_chart.add('cost, vehicles', to_plot)

xy_chart.render_to_file('RC101.svg')