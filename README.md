# Red

:warning: Code is buggy :warning:

## 1.0 Introduction

+ The aim of the project is to analyze corelations between the threat status of a particular species tracked on the [IUCN Red List](https://www.iucnredlist.org/ "IUCN Red List"), and their threats and stresses.

+ This repository is dedicated to the scrapping of the necessary datafields from the [IUCN Red List](https://www.iucnredlist.org/ "IUCN Red List") to prove such corelations.

+ This project is a collaboration with [Uttara Mendiratta](https://www.researchgate.net/profile/Uttara_Mendiratta "Uttara") and [Anand M Ossuri](https://www.ncf-india.org/author/675623/anand-osuri-2 "Anand") from the [Nature Conservation Foundation, India](http://ncf-india.org/ "NCF-India").

## 2.0 Model Overview

+ The model is made of two components: 1. [```interface.py```](https://github.com/SarthakJShetty/Red/tree/master/interface.py) and 2. [```scraper.py```](https://github.com/SarthakJShetty/Red/tree/master/scraper.py).

+ Disk write/read operations are handled by the ```interface.py``` code.

+ The ```scraper.py``` pipeline collects the prescribed ```HTML``` tags from the website queried and updates a ```pandas``` dataframe with the information.

+ The ```pandas``` dataframe is saved to the disc by the ```interface.py``` code after each run.

+ The ```speciesCounter()``` in the ```scraper.py``` script returns the ```sno``` of the last species that missing the ```stable```, ```unknown``` or ```decline``` population trend tags, which all scrapped species must have.