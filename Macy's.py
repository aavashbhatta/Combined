import requests
from bs4 import BeautifulSoup
import json

# Define the URL and headers
url = "https://www.macys.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

# Send a GET request to the URL
response = requests.get(url, headers=headers)

if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    sale_occurrences = set()  # Store unique occurrences

    # Define keywords and restricted words
    keywords = ["off"]
    restricted_words = ["coffee", "office"]

    # Function to check if text contains any restricted words
    def contains_restricted_word(text, restricted_words):
        return any(word in text for word in restricted_words)

    # Look for occurrences of keywords in <a> tags
    for link in soup.find_all("a"):
        text = link.text.lower().strip()
        if any(keyword in text for keyword in keywords) and not contains_restricted_word(text, restricted_words):
            sale_occurrences.add(link.text.strip())

    # Look for "off" in <div> tags with specific classes
    for div in soup.find_all("div", class_=["sale", "discount"]):
        text = div.text.lower().strip()
        if "off" in text and not contains_restricted_word(text, restricted_words):
            sale_occurrences.add(div.text.strip())

    # Prepare JSON data with constant storeId
    json_data = [{"storeId": 36, "title": occurrence} for occurrence in sale_occurrences]

    # Write the JSON data to a file
    with open("sale_occurrences.json", "w") as file:
        json.dump(json_data, file, indent=4)

    print("JSON file 'sale_occurrences.json' has been created successfully.")
else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)
