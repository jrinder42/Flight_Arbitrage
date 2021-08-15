"""Unit test file for the Flight class"""

import unittest
from unittest.mock import patch

from flight_arbitrage.flight import Flight


class TestFlight(unittest.TestCase):
    """Unit tests for the Flight class"""

    def setUp(self):
        """
        Create the initial class object for use in each unit test

        :return: nothing
        """
        self.flight = Flight("start_airport", "end_airport", "date")

    @patch("flight_arbitrage.flight.ChromeOptions")
    @patch("flight_arbitrage.flight.webdriver")
    def test_open_chrome(self, mocked_webdriver, mocked_options):
        """
        Opening a chrome driver using selenium

        :param mocked_webdriver: a mocked selenium webdriver object
        :param mocked_options: a mocked function for Chrome driver options
        :return: nothing
        """
        # headless is False
        path = "path"

        self.flight.open_chrome(driver=path)

        mocked_webdriver.Chrome.assert_called_once_with(executable_path="path")

        # headless is True
        headless = True

        self.flight.open_chrome(driver=path, headless=headless)

        mocked_options.add_argument("--headless")
        mocked_options.add_argument.assert_called_once_with("--headless")
        self.assertEqual(mocked_webdriver.Chrome.call_count, 2)
        mocked_webdriver.Chrome.assert_called_with(
            executable_path="path", options=mocked_options()
        )

    @patch("flight_arbitrage.flight.FirefoxOptions")
    @patch("flight_arbitrage.flight.webdriver")
    def test_open_firefox(self, mocked_webdriver, mocked_options):
        """

        :param mocked_webdriver:
        :param mocked_options:
        :return:
        """
        # headless is False
        self.flight.open_firefox()

        mocked_webdriver.Firefox.assert_called_once_with()

        # headless is True
        headless = True

        self.flight.open_firefox(headless=headless)

        mocked_options.add_argument("--headless")
        mocked_options.add_argument.assert_called_once_with("--headless")
        self.assertEqual(mocked_webdriver.Firefox.call_count, 2)
        mocked_webdriver.Firefox.assert_called_with(options=mocked_options())

    @patch("flight_arbitrage.flight.webdriver")
    def test_open_safari(self, mocked_webdriver):
        """

        :param mocked_webdriver:
        :return:
        """
        # headless is False
        path = "path"

        self.flight.open_safari(driver=path)

        mocked_webdriver.Safari.assert_called_once_with(executable_path="path")

        # headless is True
        headless = True

        self.flight.open_safari(driver=path, headless=headless)

        self.assertEqual(mocked_webdriver.Safari.call_count, 2)
        mocked_webdriver.Safari.assert_called_with(executable_path="path")

    @patch("flight_arbitrage.flight.webdriver")
    def test_open_edge(self, mocked_webdriver):
        """

        :param mocked_webdriver:
        :return:
        """
        # headless is False
        path = "path"

        self.flight.open_edge(driver=path)

        mocked_webdriver.Edge.assert_called_once_with(executable_path="path")

        # headless is True
        headless = True

        self.flight.open_edge(driver=path, headless=headless)

        self.assertEqual(mocked_webdriver.Edge.call_count, 2)
        mocked_webdriver.Edge.assert_called_with(executable_path="path")

    def test_open_browser_bad_exception(self):
        """

        :return:
        """
        # bad browser
        with self.assertRaises(Exception):
            self.flight.open_browser(web_browser="browser")

    @patch("flight_arbitrage.flight.Flight.open_edge")
    @patch("flight_arbitrage.flight.Flight.open_safari")
    @patch("flight_arbitrage.flight.Flight.open_firefox")
    @patch("flight_arbitrage.flight.Flight.open_chrome")
    @patch("flight_arbitrage.flight.time")
    def test_open_browser_good(
        self,
        mocked_time,
        mocked_chrome,
        mocked_firefox,
        mocked_safari,
        mocked_edge,
    ):
        """

        :param mocked_time:
        :param mocked_chrome:
        :param mocked_firefox:
        :param mocked_safari:
        :param mocked_edge:
        :return:
        """
        # chrome
        self.flight.open_browser(
            web_browser="chrome", driver="path", headless=False
        )

        mocked_time.sleep.assert_called_once_with(2)
        mocked_chrome.assert_called_once_with(driver="path", headless=False)

        # firefox
        self.flight.open_browser(web_browser="firefox", headless=False)

        mocked_time.sleep.assert_called_with(2)
        self.assertEqual(mocked_time.sleep.call_count, 2)
        mocked_firefox.assert_called_once_with(headless=False)

        # safari
        self.flight.open_browser(
            web_browser="safari", driver="path", headless=False
        )

        mocked_time.sleep.assert_called_with(2)
        self.assertEqual(mocked_time.sleep.call_count, 3)
        mocked_safari.assert_called_once_with(driver="path", headless=False)

        # edge
        self.flight.open_browser(
            web_browser="edge", driver="path", headless=False
        )

        mocked_time.sleep.assert_called_with(2)
        self.assertEqual(mocked_time.sleep.call_count, 4)
        mocked_edge.assert_called_once_with(driver="path", headless=False)

    @patch("flight_arbitrage.flight.requests.get")
    def test_airports_to_search_bad_request_status(self, mocked_get):
        """

        :param mocked_get:
        :return:
        """
        mocked_get.return_value.status_code = 201

        with self.assertRaises(ValueError):
            self.flight.airports_to_search()

        self.assertEqual(mocked_get.call_count, 1)

    @patch("flight_arbitrage.flight.requests.get")
    def test_airports_to_search_bad_request_exception(self, mocked_get):
        """

        :param mocked_get:
        :return:
        """
        mocked_get.side_effect = Exception()

        with self.assertRaises(ValueError):
            self.flight.airports_to_search()

        self.assertEqual(mocked_get.call_count, 1)

    @patch("flight_arbitrage.flight.BeautifulSoup")
    @patch("flight_arbitrage.flight.requests.get")
    def test_airports_to_search_good_request(self, mocked_get, mocked_bs4):
        """

        :param mocked_get:
        :param mocked_bs4:
        :return:
        """
        url = (
            "https://en.wikipedia.org/wiki/List_of_the_"
            "busiest_airports_in_the_United_States"
        )
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.text = "airport list"

        mocked_rows = unittest.mock.MagicMock()
        mocked_row = unittest.mock.MagicMock()

        mocked_cells = unittest.mock.MagicMock()
        mocked_cells.__getitem__.return_value.string.strip.side_effect = [
            "major airport",
            "minor airport",
        ]

        mocked_row.findChildren.return_value = mocked_cells
        mocked_rows.findChildren.return_value = [
            unittest.mock.MagicMock(),
            mocked_row,
        ]

        mocked_bs4.return_value.findChildren.side_effect = [
            [mocked_rows, mocked_rows]
        ]

        result = self.flight.airports_to_search()

        mocked_get.assert_called_once_with(url)

        mocked_bs4.assert_called_once_with("airport list", features="lxml")
        mocked_bs4.return_value.findChildren.assert_called_once_with("table")

        mocked_rows.findChildren.assert_any_call(["tr"])
        self.assertTrue(mocked_rows.findChildren.call_count, 2)
        mocked_row.findChildren.assert_any_call("td")
        self.assertTrue(mocked_row.findChildren.call_count, 2)

        self.assertEqual(result, ["major airport", "minor airport"])

    @patch("builtins.open")
    def test_airports_to_search_custom_airports(self, mocked_open):
        """

        :param mocked_open:
        :return:
        """
        mocked_open.return_value.__enter__.return_value = [
            " airport1",
            "airport2 ",
        ]

        result = self.flight.airports_to_search(
            override=True, override_filename="filename"
        )
        expected_result = ["airport1", "airport2"]

        mocked_open.assert_called_once_with("filename", "r")
        self.assertTrue(result, expected_result)

        result = self.flight.airports_to_search(override=True)
        expected_result = ["airport1", "airport2"]

        mocked_open.assert_called_with("airports.txt", "r")
        self.assertEqual(mocked_open.call_count, 2)
        self.assertEqual(result, expected_result)


if __name__ == "__main__":

    unittest.main()
