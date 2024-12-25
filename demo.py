"""This script demonstrates how to use Python and Playwright to extract data from Google Maps"""

from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
import os
import sys

@dataclass
class Business:
    """Represents a business's information"""

    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    reviews_count: int = None
    reviews_average: float = None
    latitude: float = None
    longitude: float = None


@dataclass
class BusinessList:
    """Holds multiple businesses and can save them as Excel or CSV files"""

    business_list: list[Business] = field(default_factory=list)
    save_at = 'output'

    def dataframe(self):
        """Converts business_list to a pandas dataframe

        Returns:
            pandas dataframe: A dataframe containing the business data
        """
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_"
        )

    def save_to_excel(self, filename):
        """Saves the business data to an Excel file

        Args:
            filename (str): The name of the Excel file to save
        """
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_excel(f"output/{filename}.xlsx", index=False)

    def save_to_csv(self, filename):
        """Saves the business data to a CSV file

        Args:
            filename (str): The name of the CSV file to save
        """
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_csv(f"output/{filename}.csv", index=False)

def extract_coordinates_from_url(url: str) -> tuple[float, float]:
    """Extracts latitude and longitude from a Google Maps URL"""
    
    coordinates = url.split('/@')[-1].split('/')[0]
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])

def main():
    
    ########
    # Parsing input arguments
    ########
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-t", "--total", type=int)
    args = parser.parse_args()
    
    if args.search:
        search_list = [args.search]
        
    if args.total:
        total = args.total
    else:
        total = 10 # Default to a large number if not specified

    if not args.search:
        search_list = []
        input_file_name = 'input.txt'
        input_file_path = os.path.join(os.getcwd(), input_file_name)
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r') as file:
                search_list = file.readlines()
                
        if len(search_list) == 0:
            print('Error: You must provide a search term via -s or use an input.txt file')
            sys.exit()
        
    ###########
    # Web scraping begins here
    ###########
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.google.com/maps", timeout=60000)
        page.wait_for_timeout(5000)  # Allow page to load completely
        
        for search_for_index, search_for in enumerate(search_list):
            print(f"-----\nSearching for {search_for_index} - {search_for}".strip())

            # Typing search term into the search box
            page.locator('//input[@id="searchboxinput"]').fill(search_for)
            page.wait_for_timeout(3000)  # Wait for results to load

            # Pressing enter to trigger search
            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)  # Wait for results to load

            # Hovering to initiate scrolling
            page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

            previously_counted = 0
            while True:
                # Scrolling down to load more results
                page.mouse.wheel(0, 10000)
                page.wait_for_timeout(3000)

                if (
                    page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).count()
                    >= total
                ):
                    listings = page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).all()[:total]
                    listings = [listing.locator("xpath=..") for listing in listings]
                    print(f"Total listings scraped: {len(listings)}")
                    break
                else:
                    if (
                        page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).count()
                        == previously_counted
                    ):
                        listings = page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).all()
                        print(f"Scraping complete, found all available listings\nTotal: {len(listings)}")
                        break
                    else:
                        previously_counted = page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).count()
                        print(
                            f"Scraped so far: ",
                            page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).count(),
                        )

            business_list = BusinessList()

            # Scraping details for each listing
            for listing in listings:
                try:
                    listing.click()  # Click on the listing
                    page.wait_for_timeout(5000)

                    # XPath to retrieve various business details
                    name_attribute = 'aria-label'
                    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                    website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                    phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                    review_count_xpath = '//button[@jsaction="pane.reviewChart.moreReviews"]//span'
                    reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'

                    business = Business()

                    # Safe check for each attribute
                    name = listing.get_attribute(name_attribute)
                    business.name = name if name else ""  # Set to empty if None

                    if page.locator(address_xpath).count() > 0:
                        business.address = page.locator(address_xpath).all()[0].inner_text()
                    else:
                        business.address = ""

                    if page.locator(website_xpath).count() > 0:
                        business.website = page.locator(website_xpath).all()[0].inner_text()
                    else:
                        business.website = ""

                    if page.locator(phone_number_xpath).count() > 0:
                        business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text()
                    else:
                        business.phone_number = ""

                    if page.locator(review_count_xpath).count() > 0:
                        business.reviews_count = int(
                            page.locator(review_count_xpath).inner_text()
                            .split()[0]
                            .replace(',', '')
                            .strip()
                        )
                    else:
                        business.reviews_count = None  # Set to None if no reviews

                    if page.locator(reviews_average_xpath).count() > 0:
                        business.reviews_average = float(
                            page.locator(reviews_average_xpath).get_attribute(name_attribute)
                            .split()[0]
                            .replace(',', '.')
                            .strip()
                        )
                    else:
                        business.reviews_average = None  # Set to None if no average reviews

                    # Extract coordinates (latitude, longitude)
                    business.latitude, business.longitude = extract_coordinates_from_url(page.url)

                    # Add this business to the list
                    business_list.business_list.append(business)

                except Exception as e:
                    print(f'Error occurred: {e}')

            #########
            # Saving data
            #########
            business_list.save_to_excel(f"google_maps_data_{search_for}".replace(' ', '_'))
            business_list.save_to_csv(f"google_maps_data_{search_for}".replace(' ', '_'))

        browser.close()


if __name__ == "__main__":
    main()
