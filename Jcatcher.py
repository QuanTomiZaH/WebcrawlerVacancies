# import all libraries
from selenium import webdriver
from bs4 import BeautifulSoup
from multiprocessing import Pool
import pandas as pd
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = webdriver.Chrome("C:\Chromedriver\chromedriver.exe")


# the function to create the URL list from which information should be pulled
def create_url_list():
    local_url_list = []

    # For now the below variable has to be edited to add how many vacancies you want to check
    input_vacancies_amount = 1000
    starting_page_number = 0

    # find the starting page URL(number) of the newest vacancy on the website
    opdrachten_page_url = "<addurl>"
    browser.get(opdrachten_page_url)
    WebDriverWait(browser, 20).until(EC.presence_of_element_located(
        (By.XPATH, '/html/body/form/div[3]/div[1]/div/div/div[1]/div/section/div[1]')))
    starting_page_numbers = create_soup(browser).findAll("a", href=re.compile("functienaam.*"))

    # loop to find the highest vacancy number on the front page of the website, so we get the most recent created
    for number in starting_page_numbers:
        number = int(re.search(r'\d+', number.get("href")).group())
        if number > starting_page_number:
            starting_page_number = number

    # make a list to create the URLs
    while input_vacancies_amount > 0:
        local_url_list.append("<addurl>" + str(starting_page_number))
        starting_page_number -= 1
        input_vacancies_amount -= 1
    return local_url_list


# A function to create a dynamic soup so it can be used in loops
def create_soup(pageresponse_html):
    soup = BeautifulSoup(pageresponse_html.page_source, "html.parser")
    return soup


# find the text from the html page
def find_information(url):
    print("Getting web page: " + url)
    localdf = pd.DataFrame()

    # get html and parsing the data
    # in case the webserver does not respond fast enough
    try:
        browser.get(url)
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="request"]/table[1]/tbody/tr[1]/td[2]')))

        browser.find_element_by_xpath('//*[@id="request"]/table[1]/tbody/tr[1]/td[2]')
        WebDriverWait(browser, 20).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="requestHeader"]/div/h1')))

        element_2 = browser.find_element_by_xpath('//*[@id="requestHeader"]/div/h1')
        print("Found a vacancy for " + element_2.text)

        nested_soup_string = create_soup(browser)
    except:
        print("Connecting to page: " + url + " has failed, loading the next vacany in the sequence")
        return

    # creating the variables
    status_data = []
    # can be substituted by pointing to a certing file
    property_options = ["rol", "werkniveau", "klant", "locatie", "startdatum", "einddatum",
                        "aantal uren per week", "publicatiedatum", "aanvrager",
                        "uiterste aanbiedingsdatum", "deze vacature sluit over"]
    try:
        title_data_in_soup = nested_soup_string.find("h1", attrs={"class": "text-center ng-binding"}).text.strip()
        status_data.append(str(title_data_in_soup))
        status_data.append(str(url))
        for properties in nested_soup_string.findAll("table", attrs={"class": "table table-inline"}):
            for td in properties.findAll("td"):
                td = td.text.lower().strip()
                if td not in property_options:
                    status_data.append(td)

    except AttributeError:
        print("error")

    # appending and transposing the dataframe
    df = pd.DataFrame(status_data)
    df = pd.DataFrame.transpose(df)
    localdf = localdf.append(df, ignore_index=True)

    return localdf


# the main sequence to enact
def main():
    # define the dataframe
    totaldf = pd.DataFrame()

    # Pointing to the webdriver and inserting the URL
    url_list = create_url_list()
    print(url_list)

    # multiprocessing
    poolworkers = Pool(4)
    totaldf = totaldf.append(poolworkers.map(find_information, url_list))

    # creating the csv
    print(totaldf)
    totaldf.to_csv("JobcatcherScrapingOutput.csv", encoding='utf-8')
    print("Created a CSV file on the local file location")


# excecute the program
if __name__ == '__main__':
    main()
