from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
import pdb


class Selenium:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        self.driver = webdriver.Chrome(options=options)
        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def get(self, url: str):
        self.driver.get(url)


    def get_title(self):
        
        element = self.driver.find_element(
            By.XPATH,
            '//*[@id="main-content"]/section[1]/div/section[2]/div/div[1]/div/h1',
        )
        title = element.text
        return title

    def get_description(self) -> str:
        """
        Get the job description raw HTML. It includes <strong>, <i>, etc.

        Example output:
            "<div>The <strong>Energy Markets team at Octopus Energy</strong> is responsible for making sure that...</div>"
        """
        element = self.driver.find_element(
            By.XPATH,
            '//*[@id="main-content"]/section[1]/div/div/section[1]/div/div/section/div',
        )
        desc_html = element.get_attribute("outerHTML")
        return desc_html

    def get_company(self) -> str:
        """
        Get company name.

        Example output:
            "Octopus Energy"
        """
        element = self.driver.find_element(
            By.XPATH,
            '//*[@id="main-content"]/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[1]/a',
        )
        company = element.text
        return company

    def get_location(self) -> str:
        """
        Get location.

        Example output:
            "Munich, Bavaria, Germany"
        """
        element = self.driver.find_element(
            By.XPATH,
            '//*[@id="main-content"]/section[1]/div/section[2]/div/div[1]/div/h4/div[1]/span[2]',
        )
        location = element.text
        return location
