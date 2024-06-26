import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from typing import List, Dict
import os

class ImmowebScraper:
    def __init__(self, base_url: str, headers: Dict[str, str], output_file: str):
        self.base_url = base_url
        self.headers = headers
        self.output_file = output_file

    def get_price(self, url: str) -> int:
        response = requests.get(url, headers=self.headers)
        soup = bs(response.content, 'html.parser')
        price = soup.find('span', class_='sr-only').text
        return price

    def get_link(self) -> str:
        response = requests.get(self.base_url, headers=self.headers)
        soup = bs(response.content, 'html.parser')
        link = soup.find('a', class_="card__title-link")
        return link['href']

    # il ne fonctionnera pas dans un boucle car on prend juste le premier
    def get_code(self) -> str:
        pattern = r"[0-9]{4}"
        response = requests.get(self.base_url, headers=self.headers)
        soup = bs(response.content, 'html.parser')
        code = soup.find('p', class_="card__information--locality").text
        code_num = re.search(pattern, code)
        return code_num.group(0)

    def save_init_dic_building(
            self,
            locality: str,
            type_and_subtype_of_property: List[str | None],
            price: int,
            type_of_sale: str,
            other: Dict[str, int | bool | None | str],
            state_of_the_building: str,
            link_save: str
    ) -> None:
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

    def get_type_and_subtype_of_property(self, soup, dic_filter: Dict[str, List[str]]) -> List[str | None]:
        h1_title = soup.find('h1', class_='classified__title')
        if not h1_title:
            return [None, None]
        full_title = h1_title.text.strip()
        first_word = full_title.split()[0] if full_title else ""
        for j, i in dic_filter.items():
            if first_word in i:
                return [j, first_word]
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
        self.save_init_dic_building(localite_cp, [None, None], price, "None", other, "None", self.output_file)

    def run_scraper(self, pages: int) -> None:
        for i in range(pages):
            print(f"Scraping page {i}")
            link = requests.get(f'{self.base_url}&page={i}&orderBy=relevance', headers=self.headers)
            soup = bs(link.content, 'html.parser')
            page_links = soup.find_all('a', class_='card__title-link')
            for l in page_links:
                print(l.get("href"))
                self.scrap([], self.get_price(l.get("href")), l.get("href"))

if __name__ == "__main__":
    base_url = 'https://www.immoweb.be/en/search/house/for-sale?countries=BE'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, comme Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    output_file = "all.xlsx"
    scraper = ImmowebScraper(base_url, headers, output_file)
    scraper.run_scraper(50)
