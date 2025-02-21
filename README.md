# Amazon Data Scraper & React App

This project integrates a Scrapy-Selenium spider with a React app. The spider crawls Amazon using specific keywords, saves the data to a JSON file, and the React app displays the data in a tabular format.

## Project Overview

1. **Crawler**: A Scrapy-Selenium spider (`amazonScrape`) that crawls Amazon using specific keywords. The spider fetches data and stores it in a JSON file.
2. **React App**: The app reads the JSON file generated by the spider and displays the product data in a tabular format.

### Why Scrapy-Selenium?
The crawling process was not ideal for standard Scrapy, so Scrapy-Selenium was chosen for better handling of dynamic content, such as JavaScript-loaded data.


### Crawler Components

- **amazonScrape.py**: The main spider that performs the crawling task on Amazon, using keywords to search products and scrape data.
- **product_model.py**: Defines the data model for products.
- **keyword_input.py**: A standalone script to gather keywords for the spider to use. Run this script to get a list of keywords for crawling.
- **file_saver.py**: A module responsible for saving scraped data to a JSON file.
- **json_reader.py**: A module to read the saved JSON file and make it ready for the React app.

### React App Components

- **App.js**: The entry point for the React app. It fetches data from the JSON file and renders it in a table format.
- **components/**: Contains reusable components, including a table that displays product information.

#### Prerequisites

- Python 3.x
- Scrapy
- Selenium
- ChromeDriver

#### Folder Details
- public/
- crawler/spiders/amazonScrape.py: The spider that scrapes data.
- modules/: Contains utility modules to handle keywords, saving files, and reading JSON.
- settings.py: Scrapy settings and configurations.
- requirements.txt: Lists dependencies like Scrapy, Selenium, etc.
- App.js: Main React component that fetches and displays the JSON data.
- package.json: Lists React app dependencies.