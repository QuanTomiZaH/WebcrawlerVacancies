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

    # getting the data from the title
    try:
        # appending the role title and url
        title_text = nested_soup_string.find("h1", class_="single-vacancy__title")
        status_data.append(title_text.text.lower().strip())
        status_data.append(url)

        dd_soup = nested_soup_string.find("section", class_="single-vacancy__main")
        for dd in dd_soup.find_all("dd"):

            # if there is a clausule that show how many days are left, remove this from the string"
            if dd.find("span", class_="days") in dd:
                removedd = dd.find("span", class_="days").text.lower().strip()
                dd = dd.text.lower().strip()
                dd = dd[:len(removedd)].strip()
                status_data.append(dd)
            else:
                status_data.append(dd.text.lower().strip())
                continue

    except AttributeError:
        print(url + "; This HTML is not found")
        return

        #time = re.search("end(.*)end", hours_worked)
        #print(time.group(1))

        # print(hours_worked)
        # print(hours_worked)

        # text_section = nested_soup_string.find_all("section", class_="content__main editor")
        # for hours in text_section:
        # print(hours)
        # hours = str(hours)
        # print(hours)

        # string = re.findall("</h2>.*<h2>", hours)
        # print(string)
        # hours_per_week = hours.find_all("h2")
        # print(hours_per_week)


    except AttributeError:
        print(url + "; This HTML is not found")
        print("testing123")
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
    # totaldf.to_csv("werkeningelderlandScrapingOutput.csv", encoding='utf-8')
    # print("Created a CSV file on the local file location")


# excecute the program
if __name__ == '__main__':
    main()
