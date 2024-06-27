import requests
from bs4 import BeautifulSoup as bs
import regex as re
import csv
from typing import List, Dict
import jsonlines

page1 = 'https://www.immoweb.be/en/search/house/for-sale?countries=BE&page=1&orderBy=relevance'

headers = { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

response = requests.get(page1, headers=headers)
soup_tomato = bs(response.content, 'html.parser')

def get_price(headers: dict[str]) -> str:
    url = 'https://www.immoweb.be/en/classified/house/for-sale/mechelen/2800/11486576'

    response = requests.get(url, headers=headers)
    soup = bs(response.content, 'html.parser')

    price = soup.find('span', class_='sr-only').text
    return price


def get_link(url: str, headers: dict[str], soup: bs) -> str:
        
    link = soup.find('a', class_="card__title-link")
    return link['href']


def get_code(url: str, headers: dict[str]) -> int:
    pattern = r"[0-9]{4}"
        
    headers = { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    code = bs.find('p', class_="card__information--locality").text
    
    code_num = re.search(pattern, code)        
    return code_num.group(0)


with open('data_set.csv', 'w', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Locality', 'Type of property', 'Subtype of property', 'Price', 'Type of sale', 'Number of rooms', 'Living Area (m²)', 'Fully equipped kitchen', 'Furnished', 'Open fire', 'Terrace', 'Garden', 'Surface of the plot (m²)', 'Number of facades', 'Swimming pool', 'State of the building'])
        
'''with open('soup.html', 'w') as html:
   html.write(str(soup))'''


#  ***********************
#  ** window.classified **
#  ***********************


def save_init_dic_building(
        locality: List[str], 
        type_and_subtype_of_property: List[str|None], 
        price: int, 
        type_of_sale: str,
        other: Dict[str, int|bool|None|str],
        state_of_the_building: str,
        link_save: str
        ) -> None:

    property_example = {
        "Locality": locality,
        "Type of property": type_and_subtype_of_property[0],
        "Subtype of property": type_and_subtype_of_property[1],
        "Price": price,
        "Type of sale": type_of_sale,
        "Bedrooms": None,
        "Living area": None,
        "Kitchen type": None,
        "Furnished": None,
        "How many fireplaces?": None,
        "Terrace surface": None,
        "Garden surface": None,
        "Surface of the plot": None,
        "Number of frontages": None,
        "Swimming pool": None,
        "State of the building": state_of_the_building
    }

    for key, value in other.items():
        property_example[key] = value

    with jsonlines.open(link_save, mode='a') as writer:
        writer.write(property_example)

def get_type_and_subtype_of_property(soup, dic_flitre: Dict[str, List[str]]) -> List[str | None]:
    h1_title = soup.find('h1', class_='classified__title')
  
    if not h1_title:
        return [None, None]
    
    full_title = h1_title.text.strip()
    first_word = full_title.split()[0] if full_title else ""

    for j, i in dic_flitre.items():
        if first_word in i:
            return [j, first_word]
    
    return [None, None]

def extract_number(value: str) -> float | str:
    match = re.search(r'(\d+)', value)
    if match:
        return int(match.group(1))
    return value

def get_other_info(soup) -> Dict[str, str|int|None|bool]:
    property_other = {
        "Bedrooms": 0,
        "Living area": 0,
        "Kitchen type": False,  # Installed
        "Furnished": False,
        "How many fireplaces?": None,
        "Terrace surface": {
            "Present": False,
            "Area": None
        },
        "Garden surface": {
            "Present": False,
            "Area": None
        },
        "Surface of the plot": None,
        "Number of frontages": 1,
        "Swimming pool": False,
    }

    all_info = soup.find_all('div', class_='text-block')
    all_info.extend(soup.find_all('div', class_='accordion__content'))

    for i in all_info:
        headers = i.find_all('th', class_='classified-table__header') 

        data = i.find_all('td', class_='classified-table__data')

        for th, td in zip(headers, data):
            key = re.sub('<[^<]+?>', '', str(th))  
            key = re.sub('\s+', ' ', key).strip()

            value = re.sub('<[^<]+?>', '', str(td)) 
            value = re.sub('\s+', ' ', value).strip()

            if key in property_other:

                if key == "Terrace surface":
                    property_other["Terrace surface"]["Area"] = extract_number(value)
                    property_other["Terrace surface"]["Present"] = True

                elif key == "Garden surface":
                    property_other["Garden surface"]["Area"] = extract_number(value)
                    property_other["Garden surface"]["Present"] = True
                
                else:
                    if key == "Kitchen type":
                        value = (True if value == "Installed" else False)
                    
                    elif value == "Yes":
                        value = True

                    elif value == "No":
                        value = False
                        
                    property_other[key] = value if type(value) == bool else extract_number(value)     

    return property_other

def scrap(localite_cp:List[str], price:int, url:str) -> None:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, comme Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }   
        
    link = requests.get(url, headers=headers)
    with requests.Session() as session:
        soup = bs(link.content, 'html.parser')
        other = get_other_info(soup)
        #save_init_dic_building(localite_cp, get_type_and_subtype_of_property(soup, [None]), price, "None", other, "None", "../Data/all.json")
        save_init_dic_building(localite_cp, "None", price, "None", other, "None", "../Data/all.json")

if __name__ == "__main__":

    '''headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, comme Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }   

    for i in range(50):
        print(i)
        link = requests.get(f'https://www.immoweb.be/en/search/house/for-sale?countries=BE&page={i}&orderBy=relevance', headers=headers)
        soup = bs(link.content, 'html.parser')
        page_link = soup.find_all('a', class_= 'card__title-link')

        for l in page_link:
            scrap([], 0, l.get("href"))'''
    print(get_price())


