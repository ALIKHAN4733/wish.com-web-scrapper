from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import json
import re

# Specify the path to the ChromeDriver executable
chrome_service = Service(r'D:\realdownloads\chromedriver-win64\chromedriver.exe')

# Optionally specify the Chrome binary location if needed
chrome_options = Options()
chrome_options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
#chrome_options.add_argument('--headless')  # Uncomment if you want to run in headless mode

# Initialize Selenium WebDriver with the specified service and options
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

def get_unique_filename(base_name, extension):
    """Generate a unique filename by appending a number if the file already exists."""
    i = 1
    new_name = f"{base_name}{extension}"
    while os.path.exists(new_name):
        new_name = f"{base_name}_{i}{extension}"
        i += 1
    return new_name
def extract_attribute(patterns, text):
    """Extract attribute value using a list of patterns."""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def scrape_wish_product_details(driver, url):
    """Scrape the product details from a given URL after a 3-second wait."""
    driver.get(url)
    time.sleep(8)  # Wait for the page to load

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_data = {
        'url': url,
        'productSKU': None,
        'title': None,
        'price': None,
        'image': None,
        'description': None,
        'NumberOfRating': None,
        'rating': None,
        'gallery': '',
        'colors': None,
        'size': None,
        'model': None,
        'dimension': None,
        'Material': None,
        'category': None,
    }

    # Extract product title
    title_element = soup.find('div', class_='FeedTile__Row2-sc-1jtmq9g-20')
    if title_element:
        product_data['title'] = title_element.get_text().strip()

    product_id_match = re.search(r'/product/([a-fA-F0-9]{24})', url)
    if product_id_match:
        product_data['productSKU'] = product_id_match.group(1)

    category_match = re.search(r'/~/(.*?)/product/', url)
    if category_match:
        product_data['category'] = category_match.group(1)



    description_element = soup.find('div', class_='ProductDescriptionContainer__DescriptionContainer-m8ay5d-6 cAsEIt')
    if description_element:
        description_text = description_element.get_text().strip()
        product_data['description'] = description_text

        # Define patterns for each attribute
        color_patterns = [r'Color:\s*([^,]+(?:, [^,]+)*)', r'color:\s*([^,]+(?:, [^,]+)*)']
        material_patterns = [r'Material:\s*([^,]+(?:, [^,]+)*)', r'material:\s*([^,]+(?:, [^,]+)*)']
        size_patterns = [r'Size:\s*([^,]+(?:, [^,]+)*)', r'size:\s*([^,]+(?:, [^,]+)*)']
        model_patterns = [r'Model:\s*([^,]+)', r'model:\s*([^,]+)']
        dimension_patterns = [r'Size:\s*([0-9.]+\s*\*\s*[0-9.]+\s*\*\s*[0-9.]+mm)', r'size:\s*([0-9.]+\s*\*\s*[0-9.]+\s*\*\s*[0-9.]+mm)']

        # Extract attributes
        product_data['colors'] = extract_attribute(color_patterns, description_text)
        product_data['Material'] = extract_attribute(material_patterns, description_text)
        product_data['size'] = extract_attribute(size_patterns, description_text)
        product_data['model'] = extract_attribute(model_patterns, description_text)
        product_data['dimension'] = extract_attribute(dimension_patterns, description_text)



    # Extract product price
    price_element = soup.find('div', {'data-testid': 'product-price'})
    if price_element:
        product_data['price'] = price_element.get_text().strip()

    shipppingcost_element = soup.find('div', class_='ProductShippingContainer__ShippingPrice-ioscsf-6 dkqmxD')
    if shipppingcost_element:
        product_data['shippingcost'] = shipppingcost_element.get_text().strip()

    NumberOfRating_element = soup.find('div', class_='PurchaseContainer__RatingCount-sc-15kmsqg-5 cZSOhk')
    if NumberOfRating_element:
        product_data['NumberOfRating'] = NumberOfRating_element.get_text().strip()

    # Extract rating
    rating_element = soup.find('div', class_='ReviewSection__AverageRatingScoreSection-gcknhu-2 dwYVdR')
    if rating_element:
    # Extract the text part before the nested div (stars)
        product_data['rating'] = rating_element.contents[0].strip()



    # Extract image URLs from the gallery
    gallery_element = soup.find('div', class_='ProductImageContainer__StripImages-sc-1gow8tc-8')
    if gallery_element:
        images = gallery_element.find_all('img')
        image_urls = [img['src'] for img in images if img.get('src')]
        product_data['gallery'] = json.dumps(image_urls)  # Convert list to a JSON string

    # Extract product main image
    image_element = soup.find('img', class_='FeedTile__Image-sc-1jtmq9g-5')
    if image_element:
        product_data['image'] = image_element['src']

    return product_data

def save_to_csv(products, filename):
    """Save the scraped product data to a CSV file."""
    if products:
        df = pd.DataFrame(products)
        df = df.drop_duplicates()
        df = df.fillna('Unknown')

        # Check if file exists, then append without headers, otherwise write normally
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False, index=False)
        else:
            df.to_csv(filename, index=False)

        print(f"Data saved to {filename}")

# Main script execution
if __name__ == '__main__':
    # Load data from the existing CSV file
    csv_file = 'wishdata101.csv'
    wish_df = pd.read_csv(csv_file)

    # Replace empty titles with NaN and drop rows with NaN titles
    wish_df['title'].replace('', pd.NA, inplace=True)
    wish_df.dropna(subset=['title'], inplace=True)

    # Save the cleaned data to a new CSV file (optional)
    wish_df.to_csv("wish_basic_data.csv", header=True, index=False)
    print("Basic data CSV created.")

    # Iterate over URLs and scrape details
    all_product_details = []
    for url in wish_df['url']:
        print(f"Scraping details from: {url}")
        product_details = scrape_wish_product_details(driver, url)
        all_product_details.append(product_details)

    # Save the final product details to a CSV file
    final_filename = get_unique_filename("wish_complete", ".csv")
    save_to_csv(all_product_details, final_filename)

    # Close the browser after processing all URLs
    driver.quit()
    print(f"Data updated and saved to {final_filename}")
