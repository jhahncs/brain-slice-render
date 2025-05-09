import numpy as np
import multiprocessing
from scipy import stats
import pandas as pd
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.multitest import multipletests

import logging
import os
from datetime import datetime
# 로그 생성
logger = logging.getLogger()

# 로그의 출력 기준 설정
logger.setLevel(logging.INFO)

# log 출력 형식
formatter = logging.Formatter('%(asctime)s[%(levelname)s]: %(message)s')

while logger.hasHandlers():
    logger.removeHandler(logger.handlers[0])
    
    
# log 출력
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# log 출력
try:
    os.mkdir('logs')
except:
    pass

fileHandler = logging.handlers.TimedRotatingFileHandler(
    filename='logs/log_stat.txt', 
    when = "midnight" ,  interval=1, backupCount=30
    )
fileHandler.suffix = "-%Y%m%d"

fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)


def mystatistic(x, y):
  return np.mean(x, axis=0) - np.mean(y, axis=0)

def _stat_test(_df_agg, _color, p_or_t):
    #logger.info(_color)
    #print(_color)
    _rows_permutation_test = []
    _df = _df_agg.query(f'color=="{_color}"')
    group_exp = _df[_df['veh_exp'] == 0][_df.columns[3:]]
    group_veh = _df[_df['veh_exp'] == 1][_df.columns[3:]]
    pvalues = None
    if p_or_t == 'permutation_test':
      res = stats.permutation_test((group_exp, group_veh), mystatistic, random_state = None)
      pvalues = res.pvalue
    elif p_or_t == 't_test':
      t_stat, pvalues = stats.ttest_ind(group_exp, group_veh)
    pvalues = [1 if np.isnan(x) else x for x in pvalues]

    _row = {}

    _row['color'] = _color
    for _i, region_id in enumerate(_df.columns[3:]):
      _row[region_id] = pvalues[_i]

    _rows_permutation_test.append(_row)
    _result_df = pd.DataFrame(_rows_permutation_test)
    #print(_result_df)
    return _result_df
    #print(res.pvalue)

  

def cal_pvalue(_df_agg, test_method, region_id_2_tg_id, region_id_2_name, result_filename_permutation='output/pvalue_permutation.csv'):


    if os.path.exists(result_filename_permutation):
        _df_pvalue_permutation_test = pd.read_csv(result_filename_permutation)
        _df_pvalue_permutation_test = _df_pvalue_permutation_test.reset_index(drop=True)
        #_df_pvalue_permutation_test.rename(columns={'Unnamed: 0': 'Region ID'}, inplace=True)
        _df_pvalue_permutation_test['Region ID'] = _df_pvalue_permutation_test['Region ID'].astype(str)
        return _df_pvalue_permutation_test
    df_list = []
    color_code_list = []
    p_t_list = []
    for _color in list(set(_df_agg['color'].values)):
        df_list.append(_df_agg)
        color_code_list.append(_color)
        p_t_list.append(test_method)

    logger.info(f'the number of jobs:{len(color_code_list)}')
    with multiprocessing.Pool() as pool: # Use a pool of 4 processes
        results = pool.starmap(_stat_test, zip(df_list, color_code_list, p_t_list))
    df_pvalue = pd.concat(results)

    df_pvalue = _transpose(df_pvalue,  region_id_2_tg_id, region_id_2_name)
    df_pvalue.to_csv(result_filename_permutation, index=None)
    logger.info(f'saved:{result_filename_permutation}')


    return df_pvalue

def _transpose(_df,  region_id_2_tg_id, region_id_2_name):   
    '''
    _df_pvalue_permutation_test = _df[_df.columns[1:]]
    _df_pvalue_permutation_test.set_index("color", inplace=True)
    
    _df_pvalue_permutation_test = _df_pvalue_permutation_test.T
    _df_pvalue_permutation_test.index.name = 'Region ID'
    _df_pvalue_permutation_test = _df_pvalue_permutation_test.reset_index()
    print(_df_pvalue_permutation_test)
    _df_pvalue_permutation_test['TG number'] = _df_pvalue_permutation_test.index.map(region_id_2_tg_id)
    _df_pvalue_permutation_test['Region Name'] = _df_pvalue_permutation_test.index.map(region_id_2_name)
    _df_pvalue_permutation_test = _df_pvalue_permutation_test[['TG number','Region ID','Region Name'] + list(_df_pvalue_permutation_test.columns[1:-2])]
    return _df_pvalue_permutation_test
    '''   

    #_df = df_pvalue_permutation_test.copy()

    _df = _df.set_index("color").T   

    _df.index.name = 'Region ID'

    #_df = _df.reset_index()
    #print(_df)
    _df['TG number'] = _df.index.map(region_id_2_tg_id)
    _df['Region Name'] = _df.index.map(region_id_2_name)
    _df = _df.reset_index()
    color_columns = [c for c in _df.columns if c not in ['TG number','Region Name','Region ID']]
    #print(_df)
    _df = _df[['TG number','Region ID','Region Name'] + color_columns]
    return _df


def _cal_fdr(_row, columns, _alpha = 0.05):
  #print(_row[df_pvalue.columns[2:]])
  reject, p_corrected, _, _ = multipletests(_row[columns], alpha=_alpha, method='fdr_bh')
  _rows_permutation_test = []
  _row_new = {}
  _row_new['Region ID'] = str(_row['Region ID'])
  for _i, region_id in enumerate(columns):
    _row_new[region_id] = p_corrected[_i]

  _rows_permutation_test.append(_row_new)
  _df = pd.DataFrame(_rows_permutation_test)
  
  #_df.index = _row.index
  return _df


def cal_fdr(_df_pvalue,  region_id_2_tg_id, region_id_2_name,_alpha = 0.05, result_filename='output/pvalue_permutation_fdr.csv'):


    if os.path.exists(result_filename):
        final_df = pd.read_csv(result_filename)
        final_df = final_df.reset_index(drop=True)
        final_df['Region ID'] = final_df['Region ID'].astype(str)
        return final_df

    color_columns = [c for c in _df_pvalue.columns if c not in ['TG number','Region Name','Region ID']]

    row_list = []
    columns_list = []
    _alpha_list = []
    for _i, _row in _df_pvalue.iterrows():
        row_list.append(_row)
        columns_list.append(color_columns)
        _alpha_list.append(0.05)

    logger.info(f'the number of jobs:{len(row_list)}')
    with multiprocessing.Pool() as pool: # Use a pool of 4 processes
        results = pool.starmap(_cal_fdr, zip(row_list, columns_list, _alpha_list))
    df_pvalue_fdr = pd.concat(results)
    #final_df.to_csv(result_filename, index=None)

    df_pvalue_fdr = df_pvalue_fdr.set_index('Region ID')
    df_pvalue_fdr['TG number'] = df_pvalue_fdr.index.map(region_id_2_tg_id)
    df_pvalue_fdr['Region Name'] = df_pvalue_fdr.index.map(region_id_2_name)
    #print(df_pvalue_fdr.columns)
    #print(df_pvalue_fdr.index)
    #print(df_pvalue_fdr)
    df_pvalue_fdr = df_pvalue_fdr.reset_index()
    #print(df_pvalue_fdr)
    df_pvalue_fdr = df_pvalue_fdr[['TG number','Region ID','Region Name'] + color_columns]
    #df_pvalue_fdr.index =None
    df_pvalue_fdr.to_csv(result_filename, index=None)
    logger.info(f'saved:{result_filename}')
    '''
    #_df_pvalue_permutation_test.set_index("color", inplace=True)
    df_pvalue_fdr.index.name = 'Region ID'
    #_df_pvalue_permutation_test = _df_pvalue_permutation_test.T


    '''
    return df_pvalue_fdr

def cal_fold(cfos, df_mean_cor_sag, result_filename="output/fold.csv"):
        
    

    _df_list = []
    _df_columns = []
    for _color in list(set(df_mean_cor_sag['color'].values)):
        #for _cut_method in ['cor','sag']:

        _df_total_veh = df_mean_cor_sag.query(f'color=="{_color}" and veh_exp == 0 ').drop(['veh_exp','color','sample_id'],axis=1).copy()
        _df_total_exp = df_mean_cor_sag.query(f'color=="{_color}" and veh_exp == 1 ').drop(['veh_exp','color','sample_id'],axis=1).copy()
            
        #_df_fold_temp = _df_total_exp.mean(axis=0) / _df_total_veh.mean(axis=0)
        _df_total_exp_veh = pd.concat([_df_total_exp.mean(axis=0), _df_total_veh.mean(axis=0)], axis=1)
        _row_list = []
        for _i, _row in _df_total_exp_veh.iterrows():
            _row_new = {}

            #_row_new['TG number'] = region_id_2_tg_id[_i]
            _row_new['Region ID'] = _i
            #_row_new['Region Name'] = region_id_2_name[_i]
            #print(_i, _row)
            #if _row[1] == 0:
            #    print(_row)
            if _row[0] < _row[1]:
                if _row[1] == 0:
                    _row_new['fold'] = 0
                else:
                    _row_new['fold'] = _row[0] / _row[1]
            else:
                if _row[1] == 0:
                    _row_new['fold'] = 0
                else:
                    _row_new['fold'] = _row[0] / _row[1]
            _row_list.append(_row_new)
        _df_fold_temp = pd.DataFrame(_row_list)
        _df_fold_temp.set_index('Region ID', inplace=True)
        #_df_fold_temp

        _df_list.append(_df_fold_temp)
        _df_columns.append(f'{_color}')
    _df_fold = pd.concat(_df_list, axis=1)
    _df_fold.columns = _df_columns
    _df_fold = _df_fold.rename(index=cfos.tg_num_2_name)
    #_df_fold = np.log(_df_fold)
    _df_fold = _df_fold.replace(np.nan, 0)
    _df_fold = _df_fold.replace(np.inf, 0)
    _df_fold['TG number'] = _df_fold.index.map(cfos.region_id_2_tg_id)
    _df_fold['Region Name'] = _df_fold.index.map(cfos.region_id_2_name)
    _df_fold = _df_fold[['TG number','Region Name'] + list(_df_fold.columns[:11])]
    #_df_fold.set_index('TG number', inplace=True)
    

    _df_fold.to_csv(result_filename)
    return  _df_fold