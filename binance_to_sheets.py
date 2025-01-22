import gspread, schedule, time
from binance.client import Client
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

## Crypto Requests ##
api_key = "123"
api_secret = "123"

client = Client(api_key, api_secret)
prices = {}
user_portfolio = {}

def updatePrices():
    ticker_info = client.get_all_tickers()
    for ticker in ticker_info:
        prices[ticker["symbol"]] = ticker["price"]

def getUserPortfolio():
    info = client.get_account()
    for coin in info['balances']:
        if float(coin['free']) > 0.00:
            user_portfolio[coin["asset"]] = float(coin['free'])

## Crypto Requests ##
def updateSheets():
    updatePrices()
    getUserPortfolio()

    ## Sheets ##
    #credentials to the account
    cred = ServiceAccountCredentials.from_json_keyfile_name('gprices-sheets-config.json') 
    # authorize the clientsheet 
    client = gspread.authorize(cred)
    sheet = client.open("Personal Finance").get_worksheet_by_id(123)

    for x in range(2,len(user_portfolio)+2):
        # update with coin name
        coin = [*user_portfolio.keys()][x-2]
        sheet.update_cell(x,1,coin)
        # # update with balance of coin
        balance = [*user_portfolio.values()][x-2]
        sheet.update_cell(x,2,balance)
        # update with price of balance in busd
        if coin == "USDT" or coin == "BUSD":
            sheet.update_cell(x,3,balance)
        elif coin == "ETHW":
            sheet.update_cell(x,3,0)
        else:
            price_in_busd = float([*user_portfolio.values()][x-2])*float(prices[([*user_portfolio.keys()][x-2])+("BUSD")])
            sheet.update_cell(x,3,price_in_busd)

    # also update nexo to usdt for staking sheet to update
    sheet.update_cell(2,7,prices["NEXOUSDT"])
    sheet.update_cell(12,4,datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

    ## Sheets ##

# updateSheets()

schedule.every(2).hours.do(updateSheets)
while True:
    schedule.run_pending()
    time.sleep(1)
