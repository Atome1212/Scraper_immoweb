import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from typing import List, Dict
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class ImmowebScraper:
    def __init__(self, base_url: str, headers: Dict[str, str], output_file: str, property_types: Dict[str, List[str]]):
        self.base_url = base_url
        self.headers = headers
        self.output_file = output_file
        self.property_types = property_types

    def get_price(self, url: str) -> int:
        print(f"{url}")
        response = requests.get(url, headers=self.headers)
        soup = bs(response.content, 'html.parser')
        price = soup.find('span', class_='sr-only').text
        return price

    def get_links(self, page: int) -> List[str]:
        response = requests.get(f'{self.base_url}&page={page}&orderBy=relevance', headers=self.headers)
        soup = bs(response.content, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', class_="card__title-link")]
        return links        

    def get_code(self, soup) -> str:
        pattern = r"[0-9]{4}"
        code = soup.find('p', class_="card__information--locality").text
        code_num = re.search(pattern, code)
        return code_num.group(0) if code_num else None

    def save_init_dic_building(
            self,
            locality: str,
            type_and_subtype_of_property: List[str | None],
            price: int,
            type_of_sale: str,
            other: Dict[str, int | bool | None | str],
            link_save: str
    ) -> None:
        new_data = {
            "Locality": locality,
            "Type of property": type_and_subtype_of_property[0],
            "Subtype of property": type_and_subtype_of_property[1],
            "Price": price,
            "Type of sale": type_of_sale,
            "Bedrooms": 0,
            "Living area": 0,
            "Kitchen type": None,
            "Furnished": None,
            "How many fireplaces?": 0,
            "Terrace surface": None,
            "Garden surface": None,
            "Surface of the plot": None,
            "Number of frontages": None,
            "Swimming pool": None,
            "Building condition": None
        }

        for key in other:
            if key in new_data:
                new_data[key] = other[key]
            else:
                new_data[key] = other[key]

        new_df = pd.DataFrame([new_data])

        if os.path.exists(link_save):
            df = pd.read_excel(link_save)
            df_cleaned = df.dropna(axis=1, how='all')
            new_df_cleaned = new_df.dropna(axis=1, how='all')
            df_combined = pd.concat([df_cleaned, new_df_cleaned], ignore_index=True)
        else:
            df_combined = new_df

        df_combined.to_excel(link_save, index=False)

    def get_type_and_subtype_of_property(self, soup) -> List[str | None]:
        h1_title = soup.find('h1', class_='classified__title')
        if not h1_title:
            return [None, None]
        full_title = h1_title.text.strip()
        first_word = full_title.split()[0] if full_title else ""
        
        for j, i in property_types.items():
            if first_word in i:
                return [j, first_word]
            
            if first_word == j:
                return [j, "No subtype"]
        print(first_word)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")  
        return [None, None]

    @staticmethod
    def extract_number(value: str) -> float | str:
        match = re.search(r'(\d+)', value)
        if match:
            return int(match.group(1))
        return value

    def get_other_info(self, soup) -> Dict[str, str | int | None | bool]:
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
            "Building condition": ""
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
                        property_other["Terrace surface"]["Area"] = self.extract_number(value)
                        property_other["Terrace surface"]["Present"] = True
                    elif key == "Garden surface":
                        property_other["Garden surface"]["Area"] = self.extract_number(value)
                        property_other["Garden surface"]["Present"] = True
                    else:
                        if key == "Kitchen type":
                            value = (True if value == "Installed" else False)
                        elif value == "Yes":
                            value = True
                        elif value == "No":
                            value = False
                        property_other[key] = value if type(value) == bool else self.extract_number(value)
        return property_other

    def scrap(self, localite_cp: List[str], price: int, url: str) -> None:
        link = requests.get(url, headers=self.headers)
        soup = bs(link.content, 'html.parser')

        other = self.get_other_info(soup)
        self.save_init_dic_building(localite_cp, self.get_type_and_subtype_of_property(soup), price, "None", other, self.output_file)


    def scrape_links(self, links: List[str]) -> None:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.scrap, [], self.get_price(link), link) for link in links]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"An error occurred: {e}")

    def run_scraper(self, total_pages: int, pages_per_batch: int) -> None:
        for i in range(0, total_pages, pages_per_batch):
            page_range = range(i, min(i + pages_per_batch, total_pages))
            all_links = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(self.get_links, page) for page in page_range]
                for future in as_completed(futures):
                    try:
                        all_links.extend(future.result())
                    except Exception as e:
                        print(f"An error occurred while fetching links: {e}")
            self.scrape_links(all_links)

if __name__ == "__main__":

    property_types = {
        "House": [
            "Bungalow",
            "Chalet",
            "Castle",
            "Farmhouse",
            "Country house",
            "Exceptional property",
            "Apartment block",
            "Mixed-use building",
            "Town-house",
            "Mansion",
            "Villa",
            "Mixed-use"
        ],
        "Apartment": [
            "Ground floor",
            "Duplex",
            "Triplex",
            "Studio",
            "Penthouse",
            "Loft",
            "Kot",
            "Service flat"
        ],
        "New House": [
            "Bungalow",
            "Chalet",
            "Castle",
            "Farmhouse",
            "Country house",
            "Exceptional property",
            "Apartment block",
            "Mixed-use building",
            "Town-house",
            "Mansion"
        ],
        "New Apartment": [
            "Bungalow",
            "Chalet",
            "Castle",
            "Farmhouse",
            "Country house",
            "Exceptional property",
            "Apartment block",
            "Mixed-use building",
            "Town-house",
            "Mansion"
        ],
        "Garage": [
            "Outdoor parking space",
            "Covered parking space",
            "Closed garage",
            "Closed parking"
        ],
        "Office": [
            "Offices",
            "Building",
            "Office block",
            "Mixed-use building offices",
            "Large town house",
            "Commercial villa"
        ],
        "Business": [
            "Commercial premises",
            "Mixed-use building commercial",
            "Catering industry"
        ],
        "Industry": [
            "Industrial premises",
            "Mixed-use building",
            "Warehouse"
        ]
    }

    base_url = 'https://www.immoweb.be/en/search/house/for-sale?countries=BE'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, comme Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    output_file = "all.xlsx"
    scraper = ImmowebScraper(base_url, headers, output_file, property_types)
    scraper.run_scraper(total_pages=50, pages_per_batch=5)
