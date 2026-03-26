import pandas as pd

def profile_dataframe(name, df):
    """Prints structural and statistical features of a given DataFrame."""
    print(f"==================================================")
    print(f" DATASET PROFILE: {name}")
    print(f"==================================================\n")
    
    # 1. Structural Features
    print("--- STRUCTURAL FEATURES ---")
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nData Types and Missing Values:")
    # df.info() prints directly to sys.stdout, so we capture it or just let it print
    df.info()
    
    print("\nFirst 3 Rows:")
    print(df.head(3).to_string())
    print("\n")
    
    # 2. Statistical Features
    print("--- STATISTICAL FEATURES ---")
    # describe() provides count, mean, std, min, 25%, 50%, 75%, max
    print(df.describe().to_string())
    print("\n\n")

def load_and_profile_data():
    # Filepaths
    databento_file = 'glbx-mdp3-20260224-20260323.ohlcv-1m.csv'
    binance_files = {
        'BTC/USDT': 'BTCUSDT_1m_March2026.csv',
        'ETH/USDT': 'ETHUSDT_1m_March2026.csv',
        'PAXG/USDT': 'PAXGUSDT_1m_March2026.csv'
    }
    
    # 1. Load Databento (Classic Markets / Futures)
    try:
        print(f"Loading {databento_file}...")
        df_db = pd.read_csv(databento_file)
        
        # Databento's timestamp column is usually named 'ts_event' or 'timestamp'
        # We find the likely time column and convert it to UTC datetime
        time_col = [col for col in df_db.columns if 'ts' in col.lower() or 'time' in col.lower()][0]
        df_db[time_col] = pd.to_datetime(df_db[time_col], utc=True)
        df_db.set_index(time_col, inplace=True)
        
        profile_dataframe("CME Globex Futures (Databento)", df_db)
        
    except FileNotFoundError:
        print(f"Error: Could not find {databento_file}")
    except Exception as e:
        print(f"Error loading Databento data: {e}")

    # 2. Load Binance (Crypto & Tokenized Gold)
    df_crypto = {}
    for name, filepath in binance_files.items():
        try:
            print(f"Loading {filepath}...")
            df = pd.read_csv(filepath)
            
            # Based on our previous extraction script, the time column is 'datetime_utc'
            if 'datetime_utc' in df.columns:
                df['datetime_utc'] = pd.to_datetime(df['datetime_utc'])
                df.set_index('datetime_utc', inplace=True)
            elif 'timestamp' in df.columns: # Fallback
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
                df.set_index('timestamp', inplace=True)
                
            df_crypto[name] = df
            profile_dataframe(f"Binance: {name}", df)
            
        except FileNotFoundError:
            print(f"Error: Could not find {filepath}")
        except Exception as e:
            print(f"Error loading {name} data: {e}")

    return df_db, df_crypto

if __name__ == "__main__":
    # Execute the loader
    df_futures, dict_crypto_dfs = load_and_profile_data()