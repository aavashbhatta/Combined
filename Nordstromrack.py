import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options
import time
import random

def extract_from_macys():
    # Define the URL and headers
    url = "https://www.macys.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        sale_occurrences = set()
        keywords = ["off"]
        restricted_words = ["coffee", "office"]
        
        def contains_restricted_word(text, restricted_words):
            return any(word in text for word in restricted_words)
        
        # Find sales in <a> tags
        for link in soup.find_all("a"):
            text = link.text.lower().strip()
            if any(keyword in text for keyword in keywords) and not contains_restricted_word(text, restricted_words):
                sale_occurrences.add(link.text.strip())
        
        # Find sales in <div> tags with specific classes
        for div in soup.find_all("div", class_=["sale", "discount"]):
            text = div.text.lower().strip()
            if "off" in text and not contains_restricted_word(text, restricted_words):
                sale_occurrences.add(div.text.strip())
        
        # Prepare JSON data with storeId 36 for Macy's
        return [{"storeId": 36, "title": occurrence} for occurrence in sale_occurrences]
    else:
        print("Failed to retrieve Macy's webpage. Status code:", response.status_code)
        return []

def extract_from_nordstrom():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
    
    try:
        driver.get('https://www.nordstromrack.com/events/all?breadcrumb=Home%2FFlash%20Events')
        time.sleep(random.uniform(3, 5))
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.udmGE.cSeCo.wHJLP.L1fU8'))
        )
        time.sleep(random.uniform(2, 4))
        
        specific_div_texts = [element.text for element in driver.find_elements(By.CSS_SELECTOR, '.udmGE.cSeCo.wHJLP.L1fU8') if "Event ends" not in element.text]
        return [{"storeId": 5041, "title": title} for title in specific_div_texts[:15]]
    
    except Exception as e:
        print(f"Error in Nordstrom extraction: {e}")
        return []
    
    finally:
        driver.quit()

def save_to_json(data):
    with open('sale_occurrences.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Extract data from both sources
macys_data = extract_from_macys()
nordstrom_data = extract_from_nordstrom()

# Combine data
combined_data = macys_data + nordstrom_data

# Save to JSON
save_to_json(combined_data)

print("JSON file 'sale_occurrences.json' has been created successfully.")
