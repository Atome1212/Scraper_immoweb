#  ***Immoweb Scraper*** 

## 📜 Project Description
*This project is designed to scrape property information from the Immoweb website, focusing on extracting various data points for comprehensive analysis. The data includes locality, property type, price, and additional details like the number of bedrooms, living area, and more. All collected data is stored in a CSV file for further analysis and machine learning purposes.*

[![N|Solid](https://www.promptcloud.com/wp-content/uploads/2018/07/what-is-web-scraping-diagram.png "easter egg")](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley&autoplay=1)
***click on the image to use our scraper...***


## 👀 Project Overview

This project is designed to scrape property information from the Immoweb website, focusing on extracting various data points for comprehensive analysis. The data includes locality, property type, price, and additional details like the number of bedrooms, living area, and more. All collected data is stored in a CSV file for further analysis and machine learning purposes.

## 🌳 Project Directory Structure

```plaintext
SCRAPER_IMMOWEB/
│
├── Note/
│   └── <note files>
├── Utils/
│   ├── __pycache__/
│   ├── scrap_draft.py
│   ├── scrap_in_json.py
│   ├── scrap_multy.py
│   └── scrap.py
├── main.py
├── README.md
└── requirements.txt
```

## 🧑🏻‍💻 Functions used



- **```get_links(self, page) -> List[str]```** 
Retrieves property links from a search result page by sending an HTTP GET request and parsing the HTML to find all relevant links.

- **```extract_json_data(self, url:str) -> Dict[str, Any]```** Fetches JSON data from a property detail page by sending an HTTP GET request and parsing the HTML to extract the JSON data.

- **```save_data(self, data, filename:str) -> none```**: Saves extracted property data to a CSV file, creating the file and writing headers if necessary. Increments a counter for each property and handles data specific to sale or rent.

- **```scrap(self, url:str) -> None```**
Scrapes data from a property URL by extracting JSON data and saving it to a CSV file.

- **```scrape_links(self, links) -> None```**
Scrapes multiple property links concurrently using a ThreadPoolExecutor to handle multiple threads.
- **```run_scraper(self)```**
Runs the scraper for multiple pages, fetching and scraping property links until no more links are found.


## 🐍 Sample Code 
```python
def scrape_links(self, links: List[str]) -> None:
        """
        Scrape multiple property links concurrently.

        Args:
            links (List[str]): List of property links to scrape.
        """
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(self.scrap, link) for link  in links]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    #print(f"Error: {e}")
                    pass

```
## 🔧  Installation

To run the scraper app locally, follow these steps:

1. Clone the repository:

    
    ``` git clone https://github.com/Atome1212/Scraper_immoweb ```
    

2. Navigate into the cloned repository:

    
    ``` cd ./Scraper_immoweb/ ```


3. Install the necessary dependencies using pip:

    
    ``` pip install -r requirements.txt ```
    

4. Once you did all the these steps, type this commande in the terminal:

   ``` python3 main.py ```   
          or               
   ``` python main.py ```


---
## 🎉 Have Fun!

*I hope you'll find joy by using our scraper just as much joy as we had in developing it!* 🚀
