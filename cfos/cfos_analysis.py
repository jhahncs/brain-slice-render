from openpyxl import Workbook
from openpyxl import load_workbook
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os
import itertools
from datetime import datetime
import joblib
from scipy import stats
from sklearn.decomposition import PCA
#from tqdm.notebook import tqdm
from tqdm import tqdm
from sklearn.preprocessing import StandardScaler
from matplotlib import font_manager as fm
import openpyxl
import shutil
import subprocess
import seaborn as sns
from statsmodels.stats.multitest import multipletests
import importlib
import multiprocessing
import shutil
import tifftools


#status = subprocess.check_output('zip /disk2/2024_mice/heatmap.zip /disk2/2024_mice/heatmap_*', shell=True)
#status = subprocess.check_output('cp /disk2/2024_mice/heatmap.zip output', shell=True)
#print(status)

import cfos_util
importlib.reload(cfos_util)

import cfos_stat
importlib.reload(cfos_stat)
import cfos_brainheatmap
importlib.reload(cfos_brainheatmap)
from cfos_stat import cal_fold, cal_pvalue, cal_fdr

output_dir = "output"
#try:
#    shutil.rmtree(output_dir)
#except:
#    pass
#try:
#    os.mkdir(output_dir)
#except:
#    pass  
filename = '/home/jhahn/brain-slice-render/cfos/resources/SST_PV_cfos_Summary_FINAL_JIN_ALON.xlsx'
#project_dir = 'C:/workkspace/brainrender/web_cfos/brain/public/projects/output'
PROJECT_ROOT = '/home/jhahn/brain-slice-render/web_cfos/projects'
DATA_NAME = 'cor_sag_averaged'


DEBUG = False
g1_name = 'CFOSgradient_EXP'
g2_name = 'CFOSgradient_VEH'
g1_hemisphere = 'sag'
g2_hemisphere = 'sag'
log_2 = True
#g1_name = 'PV_SST_CFOSgradient_VEH'
#g2_name = 'PV_SST_CFOSgradient_EXP'
for hemisphere in ['cor','sag','female','male',None]:

    for (g1_name, g2_name) in [('CFOSgradient_EXP','CFOSgradient_VEH'),('PV_SST_CFOSgradient_EXP','PV_SST_CFOSgradient_VEH')]:

        if hemisphere is None:
            DATA_NAME = g1_name.split("_")[0]
            cor_vs_sag_analysis = False
        else:
            DATA_NAME = g1_name.split("_")[0]+"_"+hemisphere
            cor_vs_sag_analysis = True
        #DATA_NAME = 'cfos_sag_vs_sag'
        project_dir = f'{PROJECT_ROOT}/{DATA_NAME}'
        cfos = cfos_util.Cfos(filename, project_dir, cor_vs_sag_analysis = cor_vs_sag_analysis, load_from_files=False)


        params = cfos_util.Cfos_params()


        params.group1_name = g1_name
        params.group2_name = g2_name
        params.group1_hemisphere = hemisphere
        params.group2_hemisphere = hemisphere
        params.multipleCompareCorrectionMethod = 'FDR'


        params.fold_up = 999
        params.fold_down = 0.0
        params.color = 'CFOShigh'
        params.dataname = DATA_NAME
        params.num_of_imgs_in_brain_heatmap = 8
        params.dist_label = False
        params.log_2_transform = True

        cfos.build_group1_and_group2(params.group1_name,params.group1_hemisphere,params.group2_name, params.group2_hemisphere,
                                    log_2 = params.log_2_transform, delete_rows_with_zeros = False, load_from_files = False)
        
        for pairwiseCompareMethod in ['moderated-t-test','t-test'][:1]:
            params.pairwiseCompareMethod = pairwiseCompareMethod

            for (fdr_alpha,pvalue_th) in [(0.1,0.1), (0.05,0.05)][:1]:
            #for fdr_alpha in [0.1]:
                params.fdr_alpha = fdr_alpha
            #for pvalue_th in [0.05]:
                params.pvalue_th = pvalue_th

                

                folder_id = cfos.add_exp_param(params)


                
                filename_pairwiseCompare= f'{project_dir}/{folder_id}/pairwise_{params.pairwiseCompareMethod}.csv'


                os.makedirs(project_dir+"/"+str(folder_id), exist_ok=True)
                if params.log_2_transform:
                    filename_fold= f'{PROJECT_ROOT}/{params.dataname}/{folder_id}/foldchange_log2.csv'
                else:
                    filename_fold= f'{PROJECT_ROOT}/{params.dataname}/{folder_id}/foldchange.csv'

                df_fold, g1_sample_ids, g2_sample_ids = cal_fold(cfos, params.log_2_transform, cfos.df_by_two_group_and_color, g1_name, g2_name, filename_fold)
                
                _stat_name = params.stat_test_name(g1_sample_ids, g2_sample_ids, fdr = False)

                signal_log2_min = -0.1
                signal_log2_max = 0.1
                if df_fold is not None :
                    numeric_arr = pd.to_numeric(df_fold[cfos.color_name_list_full].min(), errors='coerce')
                    min_val = np.nanmin(numeric_arr)
                    numeric_arr = pd.to_numeric(df_fold[cfos.color_name_list_full].max(), errors='coerce')
                    max_val = np.nanmax(numeric_arr)
                    print(f"min_val/max_val : {min_val}/{max_val}")
                    _max_value = np.max([abs(min_val),abs(max_val)])

                    if _max_value > signal_log2_max:
                        signal_log2_min = -_max_value
                        signal_log2_max = _max_value
                    cfos_brainheatmap._draw_heatmap_for_all_signals(params.log_2_transform,f'{project_dir}/{folder_id}/signal_heatmap.png',
                                                                    df_fold,cfos.color_name_list_full, 
                                                                    params.group1_name,params.group1_hemisphere, params.group2_name, params.group2_hemisphere,
                                                                    _stat_name, signal_log2_min, signal_log2_max)

                                                                    
                df_pairwise_test = cfos_stat.cal_pvalue(cfos, cfos.df_by_two_group_and_color, params.pairwiseCompareMethod, 
                                                        filename_pairwiseCompare, sigle_core_mode = False, test_mode = False)

                filename_multiplecorrection = f'{project_dir}/{folder_id}/multiplecorrection_{params.multipleCompareCorrectionMethod}.csv'


                df_fdr_permutation_test = cfos_stat.cal_fdr(cfos, df_pairwise_test,  _alpha = params.fdr_alpha, result_filename=filename_multiplecorrection)

                color_2_dict_up, color_2_dict_down, df_sig_region_fold, df_sig_region_fold_merged= cfos_brainheatmap.build_dict(cfos, df_fold, df_fdr_permutation_test, params)
                
                _stat_name = params.stat_test_name(g1_sample_ids, g2_sample_ids, fdr = True)


                cfos_brainheatmap.gen_brain_heatmap(cfos,project_dir+"/"+str(folder_id), df_fdr_permutation_test, 
                                                    cfos.color_name_list_full, color_2_dict_up,color_2_dict_down, params,_stat_name, single_core_mode = False)
                
                
                
                if df_sig_region_fold is not None :
                    df_sig_region_fold.sort_values(by=['color', 'TG number'], ascending=True).to_csv(f'{project_dir}/{folder_id}/regions_sig.csv',index=None)

                    #df_sig_region_fold_merged['TG number'] = pd.to_numeric(df_sig_region_fold_merged['TG number'])
                    #df_sig_region_fold_merged.sort_values(by=['TG number'], ascending=True).to_csv(f'{project_dir}/{folder_id}/regions_all.csv',index=None)


                    cfos_brainheatmap._draw_heatmap_for_all_signals(params.log_2_transform,f'{project_dir}/{folder_id}/signal_heatmap_significant_only.png',
                                                                    df_sig_region_fold_merged,cfos.color_name_list_full, 
                                                                    params.group1_name,params.group1_hemisphere, params.group2_name, params.group2_hemisphere,
                                                                    _stat_name, signal_log2_min, signal_log2_max)
                if DEBUG:
                    break

            if DEBUG:
                break
        if DEBUG:
            break
    if DEBUG:
        break
