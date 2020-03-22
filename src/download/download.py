import yfinance as yf


def handler(event, context):

    stock = yf.Ticker(event['ticker'])

    data = stock.history(
        period='1mo',
        interval='1d',
    )

    for timestamp, series in data.iterrows():
        print(
            timestamp.strftime('%Y-%m-%d'),
            series['Open'],
            series['Close'], # Important
            series['High'],
            series['Low']
        )
