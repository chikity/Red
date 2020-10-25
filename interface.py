'''This script interfaces with the .csv files provided by NCF and contains function to import this data into
manageable pandas dataframes.
Check out the larger project at https://github.com/SarthakJShetty/Red

-Sarthak
(18/02/2020)'''

'''Reading the csv file as a pandas dataframe and port over the entire column as a list.'''
import pandas as pd
import os

def fileReader(speciesFile):
    '''This function reads the csvFile and sends it over to the scraper'''
    
    '''This clause is required so that the data is not overwritten everytime the code shuts off and restarts'''
    if(os.path.exists(speciesFile.split('.')[0]+'_WORKING'+'.csv')):
        csvFile = speciesFile.split('.')[0]+'_WORKING'+'.csv'
    else:
        csvFile = speciesFile
    '''Pandas has a memory issue when dealing with lot of columns (117) in this case. Helps if you specify the data-type of the unique columns'''
    speciesDF = pd.read_csv(csvFile, dtype={'species':str, 'tt':str})
    return speciesDF

def columnTweaker(speciesDF):
    '''Here we take the speciesDF and extract the columns and lower the name of the individual elements'''
    threatsAndStressesColumn = [column.lower() for column in speciesDF.columns]
    '''Replacing the entire column headings with a lowerscript version to ensure pattern matching  while scrapping the website'''
    speciesDF.columns = threatsAndStressesColumn
    return threatsAndStressesColumn

def lastSpeciesChecker(speciesDF):
    '''We want to check the last scrapped species and return it to the scraper to avoid manually changing it in the code'''
    '''Indexing starts from 0, hence we subtract 1 from the length of the dataframe'''
    speciesCounter = (len(speciesDF)-1)
    
    '''We start from the reverse, because if we start from the top some species may have 0 status for all population trends. If we approach
    the dataframe from the reverse direction, we get the latest species for whom the data has not been tabulated yet, indicating the last species scrapped.'''
    while speciesCounter >= 0:
        '''If any of the population trend parameters have a value stored in them, then return the corresponding speciesCounter, indicating last scrapped species'''
        if(int(speciesDF.loc[speciesCounter, 'd']) or int(speciesDF.loc[speciesCounter, 's']) or int(speciesDF.loc[speciesCounter, 'u']) or int(speciesDF.loc[speciesCounter, 'i']) or (speciesCounter==0)):
            '''If the previous condition is satisfied return the speciesCounter currently under cycle'''
            return speciesCounter
            speciesCounter = 0
        else:
            '''If condition is not satisfied, go to the previous row'''
            speciesCounter-=1

def csvDumper(speciesFile, speciesDF):
    '''This function utilizes the pandas functionality, to_csv() to dump the dataframe, for analysis and posteriety'''
    speciesDF.to_csv(speciesFile.split('.')[0]+'_WORKING'+'.csv', index=False)

def dataPorter(speciesDF):
    '''This function ports the species column of the .csv file to a list and sends it over to the scraper'''
    listOfSpecies = []
    '''We use this integer value to keep track of which species is being currently read by the scraper code'''
    numberOfSpecies = 0
    '''Looping through the pandas column and appending the listOfSpecies list, this will be returned to the scraper code'''
    for element in (speciesDF['species']):
        listOfSpecies.append(element)
        numberOfSpecies += 1
    '''Extracting the columns and lowercasing all the elements'''
    threatsAndStressesColumn = columnTweaker(speciesDF)
    '''Returning the list of species and number of species'''
    return numberOfSpecies, listOfSpecies, threatsAndStressesColumn