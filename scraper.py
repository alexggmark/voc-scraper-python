import csv
import requests
from bs4 import BeautifulSoup
import re
import time
from tenacity import retry, stop_after_attempt, wait_fixed

def generate_variations_of_url(base_url, total_pages, total_stars):
    url_variations = []
    for stars in range(1, total_stars + 1):
        for page in range(1, total_pages + 1):
            url = f"{base_url}?page={page}&stars={stars}"
            url_variations.append(url)
    return url_variations

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))  # Retry up to 3 times with a 1-second delay between retries
def fetch_page_content(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception if the response status code is not 200
    return response.content

def scrape_page(url):
    try:
        content = fetch_page_content(url)
        time.sleep(1)  # Add a 1-second delay to let dynamic elements load
        soup = BeautifulSoup(content, 'html.parser')
        title_elements = soup.select('[data-service-review-title-typography]')
        text_elements = soup.select('[data-service-review-text-typography]')

        if len(title_elements) != len(text_elements):
            print(f"Error: The number of title elements doesn't match the number of text elements for URL: {url}")
            return None

        scraped_data = []
        for title, text in zip(title_elements, text_elements):
            title_text = title.get_text(strip=True)
            text_text = text.get_text(strip=True)
            scraped_data.append(f"{title_text} {text_text}")

        return scraped_data
    except requests.exceptions.HTTPError as e:
        print(f"Error: Unable to fetch the page. Status code: {e.response.status_code} for URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Request error occurred for URL: {url}. {e}")
        return None

def save_to_csv(data, url):
    if not data:
        return

    # Extract the domain name from the URL to use in the output file name
    domain = re.findall(r"(https?://)(.*?)/", url)
    if domain:
        domain = domain[0][1].replace('.', '_')
    else:
        domain = 'unknown'

    # Create the output file name with the URL and current timestamp
    filename = f"scraped_data_{domain}.csv"
    with open(filename, 'a', newline='', encoding='utf-8') as file:  # Use 'a' for append mode
        writer = csv.writer(file)

        # Check if the file is empty, if so, write the header row
        if file.tell() == 0:
            writer.writerow(['Text', 'URL'])

        for item in data:
            writer.writerow([item, url])

if __name__ == "__main__":
    base_url = "https://uk.trustpilot.com/review/bokun.io"
    total_pages = 20
    total_stars = 5

    url_variations = generate_variations_of_url(base_url, total_pages, total_stars)

    for url in url_variations:
        scraped_data = scrape_page(url)

        if scraped_data:
            save_to_csv(scraped_data, url)
            print(f"Data has been scraped and appended to 'scraped_data_{url}.csv'.")
