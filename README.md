# Google Maps Scraper

A Python-based web scraping tool using Playwright to extract business data from Google Maps. The tool allows you to scrape important business details such as the business name, address, phone number, website, reviews count, average review rating, and geographical coordinates (latitude and longitude).

## Project Overview

The **Google Maps Scraper** is designed to help users extract and organize business information from Google Maps. By leveraging Playwright for browser automation, this tool simulates user interactions with Google Maps to retrieve data about various businesses based on search criteria such as location or business type.

### Key Features:
- **Search**: Scrape business information based on a search term (e.g., restaurant, hotel, etc.) and location (e.g., city or area).
- **Business Details**: Extracts details like business name, address, phone number, website, reviews count, average review rating, and geographical coordinates.
- **Multiple Results**: Allows you to scrape a defined number of results (`-t <total_results>`).
- **Export Data**: The extracted data is saved in both **CSV** and **Excel (XLSX)** formats for easy access and analysis.
- **Custom Search List**: You can provide search terms either as command-line arguments or from a text file (`input.txt`).

## Functionalities

### 1. **Search for Businesses**
The scraper allows you to search for businesses by providing a search term and location. The search term can be any business category (e.g., restaurants, hotels, etc.) or a specific location (e.g., "restaurants in New York").

### 2. **Scrape Business Information**
For each business found in the search results, the scraper extracts the following information:
- **Business Name**: The name of the business as shown in Google Maps.
- **Business Address**: The physical address of the business.
- **Phone Number**: If available, the phone number of the business.
- **Website**: If available, the website URL of the business.
- **Reviews Count**: The total number of reviews for the business.
- **Average Reviews Rating**: The average rating of the business based on customer reviews.
- **Geographical Coordinates**: Latitude and longitude of the business based on the map URL.

### 3. **Scroll to Load More Results**
The tool automatically scrolls through the Google Maps results page to load more businesses until the desired number of businesses is scraped.

### 4. **Export Data**
Once the business details are scraped, the data is saved into:
- **CSV format**: This is ideal for opening in spreadsheet programs like Microsoft Excel, Google Sheets, or other data analysis tools.
- **Excel format (XLSX)**: The data can also be saved directly into an Excel file for better formatting and usability.

### 5. **Input and Configuration**
You can provide your search terms in two ways:
- **Command Line Arguments**: Use the `-s <search_term>` argument to define the search term and `-t <total_results>` to specify the number of results to scrape.
- **Input File**: If no search term is provided in the command line, the scraper reads search terms from an `input.txt` file.

### Example Usage

To scrape data for a search term (e.g., "restaurants in New York") and get 100 results:

```bash
python scraper.py -s "restaurants in New York" -t 100
