import yfinance as yf

stock = yf.Ticker('AMZN')

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
