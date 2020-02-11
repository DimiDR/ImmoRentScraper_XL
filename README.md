# ImmoRentScraper_XL
Scrape all the Data from Immobilienscout24 with Scrapy

# Requirenments
Scrapy

# Description
This scraper will get information from 3 soures.
- from the main search page of Immobilienscout24
- from the detail pages of the ral estate objects
- from an API to get the information of cost of purchasing
Check Pipeline for DB definition.

# Run
The program can simply be executed with "runner.py".
The URL can be inputted as string. All the data behind this URL will be scrapped.
The URL should contain the needed filter criteria. Please go to www.immobilienscout24.de to get the search link.

# Saving of Data
The scraped data will be saved into a SQLite Database "real-estate.db".