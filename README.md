## Flight Arbtrage

[![PyPI Version][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Code Coverage][coverage-image]][coverage-url]
[![Code Quality][quality-image]][quality-url]
![Python Versions](assets/img/python_versions.svg)
![Platform Badge](assets/img/platforms.svg)


<!-- Badges -->

[pypi-image]: assets/img/pypi.svg
[pypi-url]: https://pypi.org/project/flight_arbitrage/
[build-image]: https://github.com/jrinder42/Flight_Arbitrage/actions/workflows/build.yml/badge.svg
[build-url]: https://github.com/jrinder42/Flight_Arbitrage/actions/workflows/build.yml
[coverage-image]: https://codecov.io/gh/jrinder42/Flight_Arbitrage/branch/main/graph/badge.svg
[coverage-url]: https://codecov.io/gh/jrinder42/Flight_Arbitrage
[quality-image]: https://api.codeclimate.com/v1/badges/85937031d4258ed2909a/maintainability
[quality-url]: https://codeclimate.com/github/jrinder42/Flight_Arbitrage

This project adheres to [Semantic Versioning](https://semver.org/)

### Install
```bash
pip install flight_arbitrage
```

### Features

- Parse plane tickets for arbitrage opportunities

- Scrape websites in a headless browser mode

### Examples
```python
from flight_arbitrage.hidden_city import OneWay

arbitrage = OneWay('JFK', 'SLC', '07/10/2021')
a = arbitrage.find_arbitrage(headless=True)
print(f'Is there an arbitrage opportunity: {len(a) > 0}')
for d in a:
    print(d)
```
### License
Flight Arbitrage is MIT licensed, as found in the LICENSE file.

### Todo

- Finish writing docs

- Incorporate readthedocs

    - Include automating doc updating

- Use pre-commit

- Fix code coverage upload to only ubuntu 3.9

