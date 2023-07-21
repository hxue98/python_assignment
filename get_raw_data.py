import requests
import datetime
import urllib.parse
import mysql.connector
import json

# internal imports
import constants

def getStockData(symbol: str, numDays: int) -> None:
    if not symbol or symbol == "" or numDays <= 0:
        print('Invalid input')
        return

    # build api call and make request
    apiUrl = 'https://www.alphavantage.co/query?'
    apiParams = {
        "function": "TIME_SERIES_DAILY",
        "outputsize": "compact",
        "symbol": symbol,
        "apikey": constants.apiKey
    }
    r = requests.get(apiUrl + urllib.parse.urlencode(apiParams))
    data = r.json()

    # check if response has error
    if ('Error Message' in data):
        print(f'Stock symbol {symbol} not found')
        return

    # extract open price, close price, and volume for 2 weeks
    today = datetime.datetime.today().date()
    twoWeeksAgo = (today - datetime.timedelta(days = 14)).isoformat()

    timeSeriesData = data["Time Series (Daily)"]
    financialData = list()
    for _, k in enumerate(timeSeriesData):
        if k < twoWeeksAgo: break
        dailyData = list(timeSeriesData[k].values())
        financialData.append({
            "symbol": symbol,
            "date": k,
            "open_price": dailyData[0],
            "close_price": dailyData[3],
            "volume": dailyData[4]
        })
    print(json.dumps(financialData, indent=4))

    # insert data into financial_data table
    try:
        insertData(symbol, financialData)
    except Exception as err:
        print(f'Error encountered when inserting data: {err}')


def insertData(symbol: str, financialData: list) -> Exception:
    try:
        # connect DB
        dbConn = mysql.connector.connect(
            host = constants.dbHost,
            user = constants.dbUser,
            database = constants.dbName,
            password = constants.dbPassword
        )

        # use REPLACE instead of INSERT to make sure we do not insert duplicate entries
        mycursor = dbConn.cursor()
        for data in financialData:
            dataValues = list(data.values())
            sql = "REPLACE INTO financial_data (symbol, date, open_price, close_price, volume) VALUES (%s, %s, %s, %s, %s)"
            val = (dataValues[0], dataValues[1], dataValues[2], dataValues[3], dataValues[4])
            mycursor.execute(sql, val)
        dbConn.commit()
        print(f'{len(financialData)} entries inserted for symbol {symbol}')
    except mysql.connector.Error as err:
        raise err


# scirpt
getStockData("IBM", 14)
getStockData("AAPL", 14)