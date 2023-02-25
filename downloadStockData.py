import yfinance 

df = yfinance.download("MNST", start="2022-01-01", end="2023-02-20")
df.to_csv('MNST.csv')