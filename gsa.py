import requests
import bs4
import csv
import webbrowser
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


# Chrome.
webdriverPath = '/Users/mwilliams/Desktop/gsa/chromedriver'
driver = webdriver.Chrome(webdriverPath)


def check_tag_exists(name):
    try:
        driver.find_elements_by_tag_name(name)
    except NoSuchElementException:
        return False
    return True


def check_xpath_exists(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


# Grab the initial GSA site cookie so we can use the search.
driver.get('https://www.gsaadvantage.gov')


# Read from the lsit of product id's provided.
mftrNumCsv = open('tony-export.csv')
mftrNumReader = csv.reader(mftrNumCsv, delimiter=',')
mftrNums = list(mftrNumReader)

# Setup to write to a new csv file
outputfile = open('productNumbers.csv', 'w', newline='')
outputwriter = csv.writer(outputfile)


# For each product row in the CSV
for product in mftrNums:
    # Perform an exact search for mfr #

    print(product)

    # Our list variables
    searchList = []
    linkList = []

    # Some strings we need for later.
    blue = '../..//preceding::tr/td/a[contains(@class, "arial")]'
    green = '../..//preceding::tr/td/span/a[contains(@class, "arial")]'

    # Product numbers
    if product[0] and product[0] != 'n/a':
        prodNum = product[0]
        searchList.append(product[0])

    if product[3] and product[0] != 'n/a':
        option1 = product[3]
        searchList.append(product[3])

    if product[4] and product[0] != 'n/a':
        option2 = product[4]
        searchList.append(product[4])

    # Manufacturer numbers
    prodMan = product[1]
    prodManAbbr = product[2]

    # Lets loop through each product number
    for search in searchList:

        # Perform the search
        driver.get('https://www.gsaadvantage.gov/advantage/s/search.do?q=9,8:1' +
                   search +
                   '&q=10:1' + prodMan + '&q=1:4ADV.OFF.*&s=3&c=25&searchType=1')

        # html = driver.page_source

        myHref = 'a[contains(@class, "arial")'

        # If the search returns no results
        if check_xpath_exists("//*[contains(text(),'We found no')]") != False:
            outputwriter.writerow([search + '|' + 'No results found'])
            continue
        # If results are returned
        elif check_tag_exists('font') != False:

            # Grab the table holding search results
            searchResults = driver.find_element_by_xpath(
                "//td[@align='left']")
            myfont = driver.find_elements_by_tag_name('font')
            resultList = searchResults.find_elements_by_xpath(
                "//td[@align='left']/table[@width='100%']")

            # Loop through each result
            for i, v in enumerate(resultList):
                # print(i, v)

                # Limit results to 3 - otherwise we add a lot of run-time to the bot.. shrug..
                if i < 2:
                    try:
                        # If the product number is an exact match
                        if v.find_element_by_tag_name('font').text == search:
                            print(v.find_element_by_tag_name('font').text)
                            try:
                                # Tack it onto our linklist variable
                                linkList.append(v.find_elements_by_tag_name(
                                    'a')[0].get_attribute('href'))
                            except:
                                print(v.find_element_by_xpath(
                                    myHref).get_attribute('href'))
                    except:
                        print('failed to find font tag')
                else:
                    break

            # Join all links into a string
            joined = '`'.join(linkList)

            mystr = search + '|' + joined
            nostr = search + '|' + 'No results found.'

            # If links were found add them to the csv, otherwise say no results were found.
            if len(linkList) > 0:
                outputwriter.writerow([mystr])
            else:
                outputwriter.writerow([nostr])

print('complete')
