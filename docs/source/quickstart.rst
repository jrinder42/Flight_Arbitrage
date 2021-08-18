Flight Arbtrage
===============

This project adheres to `Semantic Versioning <https://semver.org/>`_

Install
-------

.. code-block:: bash

    pip install flight_arbitrage

Features
--------

- Parse plane tickets for arbitrage opportunities

- Scrape websites in a headless browser mode

Examples
--------

.. code-block:: python

    from flight_arbitrage.hidden_city import OneWay

    arbitrage = OneWay('JFK', 'SLC', '07/10/2021')
    a = arbitrage.find_arbitrage(headless=True)
    print(f'Is there an arbitrage opportunity: {len(a) > 0}')
    for d in a:
        print(d)

License
-------

Flight Arbitrage is MIT licensed, as found in the LICENSE file.

Todo
----

- Finish writing docs

- Incorporate readthedocs

    - Include automating doc updating

- Use pre-commit