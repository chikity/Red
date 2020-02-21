'''This script is used to interface with the IUCN website and returns the elements to be scraped.
It interfaces with the (lol) interface.py script and collects the inital dataframe containing the species name 
and the serials of the different species.
The eventual goal is to interface this code to a script communicating with the Google Sheets API and update the sheet in realtime.

-Sarthak
(18/02/2020)'''

import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from interface import fileReader, dataPorter

'''Specifying the species file that is being read by the script'''
speciesFile = 'data/birds.csv'
'''This is the home URL that will be used as a starting point for the scrape to start'''
homeURL = 'https://www.iucnredlist.org'

'''Grabbing the species dataframe from the interface.py script'''
speciesDf = fileReader(speciesFile)

'''Grabbing the number and the entire list of species in a given .csv file'''
numberOfSpecies, listOfSpecies, threatsAndStressesColumns = dataPorter(speciesDf)

def urlTweaker(speciesName, homeURL):
    '''This function takes the species name, lysis it and appends it to the home URL for scrapping'''
    urlPreElement = "https://www.iucnredlist.org/search?query="
    urlPostElement = "&searchType=species"
    speciesNameElements = speciesName.split(' ')
    speciesSearchURL = urlPreElement + speciesNameElements[0]+'%20'+speciesNameElements[1]+urlPostElement
    print('[INFO] Currently looking at search URL:' + speciesSearchURL)
    return speciesSearchURL

def speciesURLExtractor(searchSoup, homeURL):
    '''From the search page of the species, we collect the URL which will lead us to the species database'''
    speciesURL = searchSoup.find('a', {'class':'link--faux'}).get('href')
    speciesURL = homeURL + speciesURL
    print('[INFO] Currently looking at species URL:' + speciesURL)
    return speciesURL

def threatsAndStressesExtractor(speciesSoup):
    '''This function returns the threats and stresses which contain the stresses and threats of each species'''
    speciesThreatsAndStresses = []
    tdElements= speciesSoup.findAll('td')
    for tdElement in tdElements:
        if(tdElement.text):
            speciesThreatsAndStresses.append(tdElement.text)
    '''Lowering all the threats and stresses to carry out pattern matching with the '''
    speciesThreatsAndStresses = [speciesThreatsAndStress.lower() for speciesThreatsAndStress in speciesThreatsAndStresses]
    return speciesThreatsAndStresses

def threatsAndStressesChecker(speciesThreatsAndStresses, threatsAndStressesColumns):
    '''This function checks if any of the Threats and Stresses specific to the species match up with any of the column stresses/threats.
    Using set theory here to return the intersection of the two lists and use the elements to plot binary shifts under the corresponding'''
    speciesThreatsAndStressesSet = set(speciesThreatsAndStresses)
    threatsAndStressesColumnsSet = set(threatsAndStressesColumns)
    return list(speciesThreatsAndStressesSet.intersection(threatsAndStressesColumnsSet))

def threatsAndStressesPlotter(speciesDF, speciesCounter, threatsAndStresses):
    '''Finally! We plot the threats and stresses observed on the dataframe for the corresponding species and column'''
    for threatsAndStress in threatsAndStresses:
        speciesDF.loc[speciesCounter, threatsAndStress] = 1
    speciesDF.to_csv('hello.csv')

def browserInitializer(homeURL):
    '''Initializing the browser on which the rest of the pipeline will operate on. Also initializes the set of options in which the 
    Selenium middleware will operate on.'''
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get(homeURL)
    print('[INFO] Initializing browser instance')
    return browser

def htmlExtractor(browser):
    '''Pings the browser and returns the HTML code to be used by the rest of the functions lying within the for loop below'''
    htmlCode = browser.page_source
    print('[INFO] Extracting the HTML code')
    return htmlCode

def pageSouper(htmlCode):
    '''This function soups the HTML code to make it searchable by the individual modules of code'''
    pageSoup = bs(htmlCode, 'html.parser')
    print('[INFO] Souping the page')
    return pageSoup

'''Need this counter to keep track of which species on the list is being accessed at the moment.
In case the code shutsdown in between the scrapping, we don't want to start from scratch.'''
speciesCounter = 0

'''Generating the browser instance here'''
browser = browserInitializer(homeURL)

for speciesCounter in range(speciesCounter, numberOfSpecies):
    '''Additional functions to be used here:
    1. A function that takes the string of the species name and cuts it up, appends it to the homeURL
    2. A browser pinger which takes this URL, pings it and returns the page.
    3. A function to reduce the page to its bare HTML.
    4. A function which extracts the required element(s) from the HTML code. One for each element to be scrapped.
    5. A CSV dumper to dump the elements to the disc.'''

    '''Here, we collect the name of the species for which the data has to be scrapped. We then pass this name onto the urlTweaker to insert it into the 
    default IUCN website URL.'''
    speciesName = speciesDf.loc[speciesCounter, 'species']

    '''Using the species name to arrive at the URL to ping the browser'''
    speciesSearchURL = urlTweaker(speciesName, homeURL)

    '''Invoking the search results page here using the browser'''
    browser.get(speciesSearchURL)

    '''Delaying the collection of code because the IUCN website takes time to respond to an incoming ping'''
    time.sleep(5)

    '''Extracting the HTML code'''
    htmlSearchCode = htmlExtractor(browser)

    '''Souping the HTML here to make it more readable and look for elements within'''
    searchSoup = pageSouper(htmlSearchCode)

    '''From the search result of the species we collect the URL which will direct us to the species database'''
    speciesURL = speciesURLExtractor(searchSoup, homeURL)
    
    '''Here, we get the page containing all the information of a specific species'''
    browser.get(speciesURL)

    '''Delaying the collection of code because the IUCN website takes time to respond to an incoming ping'''
    time.sleep(5)

    '''Now extracting the HTML of the page'''
    htmlCode = htmlExtractor(browser)

    '''Souping the page!'''
    speciesSoup = pageSouper(htmlCode)

    '''Grabbing the td_elements which contains all the threats and stresses'''
    speciesThreatsAndStresses = threatsAndStressesExtractor(speciesSoup)

    '''Here, we check if the speciesThreatsAndStresses match the columns in the pandas dataframe'''
    threatsAndStresses = threatsAndStressesChecker(speciesThreatsAndStresses, threatsAndStressesColumns)

    '''Here we plot binary transformations under the corresponding threats/stresses column of the pandas dataframe for each species'''
    threatsAndStressesPlotter(speciesDf, speciesCounter, threatsAndStresses)

    '''Appennding the species counter to go to the next species on the list, in case the code breaksdown prematurely'''
    speciesCounter += 1