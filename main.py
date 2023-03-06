import sqlite3, config
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import date

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    stock_filter = request.query_params.get('filter', False)
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    if stock_filter == 'new_closing_highs':
        cursor.execute("""
        SELECT * FROM (
            SELECT symbol, name, exchange, stock_id, max(close), date
            FROM stock_price join stock on stock.id = stock_price.stock_id
            GROUP by stock_id
            ORDER by symbol
        ) WHERE date = (select max(date) from stock_price)
        """)
    
    elif stock_filter == 'new_closing_lows':
        cursor.execute("""
        SELECT * FROM (
            SELECT symbol, name, exchange, stock_id, min(close), date
            FROM stock_price JOIN stock on stock.id = stock_price.stock_id
            GROUP by stock_id
            ORDER by symbol
        ) WHERE date = (select max(date) from stock_price)
        """)
        
    
    else:
        cursor.execute("""
            SELECT id, symbol ,name, exchange
            FROM stock 
            ORDER BY symbol
                   """)
        
    rows = cursor.fetchall()
    
   
    cursor.execute("""
            SELECT symbol, close
            FROM stock JOIN stock_price on stock_price.stock_id = stock.id
            WHERE date = (select max(date) from stock_price)
                   """)
    
    indicator_rows = cursor.fetchall()
    indicator_values = {}
    
    
    for row in indicator_rows:
        indicator_values[row['symbol']] = row
    
        
    return templates.TemplateResponse("index.html", {"request":request, "stocks": rows, "indicator_values" : indicator_values})


@app.get("/strategies")
def strategies(request: Request):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT * FROM strategy
                   """)
    
    Strategies = cursor.fetchall()

    return templates.TemplateResponse("strategies.html", {"request":request , "Strategies": Strategies} )

@app.get("/watchlist")
def watchlist(request: Request):
    
    return templates.TemplateResponse("watchlist.html", {"request": request} , status_code=303)


@app.get("/etf")
def watchlist(request: Request):
    
    return templates.TemplateResponse("etf.html", {"request": request} , status_code=303)

@app.get("/profit_loss")
def watchlist(request: Request):
    
    return templates.TemplateResponse("profit_loss.html", {"request": request} , status_code=303)


@app.get("/stock/{symbol}")
def StockDetail(request: Request, symbol):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    
    cursor.execute("""
        SELECT * FROM strategy
                   """)
    
    strategies = cursor.fetchall() 
    
    cursor.execute("""
        SELECT id, symbol, name FROM stock WHERE symbol = ?
               """, (symbol,))
    
    row = cursor.fetchone()
    
    cursor.execute("""
        SELECT * FROM stock_price WHERE stock_id = ? 
               """, (row['id'],))
    
    prices = cursor.fetchall()
    
    return templates.TemplateResponse("stock_detail.html", {"request":request, "strategies": strategies, "stock": row, "bars": prices, })
    
# form handler to insert stock id into the strategy table
@app.post("/apply_strategy")
def apply_strategy(strategy_id: int = Form(...), stock_id: int = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()
    
    cursor.execute("""
        INSERT INTO stock_strategy (stock_id, strategy_id) VALUES (?, ?)
               """, (stock_id, strategy_id))
    
    connection.commit()
    
    return RedirectResponse(url=f"/strategy/{strategy_id}", status_code=303)



@app.get("/strategy/{strategy_id}")
def strategy(request: Request, strategy_id):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    
    cursor.execute("""
        SELECT id, name
        FROM strategy
        WHERE id = ?  
               """, (strategy_id,))
    
    strategy = cursor.fetchone()

    
    cursor.execute("""
        SELECT id, symbol, name
        FROM stock JOIN stock_strategy on stock_strategy.stock_id = stock.id

        WHERE strategy_id = ?
             """, (strategy_id,))
    
    stocks = cursor.fetchall()

    
    return templates.TemplateResponse("strategy.html", {"request": request, "strategy": strategy, "stocks": stocks}  )




