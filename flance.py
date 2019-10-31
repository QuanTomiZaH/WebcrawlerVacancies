# import all libraries
from bs4 import BeautifulSoup
from multiprocessing import Pool
from time import time
import requests
import pandas as pd
import re

ts = time()


# the function to create the URL list from which information should be pulled
def create_url_list():
    local_url_list = []

    # For now the below variable has to be edited to add how many vacancies you want to check
    input_vacancies_amount = 200

    # find the starting page URL(number) of the newest vacancy on the website
    opdrachten_page_url = "<addurl>"
    starting_page_number = 0
    starting_page_numbers = \
        create_soup(requests.get(opdrachten_page_url)).findAll("a", href=re.compile("/opdracht/.*"))

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
    soup = BeautifulSoup(pageresponse_html.text, "html.parser")
    return soup


# send only the total url linst(len) also only send one URL.
def find_information(url):
    print("Getting page: " + url)

    # create a local dataframe so we can return the line later
    localdf = pd.DataFrame()

    # create a list that will be filled and put into a function to enter a dataframe
    # be careful, at this time the program will continue infinitally unless.
    # if the website blocks access this program will keep querying
    # create a timout system in the exceptionerror or something (if time = X then Y ifelse start timer ifelse try again)
    status_data = []
    try:
        nested_soup_string = create_soup(requests.get(url))
    except:
        print("Connecting to page: " + url + " has failed")
        print("Trying again")
        find_information(url)
        return

    property_options = ["status", "publicatiedatum", "eindklant", "weergaven", "reacties", "referentie",
                        "inschrijven voor", "op locatie", "startdatum",
                        "looptijd", "fte (in %)", "tarief", "contract"]

    # append the data
    try:
        title_data_in_soup = nested_soup_string.find("div", attrs={"class": "head"}).text.strip()
        status_data.append(str(title_data_in_soup))
        status_data.append(str(url))

        # Check all the different modules and find the correct "value" within the Html
        # Append this to the dataframe
        for properties in nested_soup_string.find_all("div", class_="properties projectdetails"):
            name_list = []
            value_list = []
            counter = 0

            for span in properties.find_all("span", class_="name"):
                name_list.append(span.text.lower().strip())

            for span in properties.find_all("span", class_="value"):
                value_list.append(span.text.lower().strip())

            for option in property_options:
                if option in name_list:
                    status_data.append(value_list[counter])
                    counter += 1
                else:
                    status_data.append(" ")

    except AttributeError:
        print(url + "; This page is not found")
        return

    # appending and transposing the dataframe
    df = pd.DataFrame(status_data)
    df = pd.DataFrame.transpose(df)
    localdf = localdf.append(df, ignore_index=True)

    return localdf


# the main sequence to enact
def main():
    # start a timer and create a dataframe
    totaldf = pd.DataFrame()

    print("Checking the newest vacancy and creating an URL list")
    urllist = create_url_list()
    print(urllist)

    # multiprocessing
    # need to add a counter that logs what amount of pages have been added thus far
    poolworkers = Pool(8)
    totaldf = totaldf.append(poolworkers.map(find_information, urllist))
    print("Found all the information")

    # create the csv
    print(totaldf)
    totaldf.to_csv("FreelanceScrapingOutput.csv", encoding='utf-8')
    print("Created a CSV file on the local file location")

    # giving feedback about the total time of this script
    print("This script took the following amount of seconds to complete:")
    print(time() - ts)


# excecute the program
if __name__ == '__main__':
    main()
