"""Unit test file for the OneWay class"""

import unittest
from unittest.mock import patch

from selenium.common.exceptions import NoSuchElementException

from flight_arbitrage.hidden_city import OneWay


class TestOneWay(unittest.TestCase):
    """Unit tests for the OneWay class"""

    def setUp(self):
        """

        :return:
        """
        self.flight = OneWay("start_airport", "end_airport", "date")

    def test_generate_browser_bad_assert(self):
        """

        :return:
        """
        with self.assertRaises(AssertionError):
            self.flight.generate_browser()

    def test_generate_browser_bad_exception(self):
        """

        :return:
        """
        with self.assertRaises(ValueError):
            with patch.object(self.flight, "browser", 0):
                self.flight.generate_browser()

    # https://stackoverflow.com/questions/60515794/mocking-instance-attributes
    @patch("flight_arbitrage.hidden_city.time")
    def test_generate_browser_good(self, mocked_time):
        """

        :param mocked_time:
        :return:
        """
        url = (
            "https://www.expedia.com/Flights-Search?trip=oneway&leg1="
            "from:start_airport,to:end_airport,"
            "departure:dateTANYT&passengers="
            "adults:1,children:0,seniors:0,infantinlap:Y"
            "&options=cabinclass%3Aeconomy&mode=search"
        )

        with patch.object(
            self.flight, "browser", unittest.mock.Mock()
        ) as mocked_browser:
            self.flight.generate_browser()

        mocked_browser.get.assert_called_once_with(url)
        mocked_time.sleep.assert_called_once_with(2)

    def test_retrieve_element_by_xpath(self):
        """

        :return:
        """
        base_object = unittest.mock.Mock()
        base_object.find_element_by_xpath.side_effect = [
            NoSuchElementException(),
            "element 1",
        ]

        results = []
        for _ in range(2):
            result = self.flight.retrieve_element_by_xpath(
                base_object, "context"
            )
            results.append(result)
            base_object.find_element_by_xpath.assert_called_with("context")

        self.assertTrue(None in results)
        self.assertTrue("element 1" in results)
        self.assertEqual(base_object.find_element_by_xpath.call_count, 2)

    def test_retrieve_elements_by_xpath(self):
        """

        :return:
        """
        base_object = unittest.mock.Mock()
        base_object.find_element_by_xpath.side_effect = [
            NoSuchElementException(),
            ["element 1", "element 2"],
        ]

        results = []
        for _ in range(2):
            result = self.flight.retrieve_elements_by_xpath(
                base_object, "context"
            )
            results.append(result)
            base_object.find_element_by_xpath.assert_called_with("context")

        self.assertTrue([] in results)
        self.assertTrue(["element 1", "element 2"] in results)
        self.assertEqual(base_object.find_element_by_xpath.call_count, 2)

    @patch("flight_arbitrage.hidden_city.time")
    @patch("flight_arbitrage.hidden_city.OneWay.retrieve_elements_by_xpath")
    def test_cheapest_flight_bad_search(self, mocked_rxpath, mocked_time):
        """

        :param mocked_rxpath:
        :param mocked_time:
        :return:
        """
        mocked_rxpath.side_effect = [[], [], [], [], [], []]

        result = self.flight.cheapest_flight()

        self.assertEqual(result[0], -1)
        self.assertTrue(isinstance(result[0], float))
        self.assertTrue(isinstance(result[1], dict))

        mocked_rxpath.assert_called_with(
            None, '//li[@data-test-id="offer-listing"]'
        )
        self.assertEqual(mocked_rxpath.call_count, 4)
        mocked_time.sleep.assert_called_with(1)
        self.assertEqual(mocked_time.sleep.call_count, 3)

    @patch("flight_arbitrage.hidden_city.OneWay.retrieve_elements_by_xpath")
    @patch("flight_arbitrage.hidden_city.OneWay.retrieve_element_by_xpath")
    def test_cheapest_flight_good_search_empty(
        self, mocked_rxpath_element, mocked_rxpath_elements
    ):
        """

        :param mocked_rxpath_element:
        :param mocked_rxpath_elements:
        :return:
        """
        departure_time = '//span[@data-test-id="departure-time"]'
        price = '//span[@class="uitk-lockup-price"]'

        mocked_rxpath_elements.side_effect = [["element 1", "element 2"]]
        mocked_rxpath_element.side_effect = ["", "search_departure", ""]

        result = self.flight.cheapest_flight()

        self.assertEqual(result[0], -1)
        self.assertTrue(isinstance(result[0], float))
        self.assertTrue(isinstance(result[1], dict))

        mocked_rxpath_elements.assert_called_once_with(
            None, '//li[@data-test-id="offer-listing"]'
        )
        calls = [
            unittest.mock.call("element 1", "." + departure_time),
            unittest.mock.call("element 2", "." + departure_time),
            unittest.mock.call("element 2", "." + price),
        ]
        mocked_rxpath_element.assert_has_calls(calls, any_order=False)
        self.assertEqual(mocked_rxpath_element.call_count, len(calls))

    @patch("flight_arbitrage.hidden_city.OneWay.retrieve_elements_by_xpath")
    @patch("flight_arbitrage.hidden_city.OneWay.retrieve_element_by_xpath")
    def test_cheapest_flight_good_search_full(
        self, mocked_rxpath_element, mocked_rxpath_elements
    ):
        """

        :param mocked_rxpath_element:
        :param mocked_rxpath_elements:
        :return:
        """
        departure_time = '//span[@data-test-id="departure-time"]'
        price = '//span[@class="uitk-lockup-price"]'

        mocked_departure = unittest.mock.MagicMock()
        mocked_departure.text.split().__getitem__.return_value = "location"
        mocked_price = unittest.mock.MagicMock()
        mocked_price.text.__getitem__.return_value = "58"
        mocked_rxpath_elements.side_effect = [
            ["element 1", "element 2", "element 3"]
        ]
        mocked_rxpath_element.side_effect = [
            "",
            "search_departure",
            "",
            mocked_departure,
            mocked_price,
        ]

        result = self.flight.cheapest_flight()

        self.assertEqual(result[0], 58)
        self.assertTrue(isinstance(result[0], float))
        self.assertTrue(isinstance(result[1], dict))
        self.assertEqual(result[1], {"location": {58}})

        mocked_rxpath_elements.assert_called_once_with(
            None, '//li[@data-test-id="offer-listing"]'
        )
        calls = [
            unittest.mock.call("element 1", "." + departure_time),
            unittest.mock.call("element 2", "." + departure_time),
            unittest.mock.call("element 2", "." + price),
            unittest.mock.call("element 3", "." + departure_time),
            unittest.mock.call("element 3", "." + price),
        ]
        mocked_rxpath_element.assert_has_calls(calls, any_order=False)
        self.assertEqual(mocked_rxpath_element.call_count, len(calls))

    @patch("flight_arbitrage.hidden_city.tqdm")
    @patch("flight_arbitrage.hidden_city.OneWay.cheapest_flight")
    @patch("flight_arbitrage.hidden_city.OneWay.airports_to_search")
    @patch("flight_arbitrage.hidden_city.OneWay.generate_browser")
    @patch("flight_arbitrage.hidden_city.OneWay.open_browser")
    def test_find_arbitrage_exception(
        self,
        mocked_open,
        mocked_generate,
        mocked_search,
        mocked_cheapest,
        mocked_tqdm,
    ):
        """

        :param mocked_open:
        :param mocked_generate:
        :param mocked_search:
        :param mocked_cheapest:
        :param mocked_tqdm:
        :return:
        """
        mocked_search.return_value = ["airport 1", "airport 2"]
        mocked_cheapest.return_value = [
            100,
            {"location": {58}},
        ]  # base, departure_dict
        mocked_tqdm.return_value = mocked_search.return_value

        with patch.object(
            self.flight, "browser", unittest.mock.Mock()
        ) as mocked_browser:
            mocked_browser.get.side_effect = Exception()

            result = self.flight.find_arbitrage()

        mocked_open.assert_called_once_with(
            web_browser="firefox", driver="", headless=False
        )
        mocked_generate.assert_called_once_with()
        mocked_search.assert_called_once_with(
            override=False, override_filename="airports.txt"
        )
        mocked_cheapest.assert_called_once_with()
        mocked_tqdm.assert_called_once_with(["airport 1", "airport 2"])
        self.assertEqual(result, [])

    @patch("flight_arbitrage.hidden_city.re")
    @patch("flight_arbitrage.hidden_city.time")
    @patch("flight_arbitrage.hidden_city.tqdm")
    @patch("flight_arbitrage.hidden_city.OneWay.retrieve_elements_by_xpath")
    @patch("flight_arbitrage.hidden_city.OneWay.retrieve_element_by_xpath")
    @patch("flight_arbitrage.hidden_city.OneWay.cheapest_flight")
    @patch("flight_arbitrage.hidden_city.OneWay.airports_to_search")
    @patch("flight_arbitrage.hidden_city.OneWay.generate_browser")
    @patch("flight_arbitrage.hidden_city.OneWay.open_browser")
    def test_find_arbitrage(
        self,
        mocked_open,
        mocked_generate,
        mocked_search,
        mocked_cheapest,
        mocked_rxpath_element,
        mocked_rxpath_elements,
        mocked_tqdm,
        mocked_time,
        mocked_re,
    ):
        """

        :param mocked_open:
        :param mocked_generate:
        :param mocked_search:
        :param mocked_cheapest:
        :param mocked_rxpath_element:
        :param mocked_rxpath_elements:
        :param mocked_tqdm:
        :param mocked_time:
        :param mocked_re:
        :return:
        """
        departure_time = '//span[@data-test-id="departure-time"]'
        price = '//span[@class="uitk-lockup-price"]'
        layovers = '//div[@data-test-id="layovers"]'

        mocked_search.return_value = [
            "start_airport",
            "airport_2",
            "airport_3",
        ]
        mocked_cheapest.return_value = [
            100,
            {"location": {60}, "olympics": {}},
        ]  # base, departure_dict
        mocked_tqdm.return_value = mocked_search.return_value

        mocked_new_searches = unittest.mock.MagicMock()
        mocked_new_searches.text = "new search"
        mocked_re.findall.return_value = ["stop 1", "stop 2", "end_airport"]
        mocked_departure = unittest.mock.MagicMock()  # can handle slicing
        mocked_departure.text.split().__getitem__.side_effect = [
            "location",
            "olympics",
        ]
        mocked_price = unittest.mock.MagicMock()  # can handle slicing
        mocked_price.text.__getitem__.side_effect = ["99", "58", "58"]
        mocked_rxpath_elements.side_effect = [
            [],
            ["element 1", "element 2", "element 3", "element 4", "element 5"],
            ["element 6"],
        ]
        mocked_rxpath_element.side_effect = [
            "",
            mocked_new_searches,
            "",
            mocked_new_searches,
            mocked_price,
            "",
            mocked_new_searches,
            mocked_price,
            mocked_departure,
            mocked_new_searches,
            mocked_price,
            mocked_departure,
            "",
        ]
        url = (
            "https://www.expedia.com/Flights-Search?trip=oneway&"
            "leg1=from:start_airport,to:airport_2,"
            "departure:dateTANYT&passengers=adults:1,children:0,seniors:0"
            ",infantinlap:Y"
            "&options=cabinclass%3Aeconomy&mode=search"
        )

        with patch.object(
            self.flight, "browser", unittest.mock.Mock()
        ) as mocked_browser:
            result = self.flight.find_arbitrage()

        mocked_browser.get.assert_any_call(url)
        self.assertEqual(mocked_browser.get.call_count, 2)

        expected_result = [
            {
                "airport destination": "end_airport",
                "airport source": "start_airport",
                "base price": 100,
                "this ticket price": 58.0,
                "eval price": 60,
                "this destination": "airport_2",
                "savings": 2.0,
            },
            {
                "airport destination": "end_airport",
                "airport source": "start_airport",
                "base price": 100,
                "this ticket price": 58.0,
                "eval price": 100,
                "this destination": "airport_2",
                "savings": 42.0,
            },
        ]
        self.assertEqual(result, expected_result)

        mocked_open.assert_called_once_with(
            web_browser="firefox", driver="", headless=False
        )
        mocked_generate.assert_called_once_with()
        mocked_search.assert_called_once_with(
            override=False, override_filename="airports.txt"
        )
        mocked_cheapest.assert_called_once_with()
        mocked_tqdm.assert_called_once_with(
            ["start_airport", "airport_2", "airport_3"]
        )

        calls = [
            unittest.mock.call(2),
            unittest.mock.call(1),
            unittest.mock.call(2),
            unittest.mock.call(2),
            unittest.mock.call(2),
        ]
        mocked_time.sleep.assert_has_calls(calls, any_order=False)
        self.assertTrue(mocked_time.sleep.call_count, len(calls))

        mocked_re.findall.assert_any_call(r"\(.*?\)", "new search")
        self.assertTrue(mocked_re.findall.call_count, 4)

        mocked_rxpath_elements.assert_any_call(
            mocked_browser, '//li[@data-test-id="offer-listing"]'
        )
        self.assertTrue(mocked_rxpath_elements.call_count, 3)
        calls = [
            unittest.mock.call("element 1", "." + layovers),
            unittest.mock.call("element 2", "." + layovers),
            unittest.mock.call("element 2", "." + price),
            unittest.mock.call("element 3", "." + layovers),
            unittest.mock.call("element 3", "." + price),
            unittest.mock.call("element 3", "." + departure_time),
            unittest.mock.call("element 4", "." + layovers),
            unittest.mock.call("element 4", "." + price),
            unittest.mock.call("element 4", "." + departure_time),
            unittest.mock.call("element 5", "." + layovers),
            unittest.mock.call("element 5", "." + price),
            unittest.mock.call("element 5", "." + departure_time),
            unittest.mock.call("element 6", "." + layovers),
        ]
        mocked_rxpath_element.assert_has_calls(calls, any_order=False)
        self.assertTrue(mocked_rxpath_element.call_count, len(calls))

        mocked_browser.quit.assert_called_once_with()


if __name__ == "__main__":

    unittest.main()
