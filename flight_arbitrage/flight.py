"""Creates flight data scraping object"""

import time
from typing import List, Union

import requests
from bs4 import BeautifulSoup  # type: ignore
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class Flight:
    """Handle browser scraping"""

    def __init__(self, leaving_from: str, going_to: str, date: str) -> None:
        """
        Flight constructor

        :param leaving_from: airport where the flight originates
        :param going_to: airport that is the flight destination
        :param date: date of flight
        """
        self.leaving_from = leaving_from
        self.going_to = going_to
        self.date = date

        self.browser: Union[
            webdriver.Chrome,
            webdriver.Firefox,
            webdriver.Safari,
            webdriver.Edge,
            None,
        ] = None

        self.price = '//span[@class="uitk-lockup-price"]'
        self.layovers = '//div[@data-test-id="layovers"]'
        self.offerings = '//li[@data-test-id="offer-listing"]'
        self.departure_time = '//span[@data-test-id="departure-time"]'

    def open_chrome(self, driver: str = "", headless: bool = False) -> None:
        """
        Open the chrome browser

        :param driver: chrome driver file path
        :param headless: headless browser mode
        :return: nothing
        """
        if headless:
            options = ChromeOptions()
            options.add_argument("--headless")
            self.browser = webdriver.Chrome(
                executable_path=driver, options=options
            )
        else:
            self.browser = webdriver.Chrome(executable_path=driver)

    def open_firefox(self, headless: bool = False) -> None:
        """
        Open the firefox browser

        :param headless: headless browser mode
        :return: nothing
        """
        if headless:
            options = FirefoxOptions()
            options.add_argument("--headless")
            self.browser = webdriver.Firefox(options=options)
        else:
            self.browser = webdriver.Firefox()

    def open_safari(self, driver: str = "", headless: bool = False) -> None:
        """
        Open the safari browser

        :param driver: safari driver file path
        :param headless: headless browser mode
        :return: nothing
        """
        if headless:
            print(
                "sorry, headless is not available with "
                "safari in selenium at this moment"
            )
        self.browser = webdriver.Safari(executable_path=driver)

    def open_edge(self, driver: str = "", headless: bool = False) -> None:
        """
        Open the edge browser

        :param driver: edge driver file path
        :param headless: headless browser mode
        :return: nothing
        """
        if headless:
            print(
                "sorry, headless is not available with edge in "
                "selenium at this moment (well it kinda is)"
            )
        self.browser = webdriver.Edge(executable_path=driver)

    def open_browser(
        self,
        web_browser: str = "firefox",
        driver: str = "",
        headless: bool = False,
    ) -> None:
        """
        Opens a browser based on user-defined parameters

        :param web_browser: web browser to open
        :param driver: web browser driver file path
        :param headless: headless browser mode
        :return: nothing
        """
        web_browser = web_browser.lower()
        if web_browser == "chrome":
            self.open_chrome(driver=driver, headless=headless)
        elif web_browser == "edge":
            self.open_edge(driver=driver, headless=headless)
        elif web_browser == "firefox":
            self.open_firefox(headless=headless)
        elif web_browser == "safari":
            self.open_safari(driver=driver, headless=headless)
        else:
            raise Exception(f"web browser {web_browser} is not available")

        time.sleep(2)

    @staticmethod
    def airports_to_search(
        override: bool = False, override_filename: str = "airports.txt"
    ) -> List[str]:
        """
        Creates list of airports to iterate through

        :param override: indicating whether the user will use a custom file
        :param override_filename: the path/filename of the custom airport list
        :return: a list of airports to iterate through
        """
        if override:
            with open(override_filename, "r") as file:
                airports = [line.strip() for line in file]
            return airports

        url = (
            "https://en.wikipedia.org/wiki/List_of_the_busiest_"
            "airports_in_the_United_States"
        )
        try:
            response = requests.get(url)
            if response.status_code == 200:
                response_text = response.text
            else:
                raise ValueError(
                    f"did not return the correct response: "
                    f"{response.status_code}"
                )
        except Exception as error:
            raise ValueError(
                f"something went wrong with the url pull: {error}"
            ) from error

        airports = []
        soup = BeautifulSoup(response_text, features="lxml")
        tables = soup.findChildren("table")
        for airport_table in [tables[0], tables[1]]:
            rows = airport_table.findChildren(["tr"])
            for i, row in enumerate(rows):
                if i == 0:
                    continue

                cells = row.findChildren("td")
                airports.append(cells[2].string.strip("\n"))

        return airports
