# import all libraries
from bs4 import BeautifulSoup
import pandas as pd
import re
import requests


# A function to create a dynamic soup so it can be used in loops
def create_soup(pageresponse_html):
    soup = BeautifulSoup(pageresponse_html.text, "html.parser")
    return soup


# the function to create the URL list from which information should be pulled
def create_url_list():
    local_url_list = []

    # find the starting page URL(number) of the newest vacancy on the website
    # this does not yet loop trough multiple pages
    # given that there are not a lot of pages to scan this will not show up as a problem anytime soon
    # this should be fixed though
    opdrachten_page_url = "<addurl>"
    soup = create_soup(requests.get(opdrachten_page_url)).findAll("a", href=re.compile("/opdracht/.*"))
    for links in soup:
        local_url_list.append(links.get("href"))

    return local_url_list


def find_information(url):
    # print("Getting page: " + url)

    # create a local dataframe so we can return the line later
    localdf = pd.DataFrame()
    status_data = []

    try:
        nested_soup_string = create_soup(requests.get(url))

    except:
        print("Connecting to page: " + url + " has failed")
        print("Trying again")
        find_information(url)
        return

    # append the data
    try:

        # getting all the info in the top white info box
        for data in nested_soup_string.find_all("div", attrs={"class": "box color4"}):

            for title in data.find_all("h1"):
                status_data.append(title.text.lower().strip())

            status_data.append(url)
            for info in data.find_all("p"):
                status_data.append(info.text.lower().strip())

            # getting the planninginformation of the vacancy

        for table in nested_soup_string.find_all("table", attrs={"class": "table table-striped"}):
            planning_list = table.find_all("td", class_="bold")

            for td in table.find_all("td"):
                if td not in planning_list:
                    status_data.append(td.text.lower().strip())

        # getting the text from the vacancy
        # this website is complete crap. We will have to look at this later
        # for description in nested_soup_string.find_all("div", attrs={"class": "text color4"}):
        #    for div in description.find_all("div"):
        #       for p in div.find_all("p"):

        print(status_data)
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
    # define the dataframe
    totaldf = pd.DataFrame()

    # Pointing to the webdriver and inserting the URL
    url_list = create_url_list()
    print(url_list)

    # no multiprocessing for this page as there are not enough vacancies to make this efficiënt
    for urlname in url_list:
        totaldf = totaldf.append(find_information(urlname))
        print("Adding a row, total pages added: " + str(url_list.index(urlname) + 1))

    # creating the csv
    print(totaldf)
    totaldf.to_csv("werkeninfrieslandScrapingOutput.csv", encoding='utf-8')
    print("Created a CSV file on the local file location")


# excecute the program
if __name__ == '__main__':
    main()
