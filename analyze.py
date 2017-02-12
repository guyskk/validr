import matplotlib.pyplot as plt

import pandas as pd


def quantile_filter(series):
    """keep smallest 10%"""
    series = series[series < series.quantile(0.1)]
    series.index = range(len(series))
    return series


def analyze(result, plot=False):
    df_origin = pd.DataFrame(result)
    df_filtered = df_origin.apply(quantile_filter)
    if plot:
        plt.subplot(1, 2, 1)
        plt.title('origin')
        plt.ylabel('time')
        plt.plot(df_origin)
        plt.subplot(1, 2, 2)
        plt.title('filtered')
        plt.ylabel('time')
        plt.plot(df_filtered)
        plt.show()
    return df_filtered.mean()


def scores(result, plot=False):
    scores = analyze(result, plot=plot)
    base = scores['json:loads-dumps']
    return base * 1e+4 / scores


if __name__ == '__main__':
    results = [pd.read_json('result{}.json'.format(i + 1)) for i in range(6)]
    for i in range(6):
        print(scores(results[i]))
