'''This script interfaces with the .csv files provided by NCF and contains function to import this data into
manageable pandas dataframes.
Check out the larger project at https://github.com/SarthakJShetty/Red

-Sarthak
(18/02/2020)'''

'''Reading the csv file as a pandas dataframe and port over the entire column as a list.'''
import pandas as pd

def fileReader(csvFile):
    '''This function reads the csvFile and sends it over to the scraper'''
    speciesDF = pd.read_csv(csvFile)
    return speciesDF

def dataPorter(speciesDF):
    '''This function ports the species column of the .csv file to a list and sends it over to the scraper'''
    listOfSpecies = []
    '''We use this integer value to keep track of which species is being currently read by the scraper code'''
    numberOfSpecies = 0
    '''Looping through the pandas column and appending the listOfSpecies list, this will be returned to the scraper code'''
    for element in (speciesDF['species']):
        listOfSpecies.append(element)
        numberOfSpecies += 1
    '''Returning the list of species and number of species'''
    return numberOfSpecies, listOfSpecies