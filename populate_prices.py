import sqlite3, config
import alpaca_trade_api as dateapi
from alpaca_trade_api.rest import TimeFrame
from datetime import date

# connecto to sql db and envoke 
# row factory to The row_factory property allows you to specify 
# a callable that will be used to convert the result rows from the database 
# into a custom Python object. By default, row_factory is set to None, 
# which means that the rows are returned as tuples.

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

# get the selected ID 
cursor.execute("""
        SELECT id, symbol, name FROM stock WHERE symbol NOT LIKE ("%/%")
""")

rows = cursor.fetchall()

# symbols = [row['symbol'] for row in rows]

symbols = []
stock_dict = {}
for row in rows:
    symbol = row['symbol']
    symbols.append(symbol)
    stock_dict[symbol] = row['id']
    
api = dateapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)

# symbols = ['MSFT']

chunk_size = 200

for i in range(0, len(symbols), chunk_size):

    
    symbol_chunk = symbols[i:i+chunk_size]
    
    
    barsets = api.get_bars(symbol_chunk,TimeFrame.Day,"2023-01-28", "2023-03-01", )._raw   


    # for symbol in barsets:
    #     print( {symbol})
        # this is the problem
        
    for bar in barsets:
        symbol = bar["S"]
        print(f"processing symbol {symbol}")
        stock_id = stock_dict[bar["S"]]

    cursor.execute("""
        INSERT INTO stock_price (stock_id, date, open, high, low, close, volume )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (stock_id, bar['t'], bar['o'], bar['h'], bar['l'], bar['c'], bar['v']))


connection.commit()
