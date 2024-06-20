import numpy as np
import pandas as pd

from signal_generator import c2c_volatility, correl, signal_generator


def logic_calculator(data_input):
    calculating_data = data_input
    '''
    1. args input
    '''
    short_term_vol = c2c_volatility(calculating_data, 5, 5)
    mid_term_vol = c2c_volatility(calculating_data, 10, 5)
    long_term_vol = c2c_volatility(calculating_data, 24, 5)
    merge_col = ['date', 'time', 'code']
    append_col = ['shortvol', 'midvol', 'longvol']

    vol_structure = pd.merge(short_term_vol, mid_term_vol, left_on=merge_col,
                             right_on=merge_col, how='inner')
    vol_structure = pd.merge(vol_structure, long_term_vol, left_on=merge_col,
                             right_on=merge_col, how='inner')
    # columns_rename = ['date', 'time', 'code', 'shortvol', 'midvol', 'longvol']
    columns_rename = merge_col + append_col
    vol_structure.columns = columns_rename
    vol_structure = pd.merge(calculating_data, vol_structure, left_on=merge_col,
                             right_on=merge_col)
    vol_structure['shortvol_return'] = [0] + list(
        vol_structure['shortvol'].values[1:] / vol_structure['shortvol'].values[:-1] - 1)
    vol_structure['midvol_return'] = [0] + list(
        vol_structure['midvol'].values[1:] / vol_structure['midvol'].values[:-1] - 1)
    vol_structure['longvol_return'] = [0] + list(
        vol_structure['longvol'].values[1:] / vol_structure['longvol'].values[:-1] - 1)

    vol_structure['shortvol_correl'] = correl(vol_structure[['date', 'time', 'return']],
                                              vol_structure['shortvol_return'], 7)
    vol_structure['longvol_correl'] = correl(vol_structure[['date', 'time', 'return']],
                                             vol_structure['longvol_return'], 15)

    vol_structure.loc[:, 'signal'] = vol_structure.apply(signal_generator, threshold=10, axis=1)
    vol_structure.loc[:, 'signal'] = vol_structure.loc[:, 'signal'].apply(lambda x: np.nan if x == 0 else x)
    vol_structure.loc[:, 'signal'] = (vol_structure.loc[:, 'signal'].fillna(method='ffill')).fillna(0)
    # signal = []
    # for i in range(0, vol_structure.shape[0]):
    #     tem_vol_structure = vol_structure.iloc[i]
    #     signal.append(signal_generator(tem_vol_structure, 10))

    signal_new = int(vol_structure['signal'].iloc[-2])
    print(signal_new)