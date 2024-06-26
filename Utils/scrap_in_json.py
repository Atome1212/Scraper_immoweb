import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from typing import List, Dict
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class ImmowebScraper:
    def __init__(self, base_url: str, headers: Dict[str, str], output_file: str):
        self.base_url = base_url
        self.headers = headers
        self.output_file = output_file

    def get_links(self, page: int) -> List[str]:
        response = requests.get(f'{self.base_url}&page={page}&orderBy=relevance', headers=self.headers)
        soup = bs(response.content, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', class_="card__title-link")]
        return links        

    def extract_json_data(self, url: str) -> Dict:
        response = requests.get(url, headers=self.headers)
        soup = bs(response.content, 'html.parser')
        script_tag = soup.find('div', class_="classified")
        script = script_tag.find('script', text=re.compile('window.classified'))
        script_content = script.string
        json_data_match = re.search(r'window\.classified\s*=\s*({.*});', script_content, re.DOTALL)
        if json_data_match:
            json_data = json.loads(json_data_match.group(1))
            return json_data
        return {}

    def extract_price(self, url: str) -> int:
        response = requests.get(url, headers=self.headers)
        soup = bs(response.content, 'html.parser')
        price_tag = soup.find('span', class_='sr-only')
        if price_tag:
            price_text = price_tag.string
            price = re.search(r'\d+', price_text.replace(',', '')).group()
            return int(price)
        return None

    def save_data(self, data: Dict, link_save: str) -> None:
        # Create a dictionary with default values to handle missing keys
        
        print("Locality:", data["property"]["location"]["postalCode"])
        print("Type of property:", data["property"]["type"])
        print("Subtype of property:", data["property"]["subtype"])
        print("Price:", data["transaction"]["sale"]["price"])
        print("Type of sale: None")  # Adjust this based on your needs
        print("Bedrooms:", data["property"]["bedroomCount"])
        print("Living area:", data["property"]["netHabitableSurface"])
        print("Kitchen type:", data["property"]["kitchen"]["type"])
        print("Furnished:", data["transaction"]["sale"]["isFurnished"])
        print("How many fireplaces?:", data["property"]["fireplaceCount"])
        print("Terrace surface:", data["property"]["hasTerrace"], data["property"]["terraceSurface"])
        print("Garden surface:", data["property"]["hasGarden"], data["property"]["gardenSurface"])
        print("Surface of the plot:", data["property"]["netHabitableSurface"])
        print("Number of frontages:", data["property"]["building"]["facadeCount"])
        print("Swimming pool:", data["property"]["hasSwimmingPool"])
        print("Building condition:", data["property"]["building"]["condition"])
        print("===============================")
  

        property_info = {
            "Locality": data["property"]["location"]["postalCode"] if data["property"]["location"]["postalCode"] is not None else False,
            "Type of property": data["property"]["type"] if data["property"]["type"] is not None else False,
            "Subtype of property": data["property"]["subtype"] if data["property"]["subtype"] is not None else False,
            "Price": data["transaction"]["sale"]["price"] if data["transaction"]["sale"]["price"] is not None else False,
            "Type of sale": "None",
            "Bedrooms": data["property"]["bedroomCount"] if data["property"]["bedroomCount"] is not None else False,
            "Living area": data["property"]["netHabitableSurface"] if data["property"]["netHabitableSurface"] is not None else False,
            "Kitchen type": data["property"]["kitchen"]["type"] if data["property"]["kitchen"]["type"] is not None else False,
            "Furnished": data["transaction"]["sale"]["isFurnished"] if data["transaction"]["sale"]["isFurnished"] is not None else False,
            "How many fireplaces?": data["property"]["fireplaceCount"] if data["property"]["fireplaceCount"] is not None else False,
            "Terrace surface": {data["property"]["hasTerrace"] if data["property"]["hasTerrace"] is not None else False, 
                                data["property"]["terraceSurface"] if data["property"]["terraceSurface"] is not None else False},
            "Garden surface": {data["property"]["hasGarden"] if data["property"]["hasGarden"] is not None else False, 
                            data["property"]["gardenSurface"] if data["property"]["gardenSurface"] is not None else False},
            "Surface of the plot": data["property"]["netHabitableSurface"] if data["property"]["netHabitableSurface"] is not None else False,
            "Number of frontages": data["property"]["building"]["facadeCount"] if data["property"]["building"]["facadeCount"] is not None else False,
            "Swimming pool": data["property"]["hasSwimmingPool"] if data["property"]["hasSwimmingPool"] is not None else False,
            "Building condition": data["property"]["building"]["condition"] if data["property"]["building"]["condition"] is not None else False
        }


        new_df = pd.DataFrame([property_info])

        if os.path.exists(link_save):
            df = pd.read_excel(link_save)
            df_cleaned = df.dropna(axis=1, how='all')
            new_df_cleaned = new_df.dropna(axis=1, how='all')
            df_combined = pd.concat([df_cleaned, new_df_cleaned], ignore_index=True)
        else:
            df_combined = new_df

        df_combined.to_excel(link_save, index=False)

    def scrap(self, url: str) -> None:
        data = self.extract_json_data(url)
        self.save_data(data, self.output_file)

    def scrape_links(self, links: List[str]) -> None:
        with ThreadPoolExecutor(max_workers=1) as executor:
            futures = [executor.submit(self.scrap, link) for link in links]
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
    base_url = 'https://www.immoweb.be/en/search/house/for-sale?countries=BE'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    output_file = "all.xlsx"
    scraper = ImmowebScraper(base_url, headers, output_file)
    scraper.run_scraper(total_pages=50, pages_per_batch=1)
