'''This script is used to interface with the IUCN website and returns the elements to be scraped.
It interfaces with the (lol) interface.py script and collects the inital dataframe containing the species name 
and the serials of the different species.
The eventual goal is to interface this code to a script communicating with the Google Sheets API and update the sheet in realtime.

-Sarthak
(18/02/2020)'''

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from interface import fileReader, dataPorter

speciesFile = 'data/birds.csv'
homeURL = 'https://www.iucnredlist.org/'

'''Grabbing the species dataframe from the interface.py script'''
speciesDf = fileReader(speciesFile)

'''Grabbing the number and the entire list of species in a given .csv file'''
numberOfSpecies, listOfSpecies = dataPorter(speciesDf)

def browserInitializer(homeURL):
    '''Initializing the browser on which the rest of the pipeline will operate on. Also initializes the set of options in which the 
    Selenium middleware will operate on.'''
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Chrome(chrome_options=chrome_options)
    return browser

def htmlExtractor(browser, url):
    '''Pings the browser and returns the HTML code to be used by the rest of the functions lying within the for loop below'''
    browser.get(url)
    htmlCode = browser.page_source
    return htmlCode

def pageSouper(htmlCode):
    '''This function soups the HTML code to make it searchable by the individual modules of code'''
    pageSoup = bs(htmlCode, 'html.parser')
    return pageSoup

'''Need this counter to keep track of which species on the list is being accessed at the moment.
In case the code shutsdown in between the scrapping, we don't want to start from scratch.'''
speciesCounter = 0

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
    
    '''Appennding the species counter to go to the next species on the list, in case the code breaksdown prematurely'''
    speciesCounter+=1