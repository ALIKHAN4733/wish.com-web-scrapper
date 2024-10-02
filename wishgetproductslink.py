from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
ali = 0
# Specify the path to the ChromeDriver executable
chrome_service = Service(r'D:\realdownloads\chromedriver-win64\chromedriver.exe')

# Optionally specify the Chrome binary location if needed
chrome_options = Options()
chrome_options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
#chrome_options.add_argument('--headless')  # Uncomment if you want to run in headless mode

# Initialize Selenium WebDriver with the specified service and options
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

def scroll_down(driver, total_scroll_time=600, pause_time=5):
    """Scrolls down and then up the webpage for a specified total time."""
    pause_time=8
    end_time = time.time() + total_scroll_time  # Set the end time for scrolling

    while time.time() < end_time:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for the page to load (pause for 2 seconds)
        time.sleep(pause_time)

        # Check if the "No More Items" message is present
        if "No More Items" in driver.page_source:
            print("No More Items found. Breaking the loop.")
            break

        # Scroll back up to the top
        driver.execute_script("window.scrollTo(0, 0);")

        # Wait for the page to adjust after scrolling up
        time.sleep(pause_time)

def scrape_wish_products(driver, url):
    global ali
    driver.get(url)
    time.sleep(3)



    # Scroll down for ten minutes
    scroll_down(driver)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    products = []

    # Extract product details
    for item in soup.find_all('div', class_='ProductGrid__FeedTileWidthWrapper-sc-122ygxd-3'):
        link_element = item.find('a', class_='FeedTile__Wrapper-sc-1jtmq9g-2')
        title_element = item.find('div', class_='FeedTile__Row2-sc-1jtmq9g-20')
        price_element = item.find('div', class_='FeedTile__ActualPrice-sc-1jtmq9g-14')
        image_element = item.find('img', class_='FeedTile__Image-sc-1jtmq9g-5')

        if link_element and title_element and price_element:
            product_url = 'https://www.wish.com' + link_element.get('href')
            title = title_element.get_text().strip()
            price = price_element.get_text().strip()
            image_url = image_element['src'] if image_element else 'No Image'

            products.append({
                'title': title,
                'url': product_url
            })

    return products

def save_to_csv(products, filename):
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

# Example Usage
urls = [
       "https://www.wish.com/~/gadgets","https://www.wish.com/~/gadgets/mobile-phones-and-accessories","https://www.wish.com/~/gadgets/computers-and-office-gadgets",
    "https://www.wish.com/~/gadgets/home-electronics","https://www.wish.com/~/gadgets/car-electronics",
    "https://www.wish.com/~/baby-gear","https://www.wish.com/~/baby-gear/baby-toys","https://www.wish.com/~/baby-gear/baby-health-and-safety",
    "https://www.wish.com/~/baby-gear/baby-accessories","https://www.wish.com/~/baby-gear/baby-hygiene-products",
    "https://www.wish.com/~/baby-gear/baby-feeding-accessories","https://www.wish.com/~/fashion/fashion-brands","https://www.wish.com/~/fashion/women's-fashion",
    "https://www.wish.com/~/fashion/men's-fashion","https://www.wish.com/~/fashion/kids'-clothing","https://www.wish.com/~/fashion/shoes","https://www.wish.com/~/pet-accessories/dog-accessories",
    "https://www.wish.com/~/pet-accessories/cat-accessories","https://www.wish.com/~/pet-accessories/rabbit-accessories","https://www.wish.com/~/pet-accessories/aquariums",
    "https://www.wish.com/~/pet-accessories/hamster-accessories","https://www.wish.com/~/pet-accessories/pet-bird-accessores",
    "https://www.wish.com/~/pet-accessories/iguana-accessories","https://www.wish.com/~/pet-accessories/reptile-terrariums","https://www.wish.com/~/drinks-and-smokes/drinking-accessories",
    "https://www.wish.com/~/drinks-and-smokes/smoking-accessories","https://www.wish.com/~/health-and-beauty/beauty-and-cosmetics","https://www.wish.com/~/health-and-beauty/home-health-products"


    ]

file_path = 'wishdatareal.csv'

# Loop through URLs and scrape data without reopening the browser
al1= 0
j = 0
while j < len(urls):
    link12 = urls[j]
    wish_products = scrape_wish_products(driver, link12)
    save_to_csv(wish_products, file_path)
    j += 1
    al1 += 1
    print(al1)


# Quit the browser after processing all URLs
driver.quit()
