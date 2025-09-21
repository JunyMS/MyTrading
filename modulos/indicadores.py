import pandas as pd
import numpy as np
import yfinance as yf
import ta
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def find_rsi_divergences_multi(tickers, rsi_period=14, lookback=20, period='1y', interval='1d'):
    """
    Detecta divergencias RSI para uno o varios tickers.
    
    Parámetros:
    - tickers: str o lista de str (ej. 'AAPL' o ['AAPL', 'MSFT'])
    - rsi_period: período del RSI (por defecto 14)
    - lookback: ventana para detectar extremos (por defecto 20)
    - period: período de descarga desde Yahoo Finance (por defecto '1y')
    - interval: intervalo temporal (por defecto '1d')
    
    Devuelve:
    - Diccionario con DataFrames por ticker que contienen las señales de compra/venta.
    """
    if isinstance(tickers, str):
        tickers = [tickers]

    results = {}

    for ticker in tickers:
        df = yf.download(ticker, period=period, interval=interval, multi_level_index=False)
        if df.empty:
            print(f"⚠️ No se pudieron descargar datos para {ticker}")
            continue

        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=rsi_period).rsi()
        df['min_price'] = df['Close'].rolling(window=lookback, center=True).min()
        df['max_price'] = df['Close'].rolling(window=lookback, center=True).max()

        divergences = []
        for i in range(lookback, len(df) - lookback):
            precio_i    = df['Close'].iloc[i]
            min_price_i = df['min_price'].iloc[i]
            max_price_i = df['max_price'].iloc[i]
            rsi_i       = df['RSI'].iloc[i]

            # Bullish divergence → señal de compra
            if precio_i == min_price_i:
                prev_label = df['Close'][:i].idxmin()
                prev_pos   = df.index.get_loc(prev_label)
                if prev_pos < i and rsi_i > df['RSI'].iloc[prev_pos]:
                    divergences.append((df.index[i], '++COMPRAR'))

            # Bearish divergence → señal de venta
            if precio_i == max_price_i:
                prev_label = df['Close'][:i].idxmax()
                prev_pos   = df.index.get_loc(prev_label)
                if prev_pos < i and rsi_i < df['RSI'].iloc[prev_pos]:
                    divergences.append((df.index[i], '--VENDER'))

        results[ticker] = pd.DataFrame(divergences, columns=['Fecha', 'Señal'])

    return results


def find_rsi_divergences_single(ticker, rsi_period=14, lookback=20, period='1y', interval='1d'):
    df = yf.download(ticker, period=period, interval=interval, multi_level_index=False)
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=rsi_period).rsi()

    # 2) Ventanas para extremos
    df['min_price'] = df['Close'].rolling(window=lookback, center=True).min()
    df['max_price'] = df['Close'].rolling(window=lookback, center=True).max()

    divergences = []
    for i in range(lookback, len(df)-lookback):
        precio_i    = df['Close'].iloc[i]
        min_price_i = df['min_price'].iloc[i]
        max_price_i = df['max_price'].iloc[i]
        rsi_i       = df['RSI'].iloc[i]

        # — Bullish divergence —
        if precio_i == min_price_i:
            # etiqueta del mínimo previo
            prev_label = df['Close'][:i].idxmin()
            # posición entera de ese label
            prev_pos = df.index.get_loc(prev_label)
            if prev_pos < i and rsi_i > df['RSI'].iloc[prev_pos]:
                divergences.append((df.index[i], '++COMPRAR'))

        # — Bearish divergence —
        if precio_i == max_price_i:
            prev_label = df['Close'][:i].idxmax()
            prev_pos   = df.index.get_loc(prev_label)
            if prev_pos < i and rsi_i < df['RSI'].iloc[prev_pos]:
                divergences.append((df.index[i], '--VENDER'))

    return pd.DataFrame(divergences, columns=['Fecha', 'Señal'])



def detect_engulfing_patterns(tickers, period='1y', interval='1d', tolerance=0.005, strength_ratio=1.5):
    """
    Detecta patrones Compra y Venta Engulfing en uno o varios tickers.
    
    Parámetros:
    - tickers: str o lista de str (ej. 'AAPL' o ['AAPL', 'MSFT'])
    - period: período de descarga (por defecto '1y')
    - interval: intervalo temporal (por defecto '1d')
    - tolerance: tolerancia para comparar apertura y cierre (por defecto 0.5%)
    - strength_ratio: relación de amplitud entre velas (por defecto 1.5)
    
    Devuelve:
    - Diccionario con DataFrames por ticker que contienen las señales detectadas.
    """
    if isinstance(tickers, str):
        tickers = [tickers]

    results = {}

    for ticker in tickers:
        df = yf.download(ticker, period=period, interval=interval, multi_level_index=False)
        if df.empty:
            print(f"No se pudieron descargar datos para {ticker}")
            continue

        df["Date"] = pd.to_datetime(df.index)
        df.index.name = "time"

        # Clasificación de velas
        df["Candle way"] = np.where(df["Open"] < df["Close"], 1, -1)
        df["amplitude"] = np.abs(df["Close"] - df["Open"])

        # Inicializar columnas
        df["Compra Engulfing"] = np.nan
        df["Venta Engulfing"] = np.nan

        # Compra Engulfing
        df.loc[
            (df["Candle way"].shift(5) == -1) &
            (df["Candle way"].shift(4) == -1) &
            (df["Candle way"].shift(3) == -1) &
            (df["Candle way"].shift(2) == -1) &
            (df["Candle way"].shift(1) == -1) &
            (df["Candle way"] == 1) &
            (df["Close"].shift(1) < df["Open"] * (1 + tolerance)) &
            (df["Close"].shift(1) > df["Open"] * (1 - tolerance)) &
            (df["amplitude"].shift(1) * strength_ratio < df["amplitude"]),
            "Compra Engulfing"
        ] = 1

        # Venta Engulfing
        df.loc[
            (df["Candle way"].shift(5) == 1) &
            (df["Candle way"].shift(4) == 1) &
            (df["Candle way"].shift(3) == 1) &
            (df["Candle way"].shift(2) == 1) &
            (df["Candle way"].shift(1) == 1) &
            (df["Candle way"] == -1) &
            (df["Close"].shift(1) < df["Open"] * (1 + tolerance)) &
            (df["Close"].shift(1) > df["Open"] * (1 - tolerance)) &
            (df["amplitude"].shift(1) * strength_ratio < df["amplitude"]),
            "Venta Engulfing"
        ] = -1

        # Filtrar señales
        signals = df[df["Compra Engulfing"].notna() | df["Venta Engulfing"].notna()]
        results[ticker] = signals[["Date", "Open", "Close", "Compra Engulfing", "Venta Engulfing"]]

    for ticker, df_signals in results.items():
        if df_signals.empty:
            print(f"\nNo se detectaron señales para {ticker}.")
        else:
            print(f"\n📈 Señales para {ticker}:")
            print(df_signals[['Date', 'Compra Engulfing', 'Venta Engulfing']])
    # return results