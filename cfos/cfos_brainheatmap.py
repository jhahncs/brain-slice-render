import sys
sys.path.insert(0, '..')

from pathlib import Path
from brainrender._io import load_mesh_from_file
from myterial import orange
from rich import print
from brainglobe_atlasapi import BrainGlobeAtlas
from brainrender import Scene
import brainrender
from brainrender.actors import Points, Line
import numpy as np
from utils import slice_util
from PIL import Image
import os
import subprocess
import  vedo 
import pandas as pd
import brainglobe_heatmap as bgh
import matplotlib.pyplot as plt
import matplotlib 
from matplotlib import gridspec

import importlib
from brainglobe_heatmap import heatmaps

importlib.reload(heatmaps)
import multiprocessing
import brainglobe_heatmap.heatmaps as bgh
from mpl_toolkits.axes_grid1 import make_axes_locatable

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
    filename='logs/log_heatmap.txt', 
    when = "midnight" ,  interval=1, backupCount=30
    )
fileHandler.suffix = "-%Y%m%d"

fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)


bg_atlas = BrainGlobeAtlas("allen_mouse_50um", check_latest=False)


def _get_dict_of_fold_change_values(_df_fold,ptest,  _column, pvalue_th = 0.05, fold_up=1.5, fold_down=0.5):
    global bg_atlas
    data_dict_up = {}
    data_dict_down = {}
    not_found_region_id = []
    for region_id, _row in _df_fold[[_column]].iterrows():
        #if tg_name in ['root','grey','fiber tracts','VS']:
        #    continue
        

        try:
            #print(type(region_id))
            value = bg_atlas.structures[str(region_id)]
        except:
            not_found_region_id.append(str(region_id))
            continue

        #pvalue = ptest.query(f'Region_id=={region_id}')[_column+'_pvalue'].values[0]
        pvalue = ptest[ptest['Region ID'] == region_id][_column].values[0]
        #print(ptest[ptest['Region ID'] == region_id][_column])
        #pvalue = ptest.query(f'color=="{region_id}"')[region_id].values[0]
        if pvalue > pvalue_th:
            continue

        
        if abs(_row[_column]) != np.inf:
            if _row[_column] > fold_up:
                data_dict_up[str(region_id)] = _row[_column]
            elif _row[_column] < fold_down and _row[_column] > 0:
                data_dict_down[str(region_id)] = _row[_column]
    #print('not_found_region_id',len(not_found_region_id))
    df_fold_with_not_found_region = _df_fold[_df_fold.index.isin(not_found_region_id)].drop(['TG number','Region Name'], axis=1)
    #print(df_fold_with_not_found_region)
    not_found_region_id_with_no_zero_value = df_fold_with_not_found_region[df_fold_with_not_found_region.sum(axis=1) > 0].index
#    print(not_found_region_id_with_no_zero_value)
    not_found_region_id_with_no_zero_value = [str(a).lower() for a in not_found_region_id_with_no_zero_value]

    return data_dict_up, data_dict_down, not_found_region_id_with_no_zero_value


def build_dict(cfos, df_fold, ptest, pvalue_th, fold_up, fold_down):
    logger.info("build_dict begin")
    color_2_dict_up = {}
    color_2_dict_down = {}
    num_of_regions_with_fold = []
    #self._get_columns_color(df_fold, self.color_list)
    color_list = list([c for c in df_fold.columns if c not in ['Region ID','TG number','Region Name']])
    logger.info(color_list)
    for c in color_list:
        
        data_dict_up, data_dict_down, not_found_region_id_with_no_zero_value = _get_dict_of_fold_change_values(df_fold,ptest,c,pvalue_th,fold_up,fold_down)
        color_2_dict_up[c] = data_dict_up
        color_2_dict_down[c] = data_dict_down

        color_2_up_down = {}
        #color_2_up_down['cut_method'] = c.split("_")[0]
        color_2_up_down['color'] = c
        color_2_up_down[f'Fold > {fold_up}'] = len(data_dict_up)
        color_2_up_down[f'Fold < {fold_down}'] = len(data_dict_down)
        num_of_regions_with_fold.append(color_2_up_down)
        
        # logger.info(f'{c}, up {len(data_dict_up)}, down {len(data_dict_down)}, {len(not_found_region_id_with_no_zero_value)}')
        logger.info(f'{c}, up {len(data_dict_up)}, down {len(data_dict_down)}, {len(not_found_region_id_with_no_zero_value)}')
    logger.info("build_dict finish")
    _rows = []
    for c in color_list:
        if c in color_2_dict_up:
            for region_id, fold in color_2_dict_up[c].items():
                _row = {}
                _row['color'] = c
                _row['TG number'] = cfos.region_id_2_tg_id[region_id]
                _row['Region ID'] = region_id
                _row['Region Name'] = cfos.region_id_2_name[region_id]
                _row['fold'] = fold 
                _rows.append(_row)
        if c in color_2_dict_down:
            for region_id, fold in color_2_dict_down[c].items():
                _row = {}
                _row['color'] = c
                _row['TG number'] = cfos.region_id_2_tg_id[region_id]
                _row['Region ID'] = region_id
                _row['Region Name'] = cfos.region_id_2_name[region_id]
                _row['fold'] = fold 
                _rows.append(_row)           
    df_sig_region_fold = pd.DataFrame(_rows)
    return color_2_dict_up, color_2_dict_down, df_sig_region_fold
'''
df_num_regions = pd.DataFrame(num_of_regions_with_fold)

df_num_regions.set_index(['color'], inplace=True)

_ttest_count = pd.read_csv('resources/ttest_count.csv', encoding='utf-8')
_ttest_count.set_index(['color'], inplace=True)

df_num_regions = pd.concat([_ttest_count,df_num_regions], axis=1)
df_num_regions.to_csv('output/sig_regions.csv')
'''






def _gen_brain_heatmap(output_dir, ptest,pvalue_th, color_code, fold_up, fold_down,color_2_dict_up,color_2_dict_down):
    

    try:
        plt.clf()
    except:
        pass
    # Create a figure with 6 subplots and plot the scenes

    if len(color_2_dict_up[color_code]) == 0 and len(color_2_dict_down[color_code])==0:
        return
    fig = plt.figure(figsize=(25, 10))
    #fig, axs = plt.subplots(2,7, figsize=(30, 10))
    fig.suptitle(f'{color_code}', fontsize=20)
    spec = gridspec.GridSpec(ncols=21, nrows=9, width_ratios=[1]*20 + [0.05], height_ratios = [1,1,1,0.2,1,1,1,0.2,0.5], wspace=0.001,
                            hspace=0.6)

    maxmin_dict = {}

    ax_row_index = 0
    ax_col_index = 0
    spec_index = 0
    #for subtitle, color, data_dict in [(f'Fold > {fold_up}','Blues',color_2_dict_up[color_code]),(f'Fold < {fold_down}',"Reds_r",color_2_dict_down[color_code])]:
    for _ii, (subtitle, color, _data_dict) in enumerate([(f'Fold > {fold_up}','Blues',color_2_dict_up[color_code]),(f'Fold < {fold_down}',"Reds_r",color_2_dict_down[color_code])]):
        #print(data_dict)
        #logger.info(f'{subtitle},{color_code},{len(data_dict)}')
        print(f'{subtitle},{color_code},{len(_data_dict)}')
        if len(_data_dict) == 0:
            maxmin_dict[_ii] = ""
            continue
        data_dict = {}
        for k,v in _data_dict.items():
            value = bg_atlas.structures[str(k)]
            data_dict[value['acronym']] = v
        #ax_col_index = 0
        #ax = fig.add_subplot(spec[ax_row_index:ax_row_index+3,ax_col_index])
        #ax.set_axis_off()
        #ax.text(0.5, 0.5,f'{subtitle}',  fontsize = 20)
        

        _max = np.max(list(data_dict.values()))
        _min = np.min(list(data_dict.values()))
        print("max/min",_max, _min)
        maxmin_dict[_ii] = str(_max)+"/"+str(_min)
        
        # AP Frontal 12000
        # LR saggital 11400
        # DV horizontal 7000
        for _i, (cut, min_dist, max_dist, gap) in enumerate([('frontal',2000,12000,500),('sagittal',6000,12000,250),('horizontal',2000,7000,250)]):

            ax_col_index = 0
            
            #ax = fig.add_subplot(spec[ax_row_index,ax_col_index])        
            #ax.set_axis_off()
            #ax.text(0.5, 0.5,f'{cut}',  fontsize = 20)
            
            #distance_list = list(range(7500, 10500, 500))
            distance_list = list(range(min_dist, max_dist, gap))
            
            #logger.info(f'{cut},{distance_list}')
            print(f'{cut},{distance_list}')


            for distance in distance_list[:20]:
            #for distance in distance_list[:1]:
                

                scene = bgh.Heatmap(
                    data_dict,
                    position=distance,
                    orientation=cut,
                    thickness=1,
                    format="3D",
                    cmap= color,
                    vmin= _min,
                    vmax= _max,
                    label_regions=False,
                    interactive = False
                )

                #ax = axs[ax_row_index,ax_col_index]
                ax = fig.add_subplot(spec[ax_row_index, ax_col_index])
                
                #if ax_col_index == 19:
                #    scene.plot_subplot(fig=fig, ax=ax, show_cbar=True, hide_axes=True)
                #else:
                scene.plot_subplot(fig=fig, ax=ax, show_cbar=False, hide_axes=True)
                ax.set_title(f'{distance} \u03BCm', fontsize=5)
                ax_col_index += 1
            
            
            if _i == 0:
                ax = fig.add_subplot(spec[ax_row_index:ax_row_index+3, ax_col_index])
                norm = matplotlib.colors.Normalize(vmin=_min, vmax=_max)
                #divider = make_axes_locatable(ax)
                #cax = divider.append_axes("left", size="5%", pad=0.05)
                cbar = fig.colorbar(
                    matplotlib.cm.ScalarMappable(norm=norm, cmap=color), cax=ax,fraction=0.046, pad=0.04
                )
                for t in cbar.ax.get_yticklabels():
                    t.set_fontsize(5)
                cbar.set_label('Fold \u0394\n(EXP/VEH)', fontsize=5)
            ax_row_index += 1
       

        

        
        ax = fig.add_subplot(spec[ax_row_index, :])
        ax.set_axis_off()
        ax.axhline(color='k', linestyle='--', linewidth=2 )
        ax_row_index += 1

    ax_col_index = 0
    ax = fig.add_subplot(spec[ax_row_index,:])
    ax.set_axis_off()
    ax.text(0, 0.1, f'Significant regions were determined by a t-test with FDR corrected (pvalue < {pvalue_th})\nBlue color: Fold \u0394 (VEH/EXP) > {fold_up},  {len(color_2_dict_up[color_code])} regions visualized.\nRed color: Fold \u0394 (VEH/EXP) < {fold_down},  {len(color_2_dict_down[color_code])} regions visualized.\nEach three rows is with frontal(Rostal \u2192 Caudal), saggital, horizontal view, respectively\n',  fontsize = 8)
    plt.tight_layout()
    #plt.show()
    fig.savefig(f'{output_dir}/heatmap_{color_code.replace("/","_")}.png', dpi=600, bbox_inches='tight', pad_inches=1)


def gen_brain_heatmap(output_dir,color_list, ptest,pvalue_th, fold_up, fold_down,color_2_dict_up,color_2_dict_down):       
    output_dir_list = []
 
    ptest_list = []
    pvalue_ts_list = []
    color_code_list = []
    fold_up_list= []
    fold_down_list= []
    color_2_dict_up_list= []
    color_2_dict_down_list= []

    for color_code in color_list:
        output_dir_list.append(output_dir)
        ptest_list.append(ptest)
        pvalue_ts_list.append(pvalue_th)

        color_code_list.append(color_code)
        fold_up_list.append(fold_up)
        fold_down_list.append(fold_down)
        color_2_dict_up_list.append(color_2_dict_up)
        color_2_dict_down_list.append(color_2_dict_down)

    print(f'the number of jobs:{len(color_code_list)}')
    with multiprocessing.Pool() as pool: # Use a pool of 4 processes
        pool.starmap(_gen_brain_heatmap, zip(output_dir_list, ptest_list,pvalue_ts_list, color_code_list,fold_up_list,fold_down_list,color_2_dict_up_list,color_2_dict_down_list))
