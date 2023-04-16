from bs4 import BeautifulSoup
import requests
import re
from tqdm.auto import tqdm


def get_items(product):
    url = f"https://www.newegg.com/p/pl?d={product}&N=4131"
    page = requests.get(url).text
    doc = BeautifulSoup(page, "html.parser")

    page_text = doc.find(class_="list-tool-pagination-text").strong.text
    pages = int(str(page_text).split("/")[-1])

    items_found = {}


    for page in tqdm(range(1, pages + 1)):
        url = f"https://www.newegg.com/p/pl?d={product}&N=4131&page={page}"
        page = requests.get(url).text
        doc = BeautifulSoup(page, "html.parser")

        div = doc.find(class_="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell")
        items = div.find_all(string=re.compile(product))

        for item in items:
            try:
                parent = item.parent
                if parent.name != "a":
                    continue

                link = parent["href"]
                next_parent = item.find_parent(class_='item-container')
                price = next_parent.find(class_="price-current").strong.string

                items_found[item] = {'price': int(price.replace(',', '')), 'link': link}

            except:
                pass

    sorted_items = sorted(items_found.items(), key=lambda x: x[1]['price'])

    new_list = []

    for item in sorted_items[0:10]:
        new_list.append([item[0], item[1]['price'], item[1]['link']])

    return new_list
