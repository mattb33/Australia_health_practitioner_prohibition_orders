# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import scraperwiki
# import lxml.html
#
# # Read in a page
# html = scraperwiki.scrape("http://foo.com")
#
# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library
# scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries.
# You can use whatever libraries you want: https://morph.io/documentation/python
# All that matters is that your final data is written to an SQLite database
# called "data.sqlite" in the current working directory which has at least a table
# called "data".

#######  SETUP   ############

# Import required modules
import requests
import csv
from bs4 import BeautifulSoup
import datetime

## URLs
urlSA = 'http://www.hcscc.sa.gov.au/orders-issued-code-conduct-unregistered-health-practitioners/'
urlNSW = ['http://www.hccc.nsw.gov.au/Hearings---decisions/Register-of-Prohibition-Orders-in-Force/List-of-Prohibition-Orders-in-Force', 'http://www.hccc.nsw.gov.au/Hearings---decisions/Register-of-Prohibition-Orders-in-Force/List-of-Prohibition-Orders-in-Force?retain=true&PagingModule=2615&Pg=2', 'http://www.hccc.nsw.gov.au/Hearings---decisions/Register-of-Prohibition-Orders-in-Force/List-of-Prohibition-Orders-in-Force?retain=true&PagingModule=2615&Pg=3', 'http://www.hccc.nsw.gov.au/Hearings---decisions/Register-of-Prohibition-Orders-in-Force/List-of-Prohibition-Orders-in-Force?retain=true&PagingModule=2615&Pg=4']
urlQLD = 'https://www.oho.qld.gov.au/news-updates/immediate-actions/prohibition-orders/'
urlVIC = 'https://hcc.vic.gov.au/prohibition-orders-warnings/prohibition-orders?page={}'


# Initialise lists
output = []

# Set today's date as variable to add to output
now = datetime.datetime.now()
scrape_date = now.strftime("%Y-%m-%d %H:%M")

#Define header for csv
header = ['state', 'date', 'name', 'practitionerType', 'orderDetails', 'orderType', 'lastCheckDate']

########## START OF QLD PROCESS #################

# Get website data
dataQLD = requests.get(urlQLD)

# parse the html using beautiful soup and store in variable `soup`
soupQLD = BeautifulSoup(dataQLD.text, 'html.parser')

# Identify table with data we want
myTableQLD = soupQLD.find('tbody')

# Iterate through each row
for tr in myTableQLD.find_all('tr'):
    date = tr.find_all('td')[0].text.strip()
    name = tr.find_all('td')[1].text.strip().replace("Mr ", "").replace("Mrs ", "").replace("Ms ", "").replace("Miss ", "").replace("Dr ", "")
    practitionerType = tr.find_all('td')[2].text.strip()
    orderDetails = tr.find_all('td')[3].text.strip()
    orderType = tr.find_all('td')[4].text.strip()
    state = 'QLD'
    lastCheckDate = scrape_date
    output.append([state, date, name, practitionerType, orderDetails, orderType, lastCheckDate])

# Test output
print('QLD - data gathered')

########### QLD complete #################

########### START OF VIC PROCESS #################

# Deal with pagination - increment page numbers
range_page_url = [urlVIC.format(i) for i in range(0,12)]

for range in range_page_url:
    r = requests.get(range)
    soupVIC = BeautifulSoup(r.text, 'lxml')
    for tr in soupVIC.table.find_all('tr')[1:-1]:
        date = [span.text for span in tr.find_all('span')]
        name = [strong.text.replace("Mr ", "").replace("Mrs ", "").replace("Ms ", "").replace("Miss ", "").replace("Dr ", "") for strong in tr.find_all('strong')]
        practitionerType = [strong.next_sibling for strong in tr.find_all('strong')]
        orderDetails = "view web page"
        orderType = "-"
        state = 'VIC'
        lastCheckDate = scrape_date
        output.append([state, date, name, practitionerType, orderDetails, orderType, lastCheckDate])

# Test output
print('VIC - data gathered')

########### VIC complete #################

########### START OF NSW PROCESS #################
# Get website data
for link in urlNSW:
    dataNSW = requests.get(link)
    # parse the html using beautiful soup and store in variable `soup`
    soupNSW = BeautifulSoup(dataNSW.text, 'html.parser')
    # Identify table with data we want
    myTableNSW = soupNSW.find('div', class_='widget')

# Iterate through each row
    for row in myTableNSW.find_all('dl'):
        date = row.find('dd').text.strip()
        name = row.find('span').text.strip().replace("Mr ", "").replace("Mrs ", "").replace("Ms ", "").replace("Miss ", "").replace("Dr ", "")
        practitionerType = 'not listed'
        orderDetails = row.find('a').get('href')
        orderType = 'not listed'
        state = 'NSW'
        lastCheckDate = scrape_date
        output.append([state, date, name, practitionerType, orderDetails, orderType, lastCheckDate])

# Test output
print('NSW - data gathered')

########### NSW complete #################


########### START OF SA PROCESS #################
# # Get website data
dataSA = requests.get(urlSA)
# parse the html using beautiful soup and store in variable `soup`
soupSA = BeautifulSoup(dataSA.text, 'html.parser')
# Identify table with data we want
myTableSA = soupSA.find('div', class_='wpb_wrapper')
#myTableSA_h2 = myTableSA.find_all('h2')

# Iterate through each row
for item in myTableSA.find_all('p', class_='margin25px'):
    date = 'view order details'
    name = item.text.replace("Mr ", "").replace("Mrs ", "").replace("Ms ", "").replace("Miss ", "").replace("Dr ", "").replace("Statement for Public Release","")
    practitionerType = 'not listed'
    orderDetails = 'not listed'
    orderType = 'not listed'
    state = 'SA'
    lastCheckDate = scrape_date
    output.append([state, date, name, practitionerType, orderDetails, orderType, lastCheckDate])


print('SA - data gathered')

########### SA complete #################



print("Here's an example of the output being written to CSV:")
print(output[0:2])

#########  Write all to CSV   ##########
print('writing to CSV...')

with open('prohibition_orders.csv', mode='w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(i for i in header)

    # Add scraped data to csv file
    for item in output:
        writer.writerow(item)

print('Writing to CSV complete')
