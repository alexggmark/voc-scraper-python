from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
import csv
import time

def scrape_reviews(page):
    global review_count
    url = f"https://www.capterra.co.uk/reviews/135106/fareharbor?page={page}" # CHANGE THIS URL 👈

    print(f"{url}")

    driver.get(url)
    time.sleep(3)  # Adjust this delay as necessary

    # Check if the URL has changed
    if driver.current_url != url:
        print(f"❌ Page does not exist or URL has changed: {url}")
        return  # If the page does not exist or the URL has changed, we stop the function

    try:
        review_containers = driver.find_elements(By.CSS_SELECTOR, ".i18n-translation_container .col-lg-7")
        print("Element found! ✅")
        print(f"Number of reviews found: {len(review_containers)}")
    except NoSuchElementException:
        print("No reviews found.")
        return

    for review in review_containers:
        title = review.find_element(By.CSS_SELECTOR, ".h5.fw-bold").get_attribute('innerHTML')
        text_elements = review.find_elements(By.CSS_SELECTOR, "p")
        review_text = ' '.join([text.get_attribute('innerHTML') for text in text_elements])
        csv_writer.writerow([title, review_text, url])
        review_count += 1  # increment the counter

# Initialize the webdriver
driver = webdriver.Chrome(service=Service('/CHANGE_THIS_PATH/Chromedriver/chromedriver')) # CHANGE PATH 👈

# Open the csv file for writing
with open('scraped_reviews.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Title", "Text", "URL of page scraped"])  # write header

    review_count = 0  # Initialize the review counter

    # Iterate over pages
    for page in range(1, 46):  # increase the limit to 46 because range() function doesn't include the end
        scrape_reviews(page)
        print(f"Scrape: page - {page}")
        print(f"Total reviews scraped: {review_count}")  # Print the total reviews scraped

# Close the webdriver
driver.quit()
