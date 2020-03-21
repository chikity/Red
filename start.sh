: 'This script is designed to loop through the scraper code over and over again in case the code exits due to a faulty Chrome instance
or delay in souping the page

-Sarthak
(23/02/2020)'

while :
    do
        python3 scraper.py
	pkill chrome
done
