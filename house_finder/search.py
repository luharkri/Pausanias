import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import pandas as pd
import numpy as np

# Function to scrape Redfin properties based on county and filters
def scrape_redfin(county: str, max_price: str, min_beds: int, min_baths: float, hoa: int):
    url = f"https://www.redfin.com/city/19701/CA/{county}/filter/property-type=house,max-price={max_price},min-beds={min_beds},min-baths={min_baths},hoa={hoa}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all property listings on the page
    listings = soup.find_all('div', class_='HomeCardContainer')
    
    properties = []
    
    # Loop through each listing and extract details
    for listing in listings:
        try:
            # Extract the address
            address = listing.find('div', class_='bp-Homecard__Address').get_text(strip=True)
            
            # Extract the price
            price = listing.find('span', class_='bp-Homecard__Price--value').get_text(strip=True)

            facts2 = listing.find_all('span', class_='KeyFacts-item')
            
            hoa_found = 0
            for fact in facts2:
                if "HOA" in fact.text:
                    hoa_found = clean_currency(fact.get_text(strip=True).replace(" HOA", "")) 
                    
            
            
            # Extract the link
            link = 'https://www.redfin.com' + listing.find('a').get('href')
            
            # Append the data
            properties.append([address, price, link, hoa_found])
            if len(properties) > 1:
                return properties
        except AttributeError:
            continue  # Skip if any data is missing
    
    return properties

def get_rental_price(address: str):
    # Format the address for the Zillow URL
    headers = {
        
        "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    proxy_addresses = {
        'http': 'http://72.206.181.123:4145',
        'https': 'http://191.96.100.33:3128'
    }
    # Print the address for debugging
    # print(f"Getting rental price for: {address}")
    
    # Format address for the URL (ensure proper handling of spaces and commas)
    formatted_address = address.replace(" ", "-").replace(",", "").lower()
    # print(f"Formatted address: {formatted_address}")
    
    # This may need modification based on the exact URL pattern Zillow uses
    url = f"https://www.zillow.com/rental-manager/price-my-rental/results/{formatted_address}"
    # print(f"Fetching data from URL: {url}")

    try:
        # Send GET request to Zillow
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Ensure we handle unsuccessful responses
        match = re.search(r'"rentZestimate":(\d+)', response.text)
        if match:
            rent = int(match.group(1))
            return f"${rent}"
        else:
            print("Rent estimate not found in page text.")
            return "Not Available"

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return "Not Available"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Not Available"

    except requests.exceptions.RequestException as e:
        # Handle errors (e.g., network issues, bad responses)
        print(f"Error fetching rental price: {e}")
        return "Not Available"
    except Exception as e:
        # Handle any other errors that may occur
        print(f"Unexpected error: {e}")
        return "Not Available"


def clean_currency(val):
    return float(val.replace("$", "").replace(",", "").strip())

def calculate_mortgage_data(properties, down_percent=0.20, rate=0.065, term_months=360, tax_rate = .011):
    

    properties["loan"] = 0
    properties["down payment"] = 0
    properties["monthly payment"] = 0
    properties["monthly taxes"] = 0
    properties["monthly insurance"] = 0
    properties["monthly balance"] = 0
    for index, row in properties.iterrows():
        # columns=["Address", "Price", "Redfin URL", "Rental Price"]
        price = clean_currency(row["Price"])
        loan_amount = price - (down_percent * price)
        monthly_rate = rate / 12
        # Mortgage payment calculation
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** term_months) / \
            ((1 + monthly_rate) ** term_months - 1)
        monthly_property_tax = price * tax_rate / 12
        properties.loc[index, 'loan'] = loan_amount
        properties.loc[index, 'down payment'] = down_percent * price
        properties.loc[index, 'monthly payment'] = float(monthly_payment)
        properties.loc[index, 'monthly taxes'] = float(monthly_property_tax)
        # properties.loc[index, 'monthly taxes'] = monthly_property_tax
        # properties.loc[index, 'monthly taxes'] = monthly_property_tax




    
# Function to append rental prices to the property data
def append_rental_prices(properties):
    for property in properties:
        address = property[0]
        rental_price = get_rental_price(address)
        property.append(rental_price)
        time.sleep(1)  # Adding delay to be kind to the server
    
    return properties

# Function to save the rental data to a CSV file
def save_rental_to_csv(properties, filename="properties_with_rental.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Address", "Price", "Redfin URL", "Rental Price"])
        for prop in properties:
            writer.writerow(prop)

# Main function to combine scraping and rental price retrieval
def main(county="Temecula", max_price="750k", min_beds=3, min_baths=2.5, hoa=150):
    # Step 1: Scrape Redfin for property listings
    print("Scraping Redfin for properties...")
    properties = scrape_redfin(county, max_price, min_beds, min_baths, hoa)
    print(f"Found {len(properties)} properties.")
    
    
    # Step 3: Append rental prices from Zillow
    print("Fetching rental prices from Zillow...")
    properties_with_rentals = append_rental_prices(properties)
    print(f"Rental prices fetched for {len(properties_with_rentals)} properties.")
    
    # Convert to DataFrame
    df = pd.DataFrame(properties_with_rentals, columns=["Address", "Price", "Redfin URL", "HOA", "Rental Price"])

    # Step 4
    calculate_mortgage_data(properties=df)
    print(df)

    # # Step 5: Save the final data to a new CSV file
    # save_rental_to_csv(p)

    

# Run the script
if __name__ == "__main__":
    main()

