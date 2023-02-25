import sqlite3, config
import alpaca_trade_api as tradeapi

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
        SELECT symbol, company FROM stock
               """)
rows = cursor.fetchall()
symbols = [row['symbol'] for row in rows]
# print(symbols)




api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)
assets = api.list_assets()

for asset in assets:
    # if the symbol is equal to ticker print asset
    # if asset.symbol == 'FTSI':
        # print(asset)
    
    #this is to loop through the values in the object provided by alpaca and insert them into own db. - fucking mad
    # get dupicate id so use a try catch block when you have duplicates
    
    try:
        
        if asset.status == 'active' and asset.tradable and asset.symbol not in symbols:
            print(f"Added a new stock {asset.symbol} {asset.name}")
            cursor.execute("INSERT INTO stock (symbol, company) VALUES (?,?)", (asset.symbol, asset.name ))
    except Exception as e:
        print(asset.symbol)
        print(e)
    
    

    connection.commit()