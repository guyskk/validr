import numpy as np
import pandas as pd


def quantile_filter(series):
    """keep smallest 50%"""
    series = series[series < series.quantile(0.5)]
    series.index = range(len(series))
    return series


def fft_filter(series):
    """keep the stable part"""
    return np.abs(np.fft.fft(series))[0]/len(series)


def analyze(result):
    df = pd.DataFrame(result)
    df = df.apply(quantile_filter).apply(fft_filter)
    return 1.0/df


def scores(speeds):
    base = speeds['json:loads-dumps']
    return speeds / base * 1000
