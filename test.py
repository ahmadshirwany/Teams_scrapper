from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


def test_selenium():
    print("Starting Selenium test...")

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode for server environment
    print("Chrome options set.")

    # Set up the Chrome driver
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print("ChromeDriver initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize ChromeDriver: {e}")
        return

    try:
        # Navigate to a website
        print("Navigating to https://www.google.com...")
        driver.get("https://www.google.com")
        print("Navigation successful.")

        # Check the title of the page
        print("Checking page title...")
        title = driver.title
        print(f"Page title is: {title}")

        if "Google" in title:
            print("Selenium is working! Page title is correct.")
        else:
            print("Selenium is not working. Page title is incorrect.")

    except Exception as e:
        print(f"An error occurred during the test: {e}")

    finally:
        # Close the browser
        print("Closing the browser...")
        driver.quit()
        print("Browser closed.")


if __name__ == "__main__":
    test_selenium()
