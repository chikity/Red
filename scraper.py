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
    speciesThreatsAndStressesTruncated = []
    threatsAndStressesColumnsTruncated = []
    threatsAndStresses= []
    commonThreats = []
    '''If threats are returned from the main script, enter this loop'''
    if(speciesThreatsAndStresses):
        for speciesThreatsAndStress in speciesThreatsAndStresses:
            if(len(speciesThreatsAndStress.split(" "))>1):
                '''Only if a stress has a numerical and an accompanying phrase, split it for truncation'''
                speciesThreatsAndStressesTruncated.append(speciesThreatsAndStress.split(" ")[0]+" "+speciesThreatsAndStress.split(" ")[1])
        for threatsAndStressesColumn in threatsAndStressesColumns:
            if(len(threatsAndStressesColumn.split(" "))>1):
                '''Truncating and storing the column members here as wells'''
                threatsAndStressesColumnsTruncated.append(threatsAndStressesColumn.split(" ")[0]+" "+threatsAndStressesColumn.split(" ")[1])
            else:
                '''This loop is required to ensure indices are consistent between the truncated column and the main column below'''
                threatsAndStressesColumnsTruncated.append(threatsAndStressesColumn)
        '''Here, we check common elements between the truncated threats and column'''
        commonThreats = list(set(threatsAndStressesColumnsTruncated).intersection(set(speciesThreatsAndStressesTruncated)))
        for commonThreat in commonThreats:
            '''Appending a new list and sending it over to the main code after checking indices between truncated column and stresses'''
            threatsAndStresses.append(threatsAndStressesColumns[threatsAndStressesColumnsTruncated.index(commonThreat)])
        '''Returning the detected stresses'''
        return threatsAndStresses
    else:
        return []

def threatsAndStressesPlotter(speciesDF, speciesCounter, threatsAndStresses):
    '''Finally! We plot the threats and stresses observed on the dataframe for the corresponding species and column'''
    for threatsAndStress in threatsAndStresses:
        speciesDF.loc[speciesCounter, threatsAndStress] = 1
    return speciesDF

def assessmentChecker(speciesSoup):
    '''This function checks the assessment status of the given species and returns it to the main function'''
    assessmentInformation = (speciesSoup.find('a', {'href':'/search?redListCategory=ex&searchType=species'}) or speciesSoup.find('a', {'href':'/search?redListCategory=ew&searchType=species'}) or speciesSoup.find('a', {'href':'/search?redListCategory=re&searchType=species'}) or speciesSoup.find('a', {'href':'/search?redListCategory=cr&searchType=species'}) or speciesSoup.find('a', {'href':'/search?redListCategory=en&searchType=species'}) or speciesSoup.find('a', {'href':'/search?redListCategory=vu&searchType=species'}) or speciesSoup.find('a', {'href':'/search?redListCategory=lr&searchType=species'}) or speciesSoup.find('a', {'href':'/search?redListCategory=nt&searchType=species'}) or speciesSoup.find('a', {'href':'/search?redListCategory=lc&searchType=species'}) or speciesSoup.find('a', {'href':'/search?redListCategory=dd&searchType=species'}) or speciesSoup.find('a', {'href':'/search?redListCategory=na&searchType=species'}))
    if(assessmentInformation):
        return assessmentInformation.text
    else:
        return 'Data Deficient'

def assessmentPlotter(speciesDF, speciesCounter, assessmentInformation):
    '''This function plots the assessment information on the speciesDF'''
    if((assessmentInformation.split(" ")[0].lower()[:2] == 'ex') and (len(assessmentInformation.split(" "))>1)):
        speciesDF.loc[speciesCounter, 'ew'] = 1
    else:
        speciesDF.loc[speciesCounter, assessmentInformation.split(" ")[0].lower()[:2]] = 1
    return speciesDF

def habitatSystemChecker(speciesSoup):
    '''This function scrapes the habitat system of the species. Any combination of the three: 1. Terrestrial, 2. Marine, 3. Freshwater'''
    habitatTags = ['/search?systems=0&searchType=species', '/search?systems=1&searchType=species', '/search?systems=2&searchType=species']
    habitats = []
    for habitatTag in habitatTags:
        '''We use this loop to collect the habitat tags of a given species.
        We check if the species possess a possible tag and append the list of habitats to be returned.'''
        if(speciesSoup.find('a', {'href':habitatTag})):
            habitats.append(speciesSoup.find('a', {'href':habitatTag}).text)
    return habitats

def habitatSystemPlotter(speciesDF, speciesCounter, habitats):
    '''Plotting the species habitat system of the species on the dataframe'''
    for habitat in habitats:
        speciesDF.loc[speciesCounter, habitat.lower()] = 1
    return speciesDF

def generationLineChecker(speciesSoup):
    '''This function checks if the species has a generation line specified'''
    generationLine = "None"
    '''This is the standard form of the p element that holds the generationLine data'''
    preGenerationLines = speciesSoup.findAll('p', {'class':'card__data card__data--std card__data--accent'})
    for preGenerationLine in preGenerationLines:
        '''We cycle through each of the cookie-cutter p elements returned and look for the one with the generation line by checking if it has the string 'years' in it'''
        if('years' in preGenerationLine.text):
            generationLine = preGenerationLine.text
    return generationLine

def generationLinePlotter(speciesDF, speciesCounter, generationLine):
    '''We plot the generation line data in the 'generation' column of the speciesDF'''
    speciesDF.loc[speciesCounter, 'generation'] = generationLine
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

    '''Here, we plot the population trend on the dataframe'''
    speciesDF = populationTrendPlotter(speciesDF, speciesCounter, populationTrend)

    '''Here, we grab the habitat information of the species'''
    habitats = habitatSystemChecker(speciesSoup)

    '''We take the habitat(s) and plot it on the dataframe'''
    speciesDF = habitatSystemPlotter(speciesDF, speciesCounter, habitats)

    '''Here, we scrape the generation line of each species'''
    generationLine = generationLineChecker(speciesSoup)

    '''Here, we plot the the generationLine of each species onto the dataframe'''
    speciesDF = generationLinePlotter(speciesDF, speciesCounter, generationLine)

    '''Here, we scrape the assessment information of the species'''
    assessmentInformation = assessmentChecker(speciesSoup)

    '''Here, we plot the assessment information on the dataframe'''
    speciesDF = assessmentPlotter(speciesDF, speciesCounter, assessmentInformation)

    '''Writing a .csv dumper here so that we can check the output after each run'''
    csvDumper(speciesFile, speciesDF)

    '''Appennding the species counter to go to the next species on the list, in case the code breaksdown prematurely'''
    speciesCounter += 1