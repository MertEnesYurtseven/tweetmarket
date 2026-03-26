import sys
import pandas as pd
import numpy as np
from datetime import timedelta
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

# ==============================================================================
# CONFIGURATION & EVENT DATA
# ==============================================================================
BACKGROUND_COLOR = '#121212'
FOREGROUND_COLOR = '#d1d4dc'

# Filtered for Microstructure Anomalies identified in the Polarity Footprint Analysis
TWEET_EVENTS = {
    # The March 23 Polarity Whipsaw (Dovish to Hawkish Reversal)
    "March 23 - 7:05 AM ET (11:05 UTC)": "2026-03-23 11:05:00+00:00",
    "March 23 - 7:23 AM ET (11:23 UTC)": "2026-03-23 11:23:00+00:00",
    
    # The March 19 Targeted Safe-Haven Distribution
    "March 19 - 8:21 AM ET (12:21 UTC)": "2026-03-19 12:21:00+00:00",
    
    # The Crude Oil Information Leaks (Asia Open & Pre-Market)
    "March 8 - 6:54 PM ET (22:54 UTC)": "2026-03-08 22:54:00+00:00",
    "March 3 - 8:02 AM ET (13:02 UTC)": "2026-03-03 13:02:00+00:00",
    "March 3 - 7:38 AM ET (12:38 UTC)": "2026-03-03 12:38:00+00:00"
}

# Maps the specific events to the assets relevant to that event's anomaly
EVENT_ASSET_MAP = {
    "March 23 - 7:05 AM ET (11:05 UTC)": ["CME: ESM6", "BTC/USDT", "ETH/USDT", "PAXG/USDT"],
    "March 23 - 7:23 AM ET (11:23 UTC)": ["CME: ESM6", "BTC/USDT", "ETH/USDT", "PAXG/USDT"],
    "March 19 - 8:21 AM ET (12:21 UTC)": ["PAXG/USDT", "CME: ESM6", "CME: CLJ6"], # CLJ6 and ESM6 included for baseline contrast
    "March 8 - 6:54 PM ET (22:54 UTC)": ["CME: CLJ6"],
    "March 3 - 8:02 AM ET (13:02 UTC)": ["CME: CLJ6"],
    "March 3 - 7:38 AM ET (12:38 UTC)": ["CME: CLJ6"]
}

# ==============================================================================
# 1. CUSTOM CANDLESTICK ITEM
# ==============================================================================
class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.picture = QtGui.QPicture()
        self.generatePicture()

    def generatePicture(self):
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('#787b86', width=1)) 
        
        w = 22.5 
        
        for (t, open_p, close_p, low_p, high_p) in self.data:
            p.drawLine(QtCore.QPointF(t, low_p), QtCore.QPointF(t, high_p))
            
            if close_p >= open_p:
                p.setBrush(pg.mkBrush('#089981')) 
                p.setPen(pg.mkPen('#089981')) 
            else:
                p.setBrush(pg.mkBrush('#f23645')) 
                p.setPen(pg.mkPen('#f23645'))
            
            body_h = close_p - open_p
            if abs(body_h) < 1e-5: 
                body_h = 0.01 if body_h >=0 else -0.01

            p.drawRect(QtCore.QRectF(t - w, open_p, w * 2, body_h))
            
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

# ==============================================================================
# 2. AUTO-SCALING PLOT WIDGET
# ==============================================================================
class DynamicPlotWidget(pg.PlotWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.plotItem.showAxis('right')
        self.plotItem.hideAxis('left')
        self.setMouseEnabled(x=True, y=False)
        self.showGrid(x=True, y=True, alpha=0.1)
        self.sigXRangeChanged.connect(self.update_y_range)
        self.items_to_scale = []

    def add_scalable_item(self, item):
        self.items_to_scale.append(item)

    def update_y_range(self):
        view_box = self.getViewBox()
        view_range = view_box.viewRange()
        
        if not view_range or len(view_range) < 2: return
        
        min_x, max_x = view_range[0]
        y_min, y_max = float('inf'), float('-inf')
        found_data = False

        for item in self.items_to_scale:
            if isinstance(item, CandlestickItem):
                timestamps = np.array([d[0] for d in item.data])
                idx_start = np.searchsorted(timestamps, min_x)
                idx_end = np.searchsorted(timestamps, max_x, side='right')
                
                if idx_start < idx_end:
                    subset = item.data[idx_start:idx_end]
                    for (_, _, _, l, h) in subset:
                        y_min = min(y_min, l)
                        y_max = max(y_max, h)
                        found_data = True
            
            elif isinstance(item, pg.BarGraphItem):
                x_data = item.opts['x']
                y_data = item.opts['height']
                idx_start = np.searchsorted(x_data, min_x)
                idx_end = np.searchsorted(x_data, max_x, side='right')
                
                if idx_start < idx_end:
                    chunk = y_data[idx_start:idx_end]
                    if len(chunk) > 0:
                        v_max = np.max(chunk)
                        y_min, y_max = 0, v_max * 3.33 
                        found_data = True

        if found_data and y_min != float('inf') and y_max != float('-inf'):
            diff = (y_max - y_min)
            if diff == 0: diff = 1.0
            pad = diff * 0.05
            view_box.setYRange(y_min - pad, y_max + pad, padding=0)

# ==============================================================================
# 3. MAIN WINDOW & DATA LOADING
# ==============================================================================
class ChartWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Microstructure Visualizer")
        self.resize(1400, 900)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {FOREGROUND_COLOR};")

        self.market_data = {}
        
        # --- UI LAYOUT ---
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        
        # 1. Controls Area
        controls = QtWidgets.QWidget()
        controls.setFixedHeight(60)
        controls.setStyleSheet("background-color: #1e1e1e; border-bottom: 1px solid #333; font-size: 14px;")
        c_layout = QtWidgets.QHBoxLayout(controls)
        c_layout.setContentsMargins(15, 10, 15, 10)
        
        lbl_event = QtWidgets.QLabel("Tweet Event:")
        self.cb_event = QtWidgets.QComboBox()
        self.cb_event.setStyleSheet("background: #333; color: white; padding: 5px; min-width: 250px;")
        self.cb_event.addItems(list(TWEET_EVENTS.keys()))

        lbl_asset = QtWidgets.QLabel("Relevant Asset:")
        self.cb_asset = QtWidgets.QComboBox()
        self.cb_asset.setStyleSheet("background: #333; color: white; padding: 5px; min-width: 150px;")
        
        c_layout.addWidget(lbl_event)
        c_layout.addWidget(self.cb_event)
        c_layout.addSpacing(30)
        c_layout.addWidget(lbl_asset)
        c_layout.addWidget(self.cb_asset)
        c_layout.addStretch()
        
        layout.addWidget(controls)

        # 2. Plotting Area (Split View)
        plot_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        
        # Price Plot
        date_axis_price = pg.DateAxisItem(orientation='bottom')
        self.price_plot = DynamicPlotWidget(axisItems={'bottom': date_axis_price})
        plot_splitter.addWidget(self.price_plot)
        
        # Volume Plot
        date_axis_vol = pg.DateAxisItem(orientation='bottom')
        self.vol_plot = DynamicPlotWidget(axisItems={'bottom': date_axis_vol})
        plot_splitter.addWidget(self.vol_plot)
        
        plot_splitter.setSizes([700, 200])
        layout.addWidget(plot_splitter)
        
        self.vol_plot.setXLink(self.price_plot)
        
        self.t0_line_price = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('b', style=QtCore.Qt.DashLine, width=2))
        self.t0_line_vol = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('b', style=QtCore.Qt.DashLine, width=2))
        self.price_plot.addItem(self.t0_line_price)
        self.vol_plot.addItem(self.t0_line_vol)

        # Connections (Event change triggers dynamic asset population)
        self.cb_event.currentIndexChanged.connect(self.on_event_changed)
        self.cb_asset.currentIndexChanged.connect(self.update_view)

        # Execution
        self.load_data()

    def load_data(self):
        print("Loading datasets into memory...")
        
        # Load Crypto
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
                df['ts_sec'] = df.index.astype(np.int64) // 10**9
                self.market_data[name] = df
            except Exception as e:
                print(f"Skipped {name}: {e}")

        # Load Futures
        try:
            df_db = pd.read_csv('glbx-mdp3-20260224-20260323.ohlcv-1m.csv')
            time_col = [col for col in df_db.columns if 'ts' in col.lower() or 'time' in col.lower()][0]
            df_db[time_col] = pd.to_datetime(df_db[time_col], utc=True)
            
            top_symbols = df_db.groupby('symbol')['volume'].sum().nlargest(3).index
            for sym in top_symbols:
                df_sym = df_db[df_db['symbol'] == sym].copy()
                df_sym.set_index(time_col, inplace=True)
                df_sym['ts_sec'] = df_sym.index.astype(np.int64) // 10**9
                self.market_data[f"CME: {sym}"] = df_sym
        except Exception as e:
            print(f"Skipped Databento: {e}")

        if self.market_data:
            # Trigger the event logic to populate the first asset list
            self.on_event_changed()
        else:
            print("CRITICAL: No data loaded. Check filepaths.")

    def on_event_changed(self):
        event_key = self.cb_event.currentText()
        if not event_key: return
        
        # Get relevant assets from map, fallback to all if event missing from map
        relevant_assets = EVENT_ASSET_MAP.get(event_key, list(self.market_data.keys()))
        
        # Filter to make sure the asset file actually loaded properly
        available_assets = [a for a in relevant_assets if a in self.market_data]
        
        # Block signals so clearing the list doesn't trigger a blank update_view
        self.cb_asset.blockSignals(True)
        self.cb_asset.clear()
        self.cb_asset.addItems(available_assets)
        self.cb_asset.blockSignals(False)
        
        if available_assets:
            self.cb_asset.setCurrentIndex(0)
            self.update_view()
        else:
            self.price_plot.clear()
            self.vol_plot.clear()
            self.setWindowTitle(f"Event Microstructure Visualizer - NO DATA for {event_key}")

    def update_view(self):
        asset = self.cb_asset.currentText()
        event_key = self.cb_event.currentText()
        
        if not asset or not event_key: return
        
        self.price_plot.clear()
        self.price_plot.addItem(self.t0_line_price)
        self.price_plot.items_to_scale = []

        self.vol_plot.clear()
        self.vol_plot.addItem(self.t0_line_vol)
        self.vol_plot.items_to_scale = []

        df = self.market_data[asset]
        t0 = pd.to_datetime(TWEET_EVENTS[event_key])
        
        start_time = t0 - timedelta(minutes=30)
        end_time = t0 + timedelta(minutes=60)
        
        mask = (df.index >= start_time) & (df.index <= end_time)
        df_slice = df.loc[mask]

        if df_slice.empty:
            self.setWindowTitle(f"Event Microstructure Visualizer - NO DATA for {asset} during {event_key}")
            return
            
        self.setWindowTitle(f"Event Microstructure Visualizer - {asset} | {event_key}")

        candles = []
        for _, row in df_slice.iterrows():
            candles.append((row['ts_sec'], row['open'], row['close'], row['low'], row['high']))
        
        candle_item = CandlestickItem(candles)
        self.price_plot.addItem(candle_item)
        self.price_plot.add_scalable_item(candle_item)

        timestamps = df_slice['ts_sec'].values
        volumes = df_slice['volume'].values
        
        brushes = [pg.mkBrush('#089981') if c >= o else pg.mkBrush('#f23645') 
                   for c, o in zip(df_slice['close'], df_slice['open'])]
        
        vol_item = pg.BarGraphItem(x=timestamps, height=volumes, width=45, brushes=brushes)
        self.vol_plot.addItem(vol_item)
        self.vol_plot.add_scalable_item(vol_item)

        t0_sec = t0.timestamp()
        self.t0_line_price.setValue(t0_sec)
        self.t0_line_vol.setValue(t0_sec)

        self.price_plot.setXRange(start_time.timestamp(), end_time.timestamp(), padding=0.02)
        self.price_plot.autoRange()
        self.vol_plot.autoRange()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ChartWindow()
    window.show()
    sys.exit(app.exec_())