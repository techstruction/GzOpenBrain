import requests
import os
import sys

def market_price_checker(asset):
    # Use the Alpha Vantage API to get the current price of the asset
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("Error: ALPHA_VANTAGE_API_KEY not found in environment.")
        sys.exit(1)
        
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={asset}&apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            return data["Global Quote"]["05. price"]
        else:
            print(f"Error: Could not find price data for {asset}. Response: {data}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_price.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    price = market_price_checker(ticker)
    print(f"The current price of {ticker} is ${price}")
