import sqlite3, config

connection = sqlite3.connect(config.DB_FILE)

print(connection.total_changes)

cursor = connection.cursor()

cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY,
            symbol TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            exchange TEXT NOT NULL
        )""")

cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_price (
            id INTEGER PRIMARY KEY,
            stock_id INTEGER,
            date NOT NULL,
            open NOT NULL,
            high NOT NULL,
            low NOT NULL,
            close NOT NULL,
            volume NOT NULL,
            sma_21,
            sma_5,
            rsi_13,
            FOREIGN KEY (stock_id) REFERENCES stock (id)
        )""")

cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy (
            id INTEGER PRIMARY KEY,
            name NOT NULL
        )""")

cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_strategy (
            stock_id INTEGER NOT NULL,
            strategy_Id INTEGER NOT NULL,
            FOREIGN KEY (stock_id) REFERENCES stock (id)
            FOREIGN KEY (strategy_Id) REFERENCES strategy (id)
        )""")

strategies = ['open_range_breakout', 'opening_range_breakdown']

for strategy in strategies:
    cursor.execute("""
        INSERT INTO strategy (name) VALUES (?)
                   """, (strategy,))     

connection.commit()