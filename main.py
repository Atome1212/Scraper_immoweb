from Utils.scrap_in_json import ImmowebScraper


def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Scraper for houses for sale
    base_url_sale = 'https://www.immoweb.be/en/search/house/for-sale?countries=BE'
    output_file_sale = "../Data/data.csv"
    scraper_sale = ImmowebScraper(base_url_sale, headers, output_file_sale, type_of_sale="sale")
    scraper_sale.run_scraper()



if __name__ == "__main__":
    main()