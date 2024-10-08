import os
import requests
import datetime
import urllib.parse
import mysql.connector
import json
import dotenv

def getAndInsertStockData(symbol: str, numDays: int):
    '''
    Get stock data for symbol in numDays and calls insertData to add these data into DB

            Parameters:
                    symbol (str): stock identifier
                    numDays (int): number of days to get data for the stock
    '''
    if not symbol or symbol == "" or numDays <= 0:
        print('Invalid input')
        return

    # build api call and make request
    apiUrl = 'https://www.alphavantage.co/query?'
    apiParams = {
        "function": "TIME_SERIES_DAILY",
        "outputsize": "compact",
        "symbol": symbol,
        "apikey": os.getenv('API_KEY')
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

def insertData(symbol: str, financialData: list):
    '''
    Insert data into DB

            Parameters:
                    symbol (str): stock identifier
                    financialData (list): list of financial data associated to the stock symbol

            Raises:
                    mysql.connector.Error: if DB interaction fails
    '''
    try:
        # use REPLACE instead of INSERT to make sure we do not insert duplicate entries
        cursor = dbConn.cursor()
        for data in financialData:
            dataValues = tuple(data.values())
            sql = "REPLACE INTO financial_data (symbol, date, open_price, close_price, volume) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, dataValues)
        dbConn.commit()
        print(f'{len(financialData)} entries inserted for symbol {symbol}')
    except mysql.connector.Error as err:
        raise err

# scirpt
dotenv.load_dotenv()
dbConn = mysql.connector.connect(
    host = os.getenv('DB_HOST'),
    user = os.getenv('DB_USER'),
    database = os.getenv('DB_NAME'),
    password = os.getenv('DB_PASSWORD')
)
getAndInsertStockData("IBM", 14)
getAndInsertStockData("AAPL", 14)
dbConn.close()