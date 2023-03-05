import sqlite3
import config
import alpaca_trade_api as tradeapi
from polygon import RESTClient
from datetime import date

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT id from strategy WHERE name = 'open_range_breakout'
               """)

strategy_id = cursor.fetchone()

cursor.execute("""
    SELECT symbol, name
    FROM stock
    JOIN stock_strategy on stock_strategy.stock_id = stock.id
    WHERE stock_strategy.strategy_id = ?
               """, (strategy_id,)) 

stocks = cursor.fetchall()
symbols = [stock['symbol'] for stock in stocks]

print(symbols)
client = RESTClient(config.POLYGON_KEY)
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)

current_date = date.today().isoformat()
start_minute_bar = f"{current_date} 09:30:00-04:00"
end_minute_bar = f"{current_date} 09:45:00-04:00"


orders = api.list_orders(status='all', limit=500, after=f"{current_date}")
existing_order_symbol = [order.symbol for order in orders]


for symbol in symbols:
    minute_bars = client.get_aggs(ticker= symbols, multiplier=1, timespan="minute", from_="2023-02-23", to="2023-02-24").df
    
    
    opening_range_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]
    opening_range_low = opening_range_bars['low'].min()
    opening_range_high = opening_range_bars['high'].min()
    opening_range = opening_range_high = opening_range_low
    
    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bar = minute_bars.loc[after_opening_range_mask]
    
    
    after_opening_range_breakout = after_opening_range_bar[after_opening_range_bar['close'] > opening_range_high]
    
    if not after_opening_range_breakout.empty:
            if symbol not in existing_order_symbol:
                limit_price = after_opening_range_breakout.iloc[0]['close']        
            
            print(f"placing order for {symbol} at {limit_price}, closed_above {opening_range_high} at {after_opening_range_breakout.iloc[0]}")
        
    api.submit_order(
            symbol=symbol,
            side='buy',
            type='limit',
            qty=100,
            time_in_force='day',
            order_class='bracket',
            limit_price= limit_price,
            take_profit=dict(
                limit_price= limit_price + opening_range
            ),
            stop_loss=dict(
                stop_price=limit_price - opening_range,
            )
        )
else:
    print(f"Already an order for {symbol} skipping")
    