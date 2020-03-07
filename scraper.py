'''This script is used to interface with the IUCN website and returns the elements to be scraped.
It interfaces with the (lol) interface.py script and collects the inital dataframe containing the species name 
and the serials of the different species.
The eventual goal is to interface this code to a script communicating with the Google Sheets API and update the sheet in realtime.

-Sarthak
(18/02/2020)'''

import time
from bs4 import BeautifulSoup as bs
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from interface import fileReader, dataPorter, csvDumper, lastSpeciesChecker

'''Specifying the species file that is being read by the script'''
speciesFile = 'data/birds.csv'
'''This is the home URL that will be used as a starting point for the scrape to start'''
homeURL = 'https://www.iucnredlist.org'

'''Grabbing the species dataframe from the interface.py script'''
speciesDF = fileReader(speciesFile)

'''Grabbing the number and the entire list of species in a given .csv file'''
numberOfSpecies, listOfSpecies, threatsAndStressesColumns = dataPorter(speciesDF)

def urlTweaker(speciesName, speciesCounter, homeURL):
    '''This function takes the species name, lysis it and appends it to the home URL for scrapping'''
    urlPreElement = "https://www.iucnredlist.org/search?query="
    urlPostElement = "&searchType=species"
    speciesNameElements = speciesName.split(' ')
    speciesSearchURL = urlPreElement + speciesNameElements[0]+'%20'+speciesNameElements[1]+urlPostElement
    print('[INFO]'+' Species Number: '+str(speciesCounter+1)+'\n[INFO] Species Name: '+speciesName+'\n[INFO] Currently looking at search URL: ' + speciesSearchURL)
    return speciesSearchURL

def speciesURLExtractor(searchSoup, homeURL):
    '''From the search page of the species, we collect the URL which will lead us to the species database'''
    speciesURL = searchSoup.find('a', {'class':'link--faux'}).get('href')
    speciesURL = homeURL + speciesURL
    print('[INFO] Currently looking at species URL:' + speciesURL)
    return speciesURL

def threatsTextsExtractor(speciesSoup):
    '''This function returns the text of the threats faced by each of the species'''
    threatsCards = speciesSoup.findAll('div', {'id':'threats-details'})
    if threatsCards:
        for threatsCard in threatsCards:
            return threatsCard.findAll('div', {'class':'text-body'})[0].text
    else:
        pass

def threatsTextsPlotter(speciesDF, speciesCounter, threatsText):
    '''Writing the text extracted by the threatsTextsExtractor to the pandas dataframe prior to writing to the disc'''
    speciesDF.loc[speciesCounter, 'tt'] = threatsText
    return speciesDF

def threatsAndStressesExtractor(speciesSoup):
    '''This function returns the threats and stresses which contain the stresses and threats of each species'''
    speciesThreatsAndStresses = []
    tdElements= speciesSoup.findAll('td')
    for tdElement in tdElements:
        if(tdElement.text):
            speciesThreatsAndStresses.append(tdElement.text)
    '''Lowering all the threats and stresses to carry out pattern matching with the '''
    speciesThreatsAndStresses = [speciesThreatsAndStress.lower() for speciesThreatsAndStress in speciesThreatsAndStresses]
    if(speciesThreatsAndStresses):
       return speciesThreatsAndStresses
    else:
        '''Incase no threats are found for the given species'''
        pass

def threatsAndStressesChecker(speciesThreatsAndStresses, threatsAndStressesColumns):
    '''This function checks if any of the Threats and Stresses specific to the species match up with any of the column stresses/threats.
    Using set theory here to return the intersection of the two lists and use the elements to plot binary shifts under the corresponding'''
    if(speciesThreatsAndStresses):
        speciesThreatsAndStressesSet = set(speciesThreatsAndStresses)
        threatsAndStressesColumnsSet = set(threatsAndStressesColumns)
        return list(speciesThreatsAndStressesSet.intersection(threatsAndStressesColumnsSet))
    else:
        return []

def threatsAndStressesPlotter(speciesDF, speciesCounter, threatsAndStresses):
    '''Finally! We plot the threats and stresses observed on the dataframe for the corresponding species and column'''
    for threatsAndStress in threatsAndStresses:
        speciesDF.loc[speciesCounter, threatsAndStress] = 1
    return speciesDF

def populationTrendChecker(speciesSoup):
    '''This function checks if the population is: 1. Increasing, or 2. Decreasing, or 3. Stable, or 4. Unknown'''
    populationTrend = (speciesSoup.find('a', {'href':'/search?populationTrend=0&searchType=species'}) or speciesSoup.find('a', {'href':'/search?populationTrend=0&searchType=species'}) or speciesSoup.find('a', {'href':'/search?populationTrend=1&searchType=species'}) or speciesSoup.find('a', {'href':'/search?populationTrend=2&searchType=species'}) or speciesSoup.find('a', {'href':'/search?populationTrend=3&searchType=species'}) or speciesSoup.find('a', {'href':'/search?searchType=species'}))
    if(populationTrend.text):
        return populationTrend.text
    else:
        return 'Unknown'

def populationTrendPlotter(speciesDF, speciesCounter, populationTrend):
    '''Plotting the data on the speciesDF'''
    speciesDF.loc[speciesCounter, populationTrend.lower()[0]] = 1
    return speciesDF

def browserPinger(browser, speciesURL):
    '''This function pings the website before scrapping. Using this as a fork of browserInitializer because we need to refresh the browser
    instance when it times out.'''
    try:
        browser.get(speciesURL)
        return browser
    except(TimeoutException):
        '''Repeated TimeOut exceptions, so we want to include this line.'''
        browser.refresh()
        return browser

def browserInitializer(homeURL):
    '''Initializing the browser on which the rest of the pipeline will operate on. Also initializes the set of options in which the 
    Selenium middleware will operate on.'''
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
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
In case the code shutsdown in between the scrapping, we don't want to start from scratch.
We increment by 1 since the interface script returns an index that begins with (len(speciesDF) - 1).'''
speciesCounter = lastSpeciesChecker(speciesDF)

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
    speciesName = speciesDF.loc[speciesCounter, 'species']

    '''Using the species name to arrive at the URL to ping the browser'''
    speciesSearchURL = urlTweaker(speciesName, speciesCounter, homeURL)

    '''Invoking the search results page here using the browser'''
    browserPinger(browser, speciesSearchURL)

    '''Delaying the collection of code because the IUCN website takes time to respond to an incoming ping'''
    time.sleep(5)

    '''Extracting the HTML code'''
    htmlSearchCode = htmlExtractor(browser)

    '''Souping the HTML here to make it more readable and look for elements within'''
    searchSoup = pageSouper(htmlSearchCode)

    '''From the search result of the species we collect the URL which will direct us to the species database'''
    speciesURL = speciesURLExtractor(searchSoup, homeURL)

    '''Here, we get the page containing all the information of a specific species'''
    browserPinger(browser, speciesURL)

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
    speciesDF = threatsAndStressesPlotter(speciesDF, speciesCounter, threatsAndStresses)

    '''Scrapping the threats text box here'''
    threatsText = threatsTextsExtractor(speciesSoup)

    '''Plotting the threats text here'''
    speciesDF = threatsTextsPlotter(speciesDF, speciesCounter, threatsText)

    '''Here, we scrape the population trend of the species'''
    populationTrend = populationTrendChecker(speciesSoup)

    '''Here, we plot the population trend'''
    speciesDF = populationTrendPlotter(speciesDF, speciesCounter, populationTrend)

    '''Writing a .csv dumper here so that we can check the output after each run'''
    csvDumper(speciesFile, speciesDF)

    '''Appennding the species counter to go to the next species on the list, in case the code breaksdown prematurely'''
    speciesCounter += 1