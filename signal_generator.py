import pandas as pd
import numpy as np


def c2c_volatility(closeprice_series, timewindow, timeinterval):  # closeprice_series dataframe should contain more than 3 series,date, time and closeprice,columns_name:date, underlying_close
    c2c_volatility_series = pd.DataFrame()
    timewindow = int(timewindow)
    timeinterval = int(timeinterval)
    for i in range(closeprice_series.shape[0] - timewindow):
        tem_closeprice_series = closeprice_series.iloc[i:i + timewindow + 1]
        # print(tem_closeprice_series)
        tem_return_series = tem_closeprice_series['close'].values[1:] / tem_closeprice_series['close'].values[:-1] - 1
        tem_c2c_volatility_series = pd.DataFrame(
            {'date': [tem_closeprice_series['date'].values[-1]], 'time': [tem_closeprice_series['time'].values[-1]],
             'code': [tem_closeprice_series['code'].values[-1]],
             'c2c_volatility': [round((np.std(tem_return_series, ddof=1) * np.sqrt(244 * 240 / timeinterval)), 6)]})
        c2c_volatility_series = c2c_volatility_series.append(tem_c2c_volatility_series)
    return c2c_volatility_series


def correl(return_series, vol_return, timewindow):
    correl_list = [0] * (timewindow - 1)

    for i in range(0, return_series.shape[0] - timewindow + 1):
        # print(return_series[i:i + timewindow], vol_return[i:i + timewindow])
        tem_corr = np.corrcoef(return_series['return'].values[i:i + timewindow], vol_return[i:i + timewindow])[0, 1]
        correl_list.append(tem_corr)

    return correl_list


def signal_generator(tem_vol_structure, threshold):
    if tem_vol_structure['shortvol_return'] > threshold * tem_vol_structure['midvol_return'] and tem_vol_structure[
        'midvol_return'] > threshold * tem_vol_structure['longvol_return'] and abs(
        tem_vol_structure['shortvol_return']) > 0.05:
        vol_signal = 1
    else:
        vol_signal = 0

    if tem_vol_structure['shortvol_correl'] > 0.8 and tem_vol_structure['longvol_correl'] > 0.8:
        trendy_signal = 1
    elif tem_vol_structure['shortvol_correl'] < - 0.8 and tem_vol_structure['longvol_correl'] < - 0.8:
        trendy_signal = -1
    else:
        trendy_signal = 0

    if vol_signal == 1:
        if trendy_signal == 1:
            signal = 1
        if trendy_signal == -1:
            signal = -1
        else:
            if tem_vol_structure['return'] > 0:
                signal = -1
            else:
                signal = 1
    else:
        signal = 0

    return signal
