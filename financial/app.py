import math
import time
from flask import Flask, request
import mysql.connector
import re

#internal imports
import constants

app = Flask(__name__)

dbConn = mysql.connector.connect(
    host = constants.DBHOST,
    user = constants.DBUSER,
    database = constants.DBNAME,
    password = constants.DBPASSWORD
)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

@app.get('/api/financial_data')
def getFinancialData():
    # endpoint params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    symbol = request.args.get('symbol')
    limit = request.args.get('limit')
    page = request.args.get('page')

    # input validation
    if start_date and not re.match(constants.DATE_PATTERN, start_date):
        response['info']['error'] = 'invalid start_date'
    if end_date and not re.match(constants.DATE_PATTERN, end_date):
        response['info']['error'] = 'invalid end_date'
    limit = 5 if not limit or not limit.isdigit() else int(limit)
    page = 0 if not page or not page.isdigit() else int(page)

    response = {
        'data': [],
        'pagination': {
            'count': 0,
            'page': page,
            'limit': limit,
            'pages': 1
        },
        'info': {'error': ''}
    }

    # fetch data from DB
    cursor = dbConn.cursor()
    # build and exec sql query
    sql = '''
        SELECT symbol, date, open_price, close_price, volume, COUNT(*) OVER()
        FROM financial_data
        WHERE (%s IS NULL OR symbol = %s) AND (%s IS NULL OR date >= %s) AND (%s IS NULL OR date <= %s)
        ORDER BY date
        LIMIT %s
        OFFSET %s
    '''
    cursor.execute(sql, (symbol, symbol, start_date, start_date, end_date, end_date, limit, page * limit))
    result = cursor.fetchall()
    for r in result:
        response['data'].append({
            "symbol": r[0],
            'date': r[1].isoformat(),
            "open_price": r[2],
            "close_price": r[3],
            "volume": str(r[4])
        })

    # populate pagination
    if cursor.rowcount > 0:
        response['pagination']['count'] = result[0][5]
        response['pagination']['pages'] = math.ceil(response['pagination']['count'] / limit) # round up to account for last page
    else:
        response['info']['error'] = f'No data found for symbol {symbol} from {start_date} to {end_date}'

    return response

@app.get('/api/statistics')
def getStatistics():
    # endpoint params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    symbol = request.args.get('symbol')

    response = {
        "data": {
            'start_date': start_date,
            'end_date': end_date,
            'symbol': symbol
        },
        'info': {'error': ''}
    }

    # input validation
    if not start_date or not end_date or not symbol:
        response['info']['error'] = 'start_date, end_date, and symbol are required parameters'
        return response
    if not re.match(constants.DATE_PATTERN, start_date) or not re.match(constants.DATE_PATTERN, end_date) or end_date < start_date:
        response['info']['error'] = 'invalid start_date/end_date'
        return response

    # fetch data from DB
    try:
        cursor = dbConn.cursor()
        # build and exec sql query
        sql = '''
            SELECT AVG(open_price), AVG(close_price), AVG(volume)
            FROM financial_data
            WHERE date >= %s AND date <= %s AND symbol = %s
        '''
        cursor.execute(sql, (start_date, end_date, symbol))
        result = cursor.fetchall()[0]

        # if we get None for average, we have no data for the stock during the period
        if not result[0]:
            response['info']['error'] = f'No stat found for {symbol} from {start_date} to {end_date}'
        else:
            response['data']['average_daily_open_price'] = f'{result[0]: .2f}'
            response['data']['average_daily_close_price'] = f'{result[1]: .2f}'
            response['data']['average_daily_volume'] = f'{result[2]: .0f}'

    except Exception as err:
        response['info']['error'] = f'Error encountered when exec query: {err}'

    return response