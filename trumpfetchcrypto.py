import requests
import pandas as pd
import time
from datetime import datetime, timezone

def fetch_binance_1m_data_raw(symbol, start_date_str, end_date_str, output_filename):
    print(f"Fetching 1m data for {symbol} using raw requests...")
    
    base_url = "https://api.binance.com/api/v3/klines"
    
    # Convert string dates to UTC timestamps in milliseconds
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    
    since_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)
    
    all_ohlcv = []
    limit = 1000  # Max limit for Binance klines
    
    while since_ms < end_ms:
        params = {
            'symbol': symbol,
            'interval': '1m',
            'startTime': since_ms,
            'endTime': end_ms,
            'limit': limit
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
            
            if not data:
                break
                
            all_ohlcv.extend(data)
            
            # The 0th index of the last candle is its open time. 
            # Add 1 minute (60,000 ms) to get the next start time.
            since_ms = data[-1][0] + 60000
            
            # Binance allows 1200 request weight per minute. 
            # A simple sleep keeps us well within safe limits.
            time.sleep(0.5) 
            
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching data: {e}")
            time.sleep(5)  # Back off on error
            
    # Binance kline response structure: 
    # [Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, ...]
    if all_ohlcv:
        # We only need the first 6 columns for standard OHLCV
        df = pd.DataFrame(all_ohlcv).iloc[:, 0:6]
        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        # Convert types from strings (Binance returns strings for prices/volumes) to floats
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        # Format the timestamp to a readable UTC datetime string
        df['datetime_utc'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        
        # Reorder and clean columns
        df = df[['datetime_utc', 'open', 'high', 'low', 'close', 'volume']]
        
        # Save to CSV
        df.to_csv(output_filename, index=False)
        print(f"Successfully saved {len(df)} rows to {output_filename}\n")
    else:
        print(f"No data found for {symbol} in this range.\n")

if __name__ == "__main__":
    # Define the assets without slashes for the raw API
    symbols = ['BTCUSDT', 'ETHUSDT', 'PAXGUSDT']
    
    # Define the March 2026 window (up to current date)
    start_date = "2026-03-01"
    end_date = "2026-03-27" # Exclusive end date
    
    for sym in symbols:
        # Create a clean filename
        filename = f"{sym}_1m_March2026.csv"
        fetch_binance_1m_data_raw(sym, start_date, end_date, filename)