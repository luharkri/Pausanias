import requests
from bs4 import BeautifulSoup
import csv
import time
import re

# Function to scrape Redfin properties based on county and filters
def scrape_redfin(county: str, max_price: str, min_beds: int, min_baths: float, hoa: int):
    url = f"https://www.redfin.com/city/19701/CA/{county}/filter/property-type=house,max-price={max_price},min-beds={min_beds},min-baths={min_baths},hoa={hoa}"
    # print(url)
    

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
    # print(listings[0])
    
    properties = []
    
    # Loop through each listing and extract details
    # Loop through each listing and extract details
    for listing in listings:
        try:
            # Extract the address
            address = listing.find('div', class_='bp-Homecard__Address').get_text(strip=True)
            
            # Extract the price
            price = listing.find('span', class_='bp-Homecard__Price--value').get_text(strip=True)
            
            # Extract the link
            link = 'https://www.redfin.com' + listing.find('a').get('href')
            
            # Append the data
            properties.append([address, price, link])
            if len(properties) > 1:
                return properties
        except AttributeError:
            continue  # Skip if any data is missing
    
    return properties

# Function to save the scraped data into a CSV file
def save_to_csv(properties, filename="properties.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Address", "Price", "Redfin URL"])
        for prop in properties:
            writer.writerow(prop)

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
    print(f"Getting rental price for: {address}")
    
    # Format address for the URL (ensure proper handling of spaces and commas)
    formatted_address = address.replace(" ", "-").replace(",", "").lower()
    print(f"Formatted address: {formatted_address}")
    
    # This may need modification based on the exact URL pattern Zillow uses
    url = f"https://www.zillow.com/rental-manager/price-my-rental/results/{formatted_address}"
    print(f"Fetching data from URL: {url}")

    try:
        # Send GET request to Zillow
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Ensure we handle unsuccessful responses
        match = re.search(r'"rentZestimate":(\d+)', response.text)
        if match:
            rent = int(match.group(1))
            print(f"Found rent estimate: ${rent}")
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

def calculate_mortgage_data(properties, down_percent=0.20, rate=0.065, term_months=360):
    enriched_data = []

    for address, list_price_str, url, rent_str in properties:
        list_price = clean_currency(list_price_str)
        purchase_price = list_price * 0.86
        down_payment = purchase_price * down_percent
        loan_amount = purchase_price - down_payment
        monthly_rate = rate / 12

        # Mortgage payment calculation
        M = loan_amount * (monthly_rate * (1 + monthly_rate) ** term_months) / \
            ((1 + monthly_rate) ** term_months - 1)

        # Build new row
        enriched_data.append([
            address,
            list_price_str,
            url,
            rent_str,
            f"${purchase_price:,.2f}",
            f"{down_percent * 100:.1f}%",
            f"${down_payment:,.2f}",
            f"${loan_amount:,.2f}",
            f"{rate * 100:.2f}%",
            term_months,
            f"${M:,.2f}"
        ])

    return enriched_data

# Function to append rental prices to the property data
def append_rental_prices(properties):
    for property in properties:
        address = property[0]
        print(address)
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
    
    # # Step 2: Save the properties to a CSV file
    # save_to_csv(properties)
    # print("Redfin data saved to properties.csv.")
    
    # Step 3: Append rental prices from Zillow
    print("Fetching rental prices from Zillow...")
    properties_with_rentals = append_rental_prices(properties)
    print(f"Rental prices fetched for {len(properties_with_rentals)} properties.")
    print(properties_with_rentals)

    # Step 4
    # need to do some data analysis here
    p = calculate_mortgage_data(properties=properties)


    # # Step 5: Save the final data to a new CSV file
    save_rental_to_csv(p)

    

# Run the script
if __name__ == "__main__":
    main()

