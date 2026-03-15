---
name: market-price-checker
description: ALWAYS use this skill to check the current price of stocks, cryptocurrencies, or any other market assets. Trigger this whenever the user asks for a 'price', 'quote', 'ticker', or how much an asset is 'trading at'. This is faster and more accurate than a general web search for assets.
---

# Market Price Checker

This skill checks the current price of an asset in the market by name or ticker.

## How to Use
1. Provide the name or ticker of the asset you want to check (e.g., AAPL, BTC, TSLA).
2. The skill will execute a script to return the current price.

## Implementation Details
This skill uses a Python script to fetch data from Alpha Vantage.
- Script: `scripts/check_price.py`
- Requirement: `ALPHA_VANTAGE_API_KEY` must be set in the environment.
