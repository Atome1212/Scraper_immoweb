import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from typing import List, Dict
import os


def price(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = bs(response.content, 'html.parser')
    price = soup.find('span', class_='sr-only').text
    return price

def get_link() -> str:
    url = 'https://www.immoweb.be/en/search/house/for-sale?countries=BE&page=1&orderBy=relevance'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = bs(response.content, 'html.parser')
    link = soup.find('a', class_="card__title-link")
    return link['href']

def get_code() -> str:
    pattern = r"[0-9]{4}"
    url = 'https://www.immoweb.be/en/search/house/for-sale?countries=BE&page=1&orderBy=relevance'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = bs(response.content, 'html.parser')
    code = soup.find('p', class_="card__information--locality").text
    code_num = re.search(pattern, code)
    return code_num.group(0)

def save_init_dic_building(
        locality: List[str],
        type_and_subtype_of_property: List[str | None],
        price: int,
        type_of_sale: str,
        other: Dict[str, int | bool | None | str],
        state_of_the_building: str,
        link_save: str
) -> None:
    # Initialiser les nouvelles données
    new_data = {
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
    
    # Mettre à jour avec les valeurs de 'other' si elles sont fournies
    for key in other:
        if key in new_data:
            new_data[key] = other[key]
        else:
            new_data[key] = other[key]
    
    # Convertir les nouvelles données en DataFrame
    new_df = pd.DataFrame([new_data])
    
    # Lire le fichier Excel existant ou créer un nouveau DataFrame
    if os.path.exists(link_save):
        df = pd.read_excel(link_save)
        # Nettoyer le DataFrame existant pour exclure les colonnes vides ou toutes NA
        df_cleaned = df.dropna(axis=1, how='all')
        # Nettoyer le DataFrame des nouvelles données pour exclure les colonnes vides ou toutes NA
        new_df_cleaned = new_df.dropna(axis=1, how='all')
        # Concaténer les DataFrames nettoyés
        df_combined = pd.concat([df_cleaned, new_df_cleaned], ignore_index=True)
    else:
        df_combined = new_df
    
    # Sauvegarder le DataFrame mis à jour dans le fichier Excel
    df_combined.to_excel(link_save, index=False)

def get_type_and_subtype_of_property(soup, dic_filter: Dict[str, List[str]]) -> List[str | None]:
    h1_title = soup.find('h1', class_='classified__title')
    if not h1_title:
        return [None, None]
    full_title = h1_title.text.strip()
    first_word = full_title.split()[0] if full_title else ""
    for j, i in dic_filter.items():
        if first_word in i:
            return [j, first_word]
    return [None, None]

def extract_number(value: str) -> float | str:
    match = re.search(r'(\d+)', value)
    if match:
        return int(match.group(1))
    return value

def get_other_info(soup) -> Dict[str, str | int | None | bool]:
    property_other = {
        "Bedrooms": 0,
        "Living area": 0,
        "Kitchen type": False,
        "Furnished": False,
        "How many fireplaces?": None,
        "Terrace surface": {"Present": False, "Area": None},
        "Garden surface": {"Present": False, "Area": None},
        "Surface of the plot": None,
        "Number of frontages": 1,
        "Swimming pool": False,
    }

    all_info = soup.find_all('div', class_='text-block') + soup.find_all('div', class_='accordion__content')
    for i in all_info:
        headers = i.find_all('th', class_='classified-table__header')
        data = i.find_all('td', class_='classified-table__data')
        for th, td in zip(headers, data):
            key = re.sub('<[^<]+?>', '', str(th)).strip()
            value = re.sub('<[^<]+?>', '', str(td)).strip()
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

def scrap(localite_cp: List[str], price: int, url: str) -> None:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, comme Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    link = requests.get(url, headers=headers)
    soup = bs(link.content, 'html.parser')
    other = get_other_info(soup)
    save_init_dic_building(localite_cp, [None, None], price, "None", other, "None", "all.xlsx")

if __name__ == "__main__":
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, comme Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for i in range(50):
        print(i)
        link = requests.get(f'https://www.immoweb.be/en/search/house/for-sale?countries=BE&page={i}&orderBy=relevance', headers=headers)
        soup = bs(link.content, 'html.parser')
        page_links = soup.find_all('a', class_='card__title-link')
        for l in page_links:
            print(l.get("href"))
            scrap([], 0, l.get("href"))
