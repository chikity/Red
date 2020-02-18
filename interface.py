'''This script interfaces with the .csv files provided by NCF and contains function to import this data into
manageable pandas dataframes.
Check out the larger project at https://github.com/SarthakJShetty/Red

-Sarthak
(18/02/2020)'''

import csv
import pandas as pd

file = 'data/birds.csv'

with open(file) as csv_file:
    for element in csv_file:
        print(element)