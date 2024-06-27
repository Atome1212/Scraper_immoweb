from Utils.scrap_in_json import ImmowebScraper

if __name__ == "__main__":
    base_url = 'https://www.immoweb.be/en/search/house/for-sale?countries=BE'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    output_file = "all.xlsx"
    scraper = ImmowebScraper(base_url, headers, output_file)
    scraper.run_scraper(total_pages=50, pages_per_batch=1)