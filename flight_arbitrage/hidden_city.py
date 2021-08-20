"""Find arbitrage in plane ticket prices"""

import re
import time
from typing import Tuple, DefaultDict, List, Union, Optional
from collections import defaultdict

from tqdm import tqdm  # type: ignore
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from flight_arbitrage.flight import Flight

ElementType = Optional[
    Union[
        webdriver.remote.webelement.WebElement,
        webdriver.firefox.webelement.FirefoxWebElement,
    ]
]
ElementsType = Union[
    List[webdriver.remote.webelement.WebElement],
    List[webdriver.firefox.webelement.FirefoxWebElement],
]


class OneWay(Flight):
    """Find arbitrage opportunities in one-way flights"""

    def generate_browser(self) -> None:
        """
        Opens a browser and goes to the expedia flights website

        :return: nothing
        """
        url = (
            f"https://www.expedia.com/Flights-Search?trip=oneway&leg1="
            f"from:{self.leaving_from},to:{self.going_to},"
            f"departure:{self.date}"
            f"TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y"
            f"&options=cabinclass%3Aeconomy&mode=search"
        )

        assert (
            self.browser is not None
        ), "browser variable is the wrong data type"

        try:
            self.browser.get(url)
        except Exception as error:
            raise ValueError(
                f"error opening up browser with error: {error}"
            ) from error

        time.sleep(2)

    @staticmethod
    def retrieve_element_by_xpath(base_object, context: str) -> ElementType:
        """
        Searches the site for a specific string -- context

        :param base_object: html parent tag object
        :param context: string to search
        :return: xpath object from selenium
        """
        searching: ElementType = None

        try:
            searching = base_object.find_element_by_xpath(context)
        except NoSuchElementException:
            pass

        return searching

    @staticmethod
    def empty_list() -> List[webdriver.firefox.webelement.FirefoxWebElement]:
        """
        Creates an empty list due to
            mypy issue: https://github.com/python/mypy/issues/6463
        The type in function 'retrieve_elements_by_xpath'
            variable 'searching' defaults to a firefox empty list

        :return: a default empty list to help work around a mypy bug
        """
        return []

    def retrieve_elements_by_xpath(
        self, base_object, context: str
    ) -> ElementsType:
        """
        Searches the site for a specific string -- context

        :param base_object: html parent tag object
        :param context: string to search
        :return: list of xpath object from selenium
        """
        # uses an extra function due to open mypy issue:
        #   https://github.com/python/mypy/issues/6463
        searching: ElementsType = self.empty_list()

        try:
            searching = base_object.find_element_by_xpath(context)
        except NoSuchElementException:
            pass

        return searching

    def cheapest_flight(
        self, tries: int = 3
    ) -> Tuple[float, DefaultDict[str, set]]:
        """
        Finds the cheapest flight that has an arbitrage

        :param tries: number of retries to load the site
        :return: the price (if a flight is found) and the flights
        """
        try_count = 0
        search = self.retrieve_elements_by_xpath(self.browser, self.offerings)

        departure_dict: DefaultDict[str, set] = defaultdict(set)
        while not search and try_count < tries:
            search = self.retrieve_elements_by_xpath(
                self.browser, self.offerings
            )

            try_count += 1
            time.sleep(1)

        if not search and tries == 3:
            return -1.0, departure_dict

        if search:
            for search_object in search:
                search_departure = self.retrieve_element_by_xpath(
                    search_object, "." + self.departure_time
                )
                if not search_departure:
                    continue

                search_price = self.retrieve_element_by_xpath(
                    search_object, "." + self.price
                )
                if not search_price:
                    continue

                return_price = float(
                    search_price.text[1:].replace(",", "").replace(".", "")
                )
                departure_location = search_departure.text.split("-")[
                    0
                ].strip()
                departure_dict[departure_location].add(return_price)

                return return_price, departure_dict

        return -1.0, departure_dict

    def find_arbitrage(
        self,
        override: bool = False,
        override_filename: str = "airports.txt",
        web_browser: str = "firefox",
        driver: str = "",
        headless: bool = False,
        tries: int = 3,
    ) -> list:
        """
        Iterates through all possible arbitrage opportunities

        :param override:
        :param override_filename:
        :param web_browser:
        :param driver:
        :param headless:
        :param tries:
        :return:

        >>> arbitrage = OneWay('JFK', 'SLC', '07/10/2021')
        >>> a = arbitrage.find_arbitrage(headless=True)
        >>> print(f'Is there an arbitrage opportunity: {len(a) > 0}')
        >>> for d in a:
        >>>     print(d)
        """
        self.open_browser(
            web_browser=web_browser, driver=driver, headless=headless
        )
        self.generate_browser()

        # have to have the below assert --> related to mypy issue:
        #   https://github.com/python/mypy/issues/5528
        assert (
            self.browser is not None
        ), "browser variable is the wrong data type"

        airports = self.airports_to_search(
            override=override, override_filename=override_filename
        )
        base, departure_dict = self.cheapest_flight()
        arbs = []

        for airport in tqdm(airports):
            if airport == self.leaving_from:
                continue

            url = (
                f"https://www.expedia.com/Flights-Search?trip="
                f"oneway&leg1=from:{self.leaving_from},"
                f"to:{airport},departure:{self.date}"
                f"TANYT&passengers=adults:1,children:0,seniors:0,"
                f"infantinlap:Y&options=cabinclass%3Aeconomy&mode=search"
            )

            try:
                self.browser.get(url)
            except Exception as error:
                print(f"error opening up browser with error: {error}")
                return []

            time.sleep(2)

            try_count = 0
            search = self.retrieve_elements_by_xpath(
                self.browser, self.offerings
            )

            while not search and try_count < tries:
                search = self.retrieve_elements_by_xpath(
                    self.browser, self.offerings
                )

                try_count += 1
                time.sleep(1)

            lowest_ticket = []
            bad_count = 0
            for search_object in search:
                new_searches = self.retrieve_element_by_xpath(
                    search_object, "." + self.layovers
                )
                if not new_searches:
                    bad_count += 1
                    continue
                find_all = re.findall(r"\(.*?\)", new_searches.text)
                stops = [location.strip("()") for location in find_all]

                price_found = self.retrieve_element_by_xpath(
                    search_object, "." + self.price
                )
                if not price_found:
                    bad_count += 1
                    continue

                ticket_price = float(
                    price_found.text[1:].replace(",", "").replace(".", "")
                )
                if ticket_price < base and self.going_to in stops:
                    print("arbitrage with destination:", airport)

                    departure = self.retrieve_element_by_xpath(
                        search_object, "." + self.departure_time
                    )
                    if not departure:
                        continue
                    departure_value = departure.text.split("-")[0].strip()

                    evaluation_price = base
                    if not departure_dict[departure_value]:
                        savings = base - ticket_price
                    else:
                        evaluation_price = min(departure_dict[departure_value])
                        savings = (
                            min(departure_dict[departure_value]) - ticket_price
                        )
                    arbs.append(
                        {
                            "airport destination": self.going_to,
                            "airport source": self.leaving_from,
                            "base price": base,
                            "this ticket price": ticket_price,
                            "eval price": evaluation_price,
                            "this destination": airport,
                            "savings": savings,
                        }
                    )
                lowest_ticket.append(ticket_price)

            if search and len(search) != bad_count:
                print(
                    f"done with airport: {airport} | "
                    f"cheapest ticket with layovers: {min(lowest_ticket)}"
                )
            else:
                print(
                    f"done with airport: {airport} | "
                    f"no available flights from {self.leaving_from}"
                    f" to {airport}"
                )

            time.sleep(2)

        self.browser.quit()

        return arbs
