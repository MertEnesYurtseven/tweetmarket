
# tweetmarket

**Insider Activity Analysis Around Public Announcements**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/) 
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Event-driven market microstructure analysis focused on **Donald Trump’s geopolitical tweets** in March 2026. The project quantifies **pre-event positioning**, **polarity footprints**, and **algorithmic front-running** across crypto (BTC, ETH, PAXG) and traditional futures (S&P 500, Crude Oil) using 1-minute OHLCV data.

This repository powers the analysis presented in the Medium article:  
[**Event driven market mechanics and insider trading**](https://medium.com/@mert.yurtseven.enes/event-driven-market-mechanics-and-insider-trading-28237ec171ec)

It detects statistically significant volume anomalies (Z-scores vs. Time-of-Day baselines), pre-event price drift, post-event moves, and polarity whipsaws — providing empirical evidence of information leakage and algorithmic anticipation around public announcements.

## Features

- **Tweet Event Catalog**: 30+ timestamped Trump-related geopolitical events (March 2026) with semantic context (dovish/hawkish, escalation/de-escalation).
- **Polarity Footprint Analysis**: Computes Z-score volume spikes, pre/post-event price drift, volatility ratios, and front-running indicators.
- **Time-of-Day Baselines**: Filters out natural market rhythms using 20-day historical averages.
- **Interactive Microstructure Visualizer**: Desktop GUI (PyQt5 + pyqtgraph) with synchronized candlestick + volume charts centered on each event.
- **Data Pipeline**: Scripts to fetch fresh Binance 1m klines and load/process Databento CME futures data.
- **Reproducible Output**: Generates `insider_analysis_report.txt` with per-event, per-asset statistics.

## Project Structure

```
tweetmarket/
├── BTCUSDT_1m_March2026.csv          # 1m Binance data (pre-fetched)
├── ETHUSDT_1m_March2026.csv
├── PAXGUSDT_1m_March2026.csv
├── analyzetrump.py                   # Core analysis engine (Z-scores, polarity footprint, report)
├── app.py                            # Interactive Event Microstructure Visualizer (GUI)
├── loaddata.py                       # Data loader + profiler (Binance + Databento)
├── trumpfetchcrypto.py               # Binance 1m klines fetcher for March 2026
├── linktofutures.txt                 # Reference for Databento CME futures dataset
└── insider_analysis_report.txt       # Generated analysis output
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MertEnesYurtseven/tweetmarket.git
   cd tweetmarket
   ```

2. (Recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate       # Windows
   ```

3. Install dependencies:
   ```bash
   pip install pandas numpy pyqt5 pyqtgraph
   ```

   (Note: No `requirements.txt` yet — the project uses only these core libraries.)

4. **Futures data (optional but recommended)**:  
   Obtain the Databento CME Globex 1m OHLCV file (`glbx-mdp3-20260224-20260323.ohlcv-1m.csv`) and place it in the root. See `linktofutures.txt` for the data source reference.

## Usage

### 1. Fetch / Refresh Crypto Data
```bash
python trumpfetchcrypto.py
```
Downloads fresh 1-minute klines for BTCUSDT, ETHUSDT, and PAXGUSDT (March 1–27 2026) from Binance.

### 2. Profile Loaded Data
```bash
python loaddata.py
```
Prints shape, data types, missing values, and statistical summary for all datasets.

### 3. Run Full Analysis (Polarity Footprint)
```bash
python analyzetrump.py
```
- Analyzes every event in `TWEET_EVENTS`.
- Outputs detailed statistics to `insider_analysis_report.txt`.
- Matches exactly the anomalies discussed in the Medium article (March 23 polarity whipsaw, March 19 safe-haven distribution, March 8 oil leak, etc.).

### 4. Launch Interactive Visualizer
```bash
python app.py
```
Opens a full-featured desktop GUI:
- Select any highlighted event (March 23 whipsaw, March 19 distribution, March 8 oil leaks, etc.).
- Switch between relevant assets (ESM6, CLJ6, BTC, ETH, PAXG).
- Zoomable candlestick + volume charts with automatic y-scaling.
- Designed to visually confirm the “Polarity Footprint” anomalies.

## Technologies

- **Data**: Pandas, NumPy
- **Analysis**: Time-series Z-score calculations, pre/post-event drift
- **Visualization**: PyQt5 + pyqtgraph (custom candlestick + dynamic scaling)
- **Data Sources**: 
  - Binance public API (crypto)
  - Databento (CME futures)

## Data Sources & Methodology

- **Crypto**: Binance 1m klines (BTCUSDT, ETHUSDT, PAXGUSDT)
- **Futures**: Databento 1m OHLCV for top-volume CME contracts (ESM6, CLJ6, etc.)
- **Events**: Manually curated list of Donald Trump’s geopolitical tweets (March 2026), converted to UTC
- **Core Metric**: Localized Z-score of volume relative to 20-day Time-of-Day baseline + directional price drift

Full methodology and example results (March 23 18-minute whipsaw, March 8 “sell the rumor” oil move, etc.) are in the [Medium article](https://medium.com/@mert.yurtseven.enes/event-driven-market-mechanics-and-insider-trading-28237ec171ec).

## License

MIT License — feel free to use, modify, and extend for research or personal projects.

## Contributing

Pull requests welcome! Especially:
- Adding more assets or events
- Improving the GUI
- Adding statistical significance tests
- Exporting results to CSV/JSON

---

— Mert Enes Yurtseven  
March 2026
```
