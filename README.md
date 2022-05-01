# Uniswap v2 Price Listener

This code simply gets all pairs generated from Uniswap Factory v2 (0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f), gets it's basic information and then listens for events on those pairs.
If any pair emits an event we see if price has changed if so we emit it to a socket.

It also has a minimal Flask app that has an index.html to consumes the events emited through Socket.io acting as a built in client.

Information we have gathered for each pair is the following:

- Token Symbol
- Decimals
- Address
- Price (calculated from reserves, ie, ratio between tokens of the pair token0reserves/token1reserves)

For simplicity sake, it will check on ehtereum mainnet through a free account with infura.

JSON ABI's copied from etherscan.

Factory ABI: https://etherscan.io/address/0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f#code

Pair ABI: https://etherscan.io/address/0x3139Ffc91B99aa94DA8A2dc13f1fC36F9BDc98eE#code

## How to run the program?

Simply `docker-compose build` and `docker-compose app up`. That should initiate the listening process and expose to localhost the website so simply accesing localhost:80 should be enough while running this docker container to see the pairs loading and the price updates afterwards.

If you wish to run tests, `docker-compose run tests` or `poetry run pytest`.

To install the code locally you will need poetry (https://python-poetry.org/) installed as this is my prefered way to manage dependencies in Python.


## TODO's

- Make the page nicer!
- Few Dockerfile optimizations
