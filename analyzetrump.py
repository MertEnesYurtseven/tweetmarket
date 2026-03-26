import pandas as pd
import numpy as np
from datetime import timedelta
import warnings

warnings.filterwarnings('ignore') # Suppress pandas slice warnings for clean output

# ==============================================================================
# CONFIGURATION & EVENT DATA
# ==============================================================================
# All timestamps converted from ET to UTC
TWEET_EVENTS = {
    # --- LATE MARCH: RESOLUTION & DIPLOMACY ---
    "March 26 - 6:16 AM ET (10:16 UTC)": "2026-03-26 10:16:00+00:00",
    "March 26 - 6:03 AM ET (10:03 UTC)": "2026-03-26 10:03:00+00:00",
    "March 25 - 2:17 PM ET (18:17 UTC)": "2026-03-25 18:17:00+00:00", # Xi Jinping Meeting
    "March 25 - 11:30 AM ET (15:30 UTC)": "2026-03-25 15:30:00+00:00",
    "March 23 - 10:29 AM ET (14:29 UTC)": "2026-03-23 14:29:00+00:00",
    "March 23 - 7:23 AM ET (11:23 UTC)": "2026-03-23 11:23:00+00:00", # Peace Resolution
    "March 23 - 7:05 AM ET (11:05 UTC)": "2026-03-23 11:05:00+00:00", # Peace Resolution (Deleted)
    "March 22 - 8:24 AM ET (12:24 UTC)": "2026-03-22 12:24:00+00:00",
    
    # --- MID MARCH: ULTIMATUMS & MILITARY CLIMAX ---
    "March 21 - 7:44 PM ET (23:44 UTC)": "2026-03-21 23:44:00+00:00", # 48hr Ultimatum
    "March 21 - 6:37 PM ET (22:37 UTC)": "2026-03-21 22:37:00+00:00", # "Blown off the map"
    "March 21 - 9:55 AM ET (13:55 UTC)": "2026-03-21 13:55:00+00:00",
    "March 19 - 8:21 AM ET (12:21 UTC)": "2026-03-19 12:21:00+00:00", # Treasury/Media Alert
    "March 18 - 8:01 AM ET (12:01 UTC)": "2026-03-18 12:01:00+00:00",
    "March 14 - 2:58 PM ET (18:58 UTC)": "2026-03-14 18:58:00+00:00", # Victory / Oil Flowing
    "March 13 - 11:53 PM ET (Mar 14 03:53 UTC)": "2026-03-14 03:53:00+00:00",
    "March 13 - 9:38 PM ET (Mar 14 01:38 UTC)": "2026-03-14 01:38:00+00:00", # Kharg Island Bombing
    "March 13 - 8:27 PM ET (Mar 14 00:27 UTC)": "2026-03-14 00:27:00+00:00", # Kharg Island (Deleted)
    "March 13 - 7:43 PM ET (23:43 UTC)": "2026-03-13 23:43:00+00:00",
    "March 13 - 12:33 AM ET (04:33 UTC)": "2026-03-13 04:33:00+00:00", # Navy/Air Force "Gone"
    "March 12 - 11:00 AM ET (15:00 UTC)": "2026-03-12 15:00:00+00:00",
    "March 12 - 9:14 AM ET (13:14 UTC)": "2026-03-12 13:14:00+00:00",
    
    # --- EARLY MARCH: ESCALATION (UTC-5 OFFSET) ---
    "March 10 - 8:57 PM ET (Mar 11 00:57 UTC)": "2026-03-11 00:57:00+00:00",
    "March 9 - 10:16 AM ET (14:16 UTC)": "2026-03-09 14:16:00+00:00",
    "March 8 - 6:54 PM ET (22:54 UTC)": "2026-03-08 22:54:00+00:00", # Oil Drop Prediction
    "March 6 - 3:46 PM ET (20:46 UTC)": "2026-03-06 20:46:00+00:00",
    "March 6 - 8:50 AM ET (13:50 UTC)": "2026-03-06 13:50:00+00:00", # Surrender Demand
    "March 5 - 9:35 AM ET (14:35 UTC)": "2026-03-05 14:35:00+00:00",
    "March 3 - 8:02 AM ET (13:02 UTC)": "2026-03-03 13:02:00+00:00",
    "March 3 - 7:38 AM ET (12:38 UTC)": "2026-03-03 12:38:00+00:00",
    "March 2 - 6:40 PM ET (23:40 UTC)": "2026-03-02 23:40:00+00:00",
    "March 2 - 6:20 PM ET (23:20 UTC)": "2026-03-02 23:20:00+00:00",
    "March 2 - 4:43 PM ET (21:43 UTC)": "2026-03-02 21:43:00+00:00",
    "March 1 - 7:40 AM ET (12:40 UTC)": "2026-03-01 12:40:00+00:00",
    "March 1 - 12:25 AM ET (05:25 UTC)": "2026-03-01 05:25:00+00:00", # "Force Never Seen"
    "February 28 - 4:37 PM ET (21:37 UTC)": "2026-02-28 21:37:00+00:00" # Khamenei Death
}

def load_data():
    market_data = {}
    
    # 1. Load Crypto Data
    crypto_files = {
        'BTC/USDT': 'BTCUSDT_1m_March2026.csv',
        'ETH/USDT': 'ETHUSDT_1m_March2026.csv',
        'PAXG/USDT': 'PAXGUSDT_1m_March2026.csv'
    }
    for name, fp in crypto_files.items():
        try:
            df = pd.read_csv(fp)
            col_name = 'datetime_utc' if 'datetime_utc' in df.columns else 'timestamp'
            df[col_name] = pd.to_datetime(df[col_name], utc=True)
            df.set_index(col_name, inplace=True)
            # Calculate 1-minute returns
            df['return'] = df['close'].pct_change().fillna(0)
            market_data[name] = df
        except Exception:
            pass

    # 2. Load CME Futures Data
    try:
        df_db = pd.read_csv('glbx-mdp3-20260224-20260323.ohlcv-1m.csv')
        time_col = [col for col in df_db.columns if 'ts' in col.lower() or 'time' in col.lower()][0]
        df_db[time_col] = pd.to_datetime(df_db[time_col], utc=True)
        
        top_symbols = df_db.groupby('symbol')['volume'].sum().nlargest(3).index
        for sym in top_symbols:
            df_sym = df_db[df_db['symbol'] == sym].copy()
            df_sym.set_index(time_col, inplace=True)
            df_sym.sort_index(inplace=True)
            df_sym['return'] = df_sym['close'].pct_change().fillna(0)
            market_data[f"CME: {sym}"] = df_sym
    except Exception:
        pass

    return market_data

def calculate_tod_baselines(df):
    """Calculates the Time-of-Day (ToD) historical baselines for every minute."""
    df['time_str'] = df.index.strftime('%H:%M')
    
    tod_stats = df.groupby('time_str').agg(
        vol_mean=('volume', 'mean'),
        vol_std=('volume', 'std'),
        ret_mean=('return', 'mean'),
        ret_std=('return', 'std')
    )
    # Fill any NaN standard deviations (if a minute only has 1 occurrence) with 0
    tod_stats.fillna(0, inplace=True)
    return tod_stats
def analyze_insider_metrics(market_data, output_filename="insider_analysis_report.txt"):
    """Analyzes data and writes the statistical output directly to a text file."""
    
    # Open a text file in write mode
    with open(output_filename, "w", encoding="utf-8") as f:
        
        for asset, df in market_data.items():
            # Direct output to the file using the 'file=f' parameter
            print(f"\n{'='*70}", file=f)
            print(f" ASSET: {asset}", file=f)
            print(f"{'='*70}", file=f)
            
            # Calculate General Baseline
            gen_vol_mean = df['volume'].mean()
            gen_ret_std = df['return'].std()
            print(f"[GENERAL BASELINE] Avg 1m Volume: {gen_vol_mean:.2f} | 1m Volatility (StdDev): {gen_ret_std*100:.4f}%\n", file=f)
            
            # Calculate ToD Baselines
            tod_stats = calculate_tod_baselines(df)
            
            for event_name, event_time_str in TWEET_EVENTS.items():
                t0 = pd.to_datetime(event_time_str)
                
                # Define Windows
                t_minus_15 = t0 - timedelta(minutes=15)
                t_minus_1 = t0 - timedelta(minutes=1)
                t_plus_60 = t0 + timedelta(minutes=60)
                
                # Extract Pre-Event Data
                pre_event_df = df.loc[t_minus_15:t_minus_1]
                post_event_df = df.loc[t0:t_plus_60]
                
                if pre_event_df.empty or post_event_df.empty:
                    continue # Skip if no data for this specific time window
                
                # 1. Volume Spikes (Z-Score against ToD)
                pre_time_strs = pre_event_df['time_str'].values
                tod_vol_means = tod_stats.loc[pre_time_strs, 'vol_mean'].values
                tod_vol_stds = tod_stats.loc[pre_time_strs, 'vol_std'].values
                
                # Calculate aggregate Z-score for the 15m window
                tod_vol_stds = np.where(tod_vol_stds == 0, 1e-9, tod_vol_stds)
                z_scores = (pre_event_df['volume'].values - tod_vol_means) / tod_vol_stds
                avg_z_score = np.mean(z_scores)
                
                # 2. Directional Price Action
                pre_drift_pct = (pre_event_df['close'].iloc[-1] / pre_event_df['open'].iloc[0]) - 1
                post_move_pct = (post_event_df['close'].iloc[-1] / post_event_df['open'].iloc[0]) - 1
                
                # Front-Running Flag
                aligned = (pre_drift_pct * post_move_pct) > 0
                front_run_indicator = "⚠️ MATCH (Potential Front-Running)" if aligned and abs(avg_z_score) > 1.5 else "None"
                
                # 3. Volatility Compression/Expansion
                pre_volatility = pre_event_df['return'].std()
                volatility_ratio = pre_volatility / gen_ret_std
                
                print(f"--- EVENT: {event_name} ---", file=f)
                print(f"  Pre-Event (-15m) Volume Z-Score: {avg_z_score:.2f} " + 
                      ("(HIGH ANOMALY)" if avg_z_score > 2.0 else ""), file=f)
                print(f"  Pre-Event Volatility Ratio:      {volatility_ratio:.2f}x Baseline", file=f)
                print(f"  Pre-Event Price Drift (-15m):    {pre_drift_pct*100:+.4f}%", file=f)
                print(f"  Post-Event Price Move (+60m):    {post_move_pct*100:+.4f}%", file=f)
                print(f"  Directional Alignment:           {front_run_indicator}\n", file=f)
                
    # Print a single confirmation to the terminal so you know it finished
    print(f"Analysis complete. Full report successfully saved to '{output_filename}'")


if __name__ == "__main__":
    print("Initializing Market Data...")
    market_data = load_data()
    
    if not market_data:
        print("Error: No data loaded. Check CSV files.")
    else:
        # Run the analysis; it will save to "insider_analysis_report.txt" by default
        analyze_insider_metrics(market_data)