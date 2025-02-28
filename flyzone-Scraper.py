from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import urljoin, urlparse
import os

def scrape_all_pages(base_url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Use WebDriver Manager to handle ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Store visited URLs to avoid duplicates
        visited_urls = set()
        urls_to_visit = [base_url]

        # Create a directory to save content
        os.makedirs("scraped_content", exist_ok=True)

        while urls_to_visit:
            current_url = urls_to_visit.pop(0)
            if current_url in visited_urls:
                continue

            # Visit the current URL
            driver.get(current_url)
            time.sleep(3)  # Wait for the page to load

            # Extract page content
            body_element = driver.find_element(By.TAG_NAME, "body")
            page_content = body_element.text

            # Save page content to a file
            parsed_url = urlparse(current_url)
            file_name = f"{parsed_url.path.strip('/').replace('/', '_') or 'home'}.txt"
            file_path = os.path.join("scraped_content", file_name)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(page_content)

            print(f"Scraped: {current_url}")
            visited_urls.add(current_url)

            # Find all links on the current page
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and href.startswith(base_url) and href not in visited_urls:
                    urls_to_visit.append(href)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

# Main script execution
if __name__ == "__main__":
    base_url = "https://flyzone.ai/"
    scrape_all_pages(base_url)
