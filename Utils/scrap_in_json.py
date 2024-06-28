import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from typing import List, Dict, Any
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import threading
import csv

file_lock = threading.Lock()

class ImmowebScraper:
    """
    A scraper class to extract property data from Immoweb for sale and rent listings.
    """
    def __init__(self, base_url: str, headers: Dict[str, str], output_file: str, type_of_sale: str, count: int = 0) -> None:
        """
        Constructor for initializing the scraper class.

        Args:
            base_url (str): Base URL for property search.
            headers (Dict[str, str]): HTTP headers for requests.
            output_file (str): Path to the CSV file for saving data.
            type_of_sale (str): Type of sale ("sale" or "rent").
            count (int): Counter for properties (default is 0).
        """
        self.base_url = base_url
        self.headers = headers
        self.output_file = output_file
        self.type_of_sale = type_of_sale
        self.counter = count
        self.session = requests.Session()
        self.session.headers.update(headers)

    def get_links(self, page: int) -> List[str]:
        """
        Get property links from a search result page.

        Args:
            page (int): Page number to scrape.

        Returns:
            List[str]: List of property links.
        """
        response = self.session.get(f'{self.base_url}&page={page}&orderBy=relevance')
        soup = bs(response.content, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', class_="card__title-link")]
        return links        

    def extract_json_data(self, url: str) -> Dict[str, Any]:
        """
        Extract JSON data from a property detail page.

        Args:
            url (str): URL of the property detail page.

        Returns:
            Dict[str, Any]: JSON data of the property.
        """
        response = self.session.get(url)
        soup = bs(response.content, 'html.parser')
        script_tag = soup.find('div', class_="classified")
        script = script_tag.find('script', text=re.compile('window.classified'))
        script_content = script.string
        json_data_match = re.search(r'window\.classified\s*=\s*({.*});', script_content, re.DOTALL)
        if json_data_match:
            json_data = json.loads(json_data_match.group(1))
            return json_data
        return {}

    def save_data(self, data: Dict[str, Any], filename: str) -> None:
        """
        Save extracted property data to a CSV file.

        Args:
            data (Dict[str, Any]): Property data.
            filename (str): Path to the CSV file.
        """
        self.counter += 1
        print(self.counter)

        if self.type_of_sale == "sale":
            price = data["transaction"]["sale"]["price"] if data["transaction"]["sale"]["price"] is not None else False
        elif self.type_of_sale == "rent":
            monthly_rent = data["transaction"]["rental"]["monthlyRentalPrice"] if data["transaction"]["rental"]["monthlyRentalPrice"] is not None else 0
            monthly_costs = data["transaction"]["rental"]["monthlyRentalCosts"] if data["transaction"]["rental"]["monthlyRentalCosts"] is not None else 0
            price = monthly_rent + monthly_costs if (monthly_rent and monthly_costs) else False

        property_info = {
            "Locality": data["property"]["location"]["postalCode"] if data["property"]["location"]["postalCode"] is not None else False,
            "Type of property": data["property"]["type"] if data["property"]["type"] is not None else False,
            "Subtype of property": data["property"]["subtype"] if data["property"]["subtype"] is not None else False,
            "Price": price,
            "Type of sale": self.type_of_sale,
            "Bedrooms": data["property"]["bedroomCount"] if data["property"]["bedroomCount"] is not None else False,
            "Living area": data["property"]["netHabitableSurface"] if data["property"]["netHabitableSurface"] is not None else False,
            "Kitchen type": data["property"]["kitchen"]["type"] if data["property"]["kitchen"]["type"] is not None else False,
            "Furnished": data["transaction"]["rental"]["isFurnished"] if self.type_of_sale == "rent" else data["transaction"]["sale"]["isFurnished"],
            "How many fireplaces?": data["property"]["fireplaceCount"] if data["property"]["fireplaceCount"] is not None else False,
            "Terrace surface": data["property"]["terraceSurface"] if data["property"]["terraceSurface"] is not None else False,
            "Garden surface": data["property"]["gardenSurface"] if data["property"]["gardenSurface"] is not None else False,
            "Surface of the plot": data["property"]["netHabitableSurface"] if data["property"]["netHabitableSurface"] is not None else False,
            "Number of frontages": data["property"]["building"]["facadeCount"] if data["property"]["building"]["facadeCount"] is not None else False,
            "Swimming pool": data["property"]["hasSwimmingPool"] if data["property"]["hasSwimmingPool"] is not None else False,
            "Building condition": data["property"]["building"]["condition"] if data["property"]["building"]["condition"] is not None else False
        }

        with file_lock:
            file_exists = os.path.isfile(filename)
            is_empty = not file_exists or os.path.getsize(filename) == 0

            with open(filename, 'a', newline='') as file:
                writer = csv.writer(file)

                if is_empty:
                    writer.writerow(property_info.keys())

                writer.writerow(property_info.values())

    def scrap(self, url: str) -> None:
        """
        Scrape data from a property URL and save it.

        Args:
            url (str): URL of the property detail page.
        """
        data = self.extract_json_data(url)
        self.save_data(data, self.output_file)

    def scrape_links(self, links: List[str]) -> None:
        """
        Scrape multiple property links concurrently.

        Args:
            links (List[str]): List of property links to scrape.
        """
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(self.scrap, link) for link in links]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    pass

    def run_scraper(self) -> None:
        """
        Run the scraper for multiple pages until the last page.
        """
        page = 1
        while True:
            links = self.get_links(page)
            if not links:
                break
            self.scrape_links(links)
            page += 1

if __name__ == "__main__":
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Scraper for houses for sale
    base_url_sale = 'https://www.immoweb.be/en/search/house/for-sale?countries=BE'
    output_file_sale = "../Data/data.csv"
    scraper_sale = ImmowebScraper(base_url_sale, headers, output_file_sale, type_of_sale="sale")
    scraper_sale.run_scraper()

