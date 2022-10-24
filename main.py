from typing import List
from bs4 import BeautifulSoup, ResultSet
import requests
import pandas as pd
from datetime import datetime

def GIS_subpages_number(main_page):
    """This function retrieves the number of subpages from GIS webpage."""
    r = requests.get(main_page)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, "html.parser")
    test = soup.find(class_="pagination__total-count")
    tag = test.contents[0] #tag’s children are available in a list called .contents
    tag_int = int(tag)
    return tag_int

def GIS_subpages_list(tag_int):
    """Creates a full list of all subpages."""
    list_init = list(range(1, tag_int + 1))
    list_subpages = []
    for number in list_init:
        list_subpages.append(str("https://www.gov.pl/web/gis/ostrzezenia?page=" + str(number) + "&size=10"))

    return list_subpages

def GIS_Dataframe(links):
    """Creates dataframe from all available GIS data. It creates 3 columns - DATE , TITLE and LINK to subpage with each warning description."""
    warning_title_ALL = []
    warning_data_ALL = []
    warning_link_ALL = []

    for link in links:
        r = requests.get(link)
        html_doc = r.text
        soup = BeautifulSoup(html_doc, features="html.parser")

        # Using CSS selectors to locate elements
        for title in soup.select('div.title'):
             warning_title_ALL.append(title.get_text())
        for data in soup.select('span.date'):
            warning_data_ALL.append(data.get_text())

        # Retrieving the side page links
        side_page_blocks_ALL = soup.find("div", class_="art-prev art-prev--near-menu")
        for link in side_page_blocks_ALL.find_all('a', href=True):
            warning_link_ALL.append(link['href'])

    # Zipping lists, with columns specified + correcting the data format
    gis_data_ALL = pd.DataFrame(list(zip(warning_title_ALL, warning_data_ALL, warning_link_ALL)),
                                columns=['TITLE', 'DATE', 'LINK'])
    gis_data_ALL['DATE'] = gis_data_ALL['DATE'].str.replace('\n', '')
    gis_data_ALL['TITLE'] = gis_data_ALL['TITLE'].str.replace('Ostrzeżenie publiczne dotyczące żywności: ', '')
    append_str = "https://www.gov.pl"
    gis_data_ALL['LINK'] = [append_str + sub for sub in gis_data_ALL['LINK']]

    return gis_data_ALL

main_page = 'https://www.gov.pl/web/gis/ostrzezenia?page=1&size=10'
tag = GIS_subpages_number(main_page)
links = GIS_subpages_list(tag)
df = GIS_Dataframe(links)

print(df)
