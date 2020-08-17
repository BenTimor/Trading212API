# Trading212 API
This is an **unofficial** selenium based API for 'Trading212' broker. 
**Neither me and neither Trading212 are responsible for the API, You are responsible for your actions and for using the API.**

Additionally, Note the Trading212 ['Robo Trading' agreement](https://www.trading212.com/en/robo-trading-agreement).

The API is still WIP, I don't know if and how it's going to work on your computer. But you're more than welcome ot open and issue and I'll try to help as much as I can.

## Requirements
- Python 3.x
- Selenium package
- GeckoDriver
- FireFox browser

## Installation
`pip install trading212`

## Import
CFD mode:

````
from Trading212 import CFD

trading = CFD(email, password) # For practice
trading = CFD(email, password, panel=Panel.Real) # For real money

````

Invest mode:

````
from Trading212 import Invest

trading = Invest(email, password) # For practice
trading = Invest(email, password, panel=Panel.Real) # For real money

````

## Usage
First of all, You have to know that the API currently uses the **display name** of the stocks.

#### Buying a stock ('Long')
`trading.buy_stock(stock, amount)`

#### Selling a stock ('Short')
`trading.sell_stock(stock, amount) # Available for CFD only`

#### Closing a position
`trading.close_position(stock)`

#### Getting a result of a position
`trading.result(stock)`

#### Getting another information of a position
`trading.position_info(css_class)`

You can get anything that's written in the bar. I've added a picture with source code so you'll be able to select the class.

![Classes](https://i.imgur.com/K05pRqs.png)