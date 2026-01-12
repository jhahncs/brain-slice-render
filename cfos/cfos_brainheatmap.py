import sys
sys.path.insert(0, '..')
#sys.path.insert(0, '../brainglobe_heatmap')
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
#import brainglobe_heatmap as bgh
import matplotlib.pyplot as plt
import matplotlib 
from matplotlib import gridspec
import tifftools
import importlib
from brainglobe_heatmap import heatmaps

importlib.reload(heatmaps)
import multiprocessing
import brainglobe_heatmap.heatmaps as bgh
from mpl_toolkits.axes_grid1 import make_axes_locatable

import logging
import os
from datetime import datetime
import cfos_util
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
    filename='logs/log_heatmap2.txt', 
    when = "midnight" ,  interval=1, backupCount=30
    )
fileHandler.suffix = "-%Y%m%d"

fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)


bg_atlas = BrainGlobeAtlas("allen_mouse_50um", check_latest=False)
cfos = None

def _get_dict_of_fold_change_values(df_fold, ptest,  _column, pvalue_th = 0.05, fold_up=1.5, fold_down=0.5):
    global bg_atlas
    #global df_fold
    #logger.info(f'{_column}')
    data_dict = {}
    data_dict['up'] = {}
    data_dict['down'] = {}
    data_dict['up'][_column] = {}
    data_dict['down'][_column] = {}

    '''
    data_dict_up = {}
    data_dict_up[_column] = {}
    data_dict_down = {}
    data_dict_down[_column] = {}
    '''
    not_found_region_id = []
    
    for region_id, _row in df_fold[[_column]].iterrows():
        #if tg_name in ['root','grey','fiber tracts','VS']:
        #    continue
        
        '''
        try:
            #print(type(region_id))
            value = bg_atlas.structures[str(region_id)]
        except:
            not_found_region_id.append(str(region_id))
            continue
        '''
        pvalue = ptest.loc[region_id][_column]
        #pvalue = ptest.query(f'Region_id=="{region_id}"')[_column].values[0]
        #pvalue = ptest[ptest['Region ID'] == region_id][_column].values[0]
        #print(ptest[ptest['Region ID'] == region_id][_column])
        #pvalue = ptest.query(f'color=="{region_id}"')[region_id].values[0]
        if pvalue > pvalue_th:
            continue

        _value = _row[_column]
        if abs(_value) != np.inf:
            if _value> fold_up:
                data_dict['up'][_column][str(region_id)] = _value
            elif _value < fold_down and _value > 0:
                data_dict['down'][_column][str(region_id)] = _value
    return data_dict
    #print('not_found_region_id',len(not_found_region_id))
    #df_fold_with_not_found_region = _df_fold[_df_fold.index.isin(not_found_region_id)].drop(['TG number','Region Name'], axis=1)
    #not_found_region_id_with_no_zero_value = df_fold_with_not_found_region[df_fold_with_not_found_region.sum(axis=1) > 0].index
    #not_found_region_id_with_no_zero_value = [str(a).lower() for a in not_found_region_id_with_no_zero_value]

    #return data_dict_up, data_dict_down, not_found_region_id_with_no_zero_value
def _sig_name_csv_merge(_ref_df, df_sig_region_fold, _color_name):
    _df_right = df_sig_region_fold[df_sig_region_fold['color'] == _color_name][['TG number','Region ID','Region Name','fold']].copy()
    _df_right.rename(columns = {'fold': _color_name}, inplace=True) 
    _merged = pd.merge(_ref_df, _df_right, left_on =['TG number','Region ID','Region Name'], right_on=['TG number','Region ID','Region Name'], how='outer')
    return _merged

df_fold = None
def build_dict(cfos, _df_fold, ptest, params: cfos_util.Cfos_params):
    logger.info("build_dict begin")
    #logger.info(f"zero value regions: {len(list(cfos.region_ids_with_all_zero_exp_veh.index))}")

    #_df_fold = _df_fold.drop(list(cfos.region_ids_with_all_zero_exp_veh.index))
    global df_fold
    df_fold = _df_fold
    color_2_dict_up = {}
    color_2_dict_down = {}
    num_of_regions_with_fold = []
    #self._get_columns_color(df_fold, self.color_list)
    color_list = list([c for c in df_fold.columns if c not in ['Region ID','TG number','Region Name']])
    df_fold_list = []
    ptest_list = []
    _color_list = []
    pvalue_list = []
    fold_up_list = []
    fold_down_list = []
    ptest = ptest.set_index('Region ID')
    for c in color_list:
        df_fold_list.append(df_fold)
        ptest_list.append(ptest)
        _color_list.append(c)
        pvalue_list.append(params.pvalue_th)
        fold_up_list.append(params.fold_up)
        fold_down_list.append(params.fold_down)

    '''
    not_found_region_id = []
    for region_id in list(df_fold.index):
        try:
            value = bg_atlas.structures[str(region_id)]
        except:
            not_found_region_id.append(str(region_id))
            continue
    df_fold_with_not_found_region = _df_fold[_df_fold.index.isin(not_found_region_id)].drop(['TG number','Region Name'], axis=1)
    not_found_region_id_with_no_zero_value = df_fold_with_not_found_region[df_fold_with_not_found_region.sum(axis=1) > 0].index
    not_found_region_id_with_no_zero_value = [str(a).lower() for a in not_found_region_id_with_no_zero_value]
    '''

    with multiprocessing.Pool() as pool: # Use a pool of 4 processes
        results_data_dict = pool.starmap(_get_dict_of_fold_change_values, 
                                                                    zip( df_fold_list, ptest_list, _color_list,pvalue_list,fold_up_list,fold_down_list))

        #print(results_data_dict)
        for data_dict in results_data_dict:
            color_2_dict_up.update(data_dict['up'])
            color_2_dict_down.update(data_dict['down'])

        color_2_up_down = {}
        for c in color_list:
            color_2_up_down['color'] = c
            color_2_up_down[f'Fold > {params.fold_up}'] = len(color_2_dict_up[c])
            color_2_up_down[f'Fold < {params.fold_down}'] = len(color_2_dict_down[c])
            num_of_regions_with_fold.append(color_2_up_down)
            logger.info(f'{c}, up {len(color_2_dict_up[c])}, down {len(color_2_dict_down[c])}')
 
    logger.info("build_dict finish")
    _rows = []
    for c in color_list:
        if c in color_2_dict_up:
            for region_id, fold in color_2_dict_up[c].items():
                region_id = str(region_id)
                try:
                    _row = {}
                    _row['color'] = c
                    _row['TG number'] = cfos.region_id_2_tg_id[region_id]
                    _row['Region ID'] = region_id
                    _row['Region Name'] = cfos.region_id_2_name[region_id]
                    _row['fold'] = fold 
                except:
                    print("NOT FOUND:"+region_id)
                    continue
                _rows.append(_row)
        if c in color_2_dict_down:
            for region_id, fold in color_2_dict_down[c].items():
                region_id = str(region_id)
                try:
                    _row = {}
                    _row['color'] = c
                    _row['TG number'] = cfos.region_id_2_tg_id[region_id]
                    _row['Region ID'] = region_id
                    _row['Region Name'] = cfos.region_id_2_name[region_id]
                    _row['fold'] = fold 
                except:
                    print("NOT FOUND:"+region_id)
                    continue   
                _rows.append(_row)           
    


    if len(_rows) > 0:
        df_sig_region_fold = pd.DataFrame(_rows)
        df_sig_region_fold['TG number'] = pd.to_numeric(df_sig_region_fold['TG number'])

        df_sig_region_fold_merged = cfos.df_dict[list(cfos.df_dict.keys())[0]][['TG number','Region ID','Region name']].copy() 
        df_sig_region_fold_merged['TG number'] = df_sig_region_fold_merged['TG number'].astype(int)
        df_sig_region_fold_merged.rename(columns = {'Region name': 'Region Name'}, inplace=True) 
        for color_name in cfos.color_name_list_full:
            df_sig_region_fold_merged = _sig_name_csv_merge(df_sig_region_fold_merged, df_sig_region_fold, color_name)


        return color_2_dict_up, color_2_dict_down, df_sig_region_fold, df_sig_region_fold_merged
    else:
        return color_2_dict_up, color_2_dict_down, None, None
    
'''
df_num_regions = pd.DataFrame(num_of_regions_with_fold)

df_num_regions.set_index(['color'], inplace=True)

_ttest_count = pd.read_csv('resources/ttest_count.csv', encoding='utf-8')
_ttest_count.set_index(['color'], inplace=True)

df_num_regions = pd.concat([_ttest_count,df_num_regions], axis=1)
df_num_regions.to_csv('output/sig_regions.csv')
'''




def build_dict_backup(cfos, df_fold, ptest, pvalue_th, fold_up, fold_down):
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
                region_id = str(region_id)
                try:
                    _row = {}
                    _row['color'] = c
                    _row['TG number'] = cfos.region_id_2_tg_id[region_id]
                    _row['Region ID'] = region_id
                    _row['Region Name'] = cfos.region_id_2_name[region_id]
                    _row['fold'] = fold 
                except:
                    print("NOT FOUND:"+region_id)
                    continue
                _rows.append(_row)
        if c in color_2_dict_down:
            for region_id, fold in color_2_dict_down[c].items():
                region_id = str(region_id)
                try:
                    _row = {}
                    _row['color'] = c
                    _row['TG number'] = cfos.region_id_2_tg_id[region_id]
                    _row['Region ID'] = region_id
                    _row['Region Name'] = cfos.region_id_2_name[region_id]
                    _row['fold'] = fold 
                except:
                    print("NOT FOUND:"+region_id)
                    continue   
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


from matplotlib.transforms import Bbox

def full_extent(ax, pad=0.0):
    """Get the full extent of an axes, including axes labels, tick labels, and
    titles."""
    # For text objects, we need to draw the figure first, otherwise the extents
    # are undefined.
    ax.figure.canvas.draw()
    items = ax.get_xticklabels() + ax.get_yticklabels() 
#    items += [ax, ax.title, ax.xaxis.label, ax.yaxis.label]
    items += [ax, ax.title]
    bbox = Bbox.union([item.get_window_extent() for item in items])

    return bbox.expanded(1.0 + pad, 1.0 + pad)
import seaborn as sns

def _draw_heatmap_for_all_signals(filename_sig_regions,_df_merged, color_name_list_full,group1_name, group2_name, stat_name, fold_up, fold_down):

    def _draw_heatmap_temp(_ax, heatmap_data, color, min_val, max_val):

        cbar_ticks = [min_val, max_val]
        sns.heatmap(heatmap_data, ax=_ax, annot=False, fmt='.1f',# [핵심] 최대값을 색상 범위 끝으로 설정
                        vmax=max_val, vmin=min_val,linewidths=0,    # [핵심] 격자 선의 두께 (보통 0.5 ~ 1 정도가 적당)
                        #linecolor='gray',
                        cbar_kws={
                            'ticks': cbar_ticks,  # 눈금 위치 지정
                            'format': '%.2f',
                        }, cmap=color, xticklabels=100)
        for side in ['top', 'bottom', 'left', 'right']:
            _ax.spines[side].set_visible(True)   # 테두리가 보이게 설정
            _ax.spines[side].set_linewidth(1)    # 테두리 두께 (2로 설정하면 진하게 보임)
            _ax.spines[side].set_color('gray')  # 테두리 색상

        # 3. Y축 방향(가로줄) 경계선 직접 그리기
        # 데이터의 행 개수(rows)와 열 개수(cols)를 구합니다.
        rows, cols = heatmap_data.shape


        _ax.hlines(y=range(1, rows), xmin=0, xmax=cols, colors='gray', linewidths=0.5)
        cbar = _ax.collections[0].colorbar
        cbar.ax.tick_params(labelsize=10)  # 폰트 크기 (원하는 크기로 숫자를 변경하세요)
        cbar.set_label(f'Fold change:\n{group1_name.split("_")[-1]} / {group2_name.split("_")[-1]}' , size=6)
        cbar.ax.tick_params(size=0)
        _ax.tick_params(axis='y', labelrotation=0)
        _ax.set_yticklabels(axes[0].get_yticklabels(), rotation=0, va='center')
    #plt.figure(figsize=(15, 3))  # 그래프 크기 조절
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(20, int(len(color_name_list_full))))
    #plt.yticks(rotation=90) # Y축 글자 수평 정렬
    heatmap_data = _df_merged.set_index('TG number')[sorted(color_name_list_full)].copy()
    heatmap_data[heatmap_data < fold_up] = 0
    _draw_heatmap_temp(axes[0], heatmap_data.T, 'Greens', fold_up, heatmap_data.max().max())

    heatmap_data = _df_merged.set_index('TG number')[sorted(color_name_list_full)].copy()
    heatmap_data[heatmap_data > fold_down] = 0
    _draw_heatmap_temp(axes[1], heatmap_data.T, 'Reds', 0.0, fold_down)

    fig.suptitle(f'{stat_name}', fontsize=10)
    plt.xlabel('TG Number')  # X축 이름
    #plt.ylabel('Signals')  # Y축 이름
    
    plt.tight_layout(rect=[0, 0, 1, 1])
    #plt.show()
    fig.savefig(filename_sig_regions, dpi=600, bbox_inches='tight', pad_inches=1)

def _gen_brain_heatmap(output_dir,params, ptest, color_code,
                       color_2_dict_up,color_2_dict_down, gen_individual_image = False):
    
    
    
    global cfos
    try:
        plt.clf()
    except:
        pass
    # Create a figure with 6 subplots and plot the scenes

    if len(color_2_dict_up[color_code]) == 0 and len(color_2_dict_down[color_code])==0:
        return
    fig = plt.figure(figsize=(25*(params.num_of_imgs_in_brain_heatmap/20), 10))
    #fig, axs = plt.subplots(2,7, figsize=(30, 10))
    fig.suptitle(f'{color_code}  {params.group1_name} / {params.group2_name}', fontsize=20)
    spec = gridspec.GridSpec(ncols=params.num_of_imgs_in_brain_heatmap + 1, nrows=8, 
                             width_ratios=[1]*params.num_of_imgs_in_brain_heatmap + [0.15], 
                             height_ratios = [1,1,1,0.2,1,1,1,0.2], 
                            # height_ratios = [1,1,1,0.2,1,1,1,0.2,0.8], 

                             wspace=0.001,
                            hspace=0.6)

    maxmin_dict = {}

    ax_row_index = 0
    ax_col_index = 0
    spec_index = 0
    not_visualized_regions = []
    #for subtitle, color, data_dict in [(f'Fold > {fold_up}','Blues',color_2_dict_up[color_code]),(f'Fold < {fold_down}',"Reds_r",color_2_dict_down[color_code])]:
    for _ii, (subtitle, color, _data_dict) in enumerate([(f'Fold > {params.fold_up}','Greens',color_2_dict_up[color_code]),(f'Fold < {params.fold_down}',"Reds_r",color_2_dict_down[color_code])]):
        #print(data_dict)
        #logger.info(f'{subtitle},{color_code},{len(data_dict)}')
        print(f'{subtitle},{color_code},{len(_data_dict)}')
        if len(_data_dict) == 0:
            maxmin_dict[_ii] = ""
            continue
        data_dict = {}
        for k,v in _data_dict.items():
            try:
                value = bg_atlas.structures[str(k)]
            except:
                print('not found:',str(k))
                not_visualized_region = {}
                not_visualized_region['Region ID'] = str(k)
                not_visualized_region['Region Name'] = cfos.region_id_2_name[str(k)]
                not_visualized_region['TG Number'] = cfos.region_id_2_tg_id[str(k)]
                not_visualized_regions.append(not_visualized_region)
                continue


            #if len(data_dict) >= 5:
            #    break
            data_dict[value['acronym']] = v
        #ax_col_index = 0
        #ax = fig.add_subplot(spec[ax_row_index:ax_row_index+3,ax_col_index])
        #ax.set_axis_off()
        #ax.text(0.5, 0.5,f'{subtitle}',  fontsize = 20)
        if len(data_dict) == 0:
            logger.info(f'No region found: {subtitle},{color_code}')
            continue
        
        

        _max = np.max(list(data_dict.values()))
        _min = np.min(list(data_dict.values()))
        print("max/min",_max, _min)
        maxmin_dict[_ii] = str(_max)+"/"+str(_min)
        
        # AP Frontal 12000
        # LR saggital 11400
        # DV horizontal 7000
        for _i, (cut, min_dist, max_dist, gap) in enumerate([('frontal',2000,12000,int(500*(20/params.num_of_imgs_in_brain_heatmap))),
                                                             ('sagittal',6000,12000,int(250*(20/params.num_of_imgs_in_brain_heatmap))),
                                                             ('horizontal',2000,7000,int(250*(20/params.num_of_imgs_in_brain_heatmap)))]):

            ax_col_index = 0
            
            #ax = fig.add_subplot(spec[ax_row_index,ax_col_index])        
            #ax.set_axis_off()
            #ax.text(0.5, 0.5,f'{cut}',  fontsize = 20)
            
            #distance_list = list(range(7500, 10500, 500))
            distance_list = list(range(min_dist, max_dist, gap))
            
            #logger.info(f'{cut},{distance_list}')
            print(f'{cut},{distance_list}')

            tiff_files = []
            for distance in distance_list[:params.num_of_imgs_in_brain_heatmap]:
            #for distance in distance_list[:1]:
                

                scene = bgh.Heatmap(
                    data_dict,
                    position=distance,
                    orientation=cut,
                    thickness=1,
                    format="2D",
                    cmap= color,
                    vmin= _min,
                    vmax= _max,
                    label_regions=False,
                    interactive = False
                )
                #scene.show()
                #ax = axs[ax_row_index,ax_col_index]
                ax = fig.add_subplot(spec[ax_row_index, ax_col_index])
                
                #if ax_col_index == 19:
                #    scene.plot_subplot(fig=fig, ax=ax, show_cbar=True, hide_axes=True)
                #else:
                _ind_fig, _ind_p = scene.plot_subplot(fig=fig, ax=ax, show_cbar=False, hide_axes=True)
                #ax.figure.savefig(f'{output_dir}/heatmap_{cut}_{str(distance)}_{params.heatpmap_vis_name()}_{cfos_util.sanitize_folder_name(color_code)}_{params.stat_test_name()}.tiff')

                if gen_individual_image:
                    # Save just the portion _inside_ the second axis's boundaries
                    extent = full_extent(ax).transformed(fig.dpi_scale_trans.inverted())
                    # Alternatively,
                    os.makedirs(f'{output_dir}/{cfos_util.sanitize_folder_name(color_code)}', exist_ok=True)
                    # extent = ax.get_tightbbox(fig.canvas.renderer).transformed(fig.dpi_scale_trans.inverted())
                    ind_file = f'{output_dir}/{cfos_util.sanitize_folder_name(color_code)}/heatmap_{color.replace("_r","")}_{cut}_{str(distance)}_{params.heatpmap_vis_name()}_{cfos_util.sanitize_folder_name(color_code)}_{params.stat_test_name()}.tiff'
                    fig.savefig(ind_file, bbox_inches=extent,dpi=600, pad_inches=1)
                    tiff_files.append(ind_file)

                if params.dist_label == 'true':
                    ax.set_title(f'{distance} \u03BCm', fontsize=5)
                ax_col_index += 1
            
            
            if _i == 0:
                ax = fig.add_subplot(spec[ax_row_index:ax_row_index+3, ax_col_index])
                norm = matplotlib.colors.Normalize(vmin=_min, vmax=_max)
                #divider = make_axes_locatable(ax)
                #cax = divider.append_axes("left", size="5%", pad=0.05)
                cbar = fig.colorbar(
                    matplotlib.cm.ScalarMappable(norm=norm, cmap=color), cax=ax, fraction=0.046, pad=0.04
                )   
                for t in cbar.ax.get_yticklabels():
                    t.set_fontsize(5)
                cbar.set_label(f'Fold \u0394\n({params.group1_name} / {params.group2_name})', fontsize=5)
            ax_row_index += 1
       
                    # Read the first TIFF file
            '''
            merged_tiff_filename = f'{output_dir}/heatmap_{color.replace("_r","")}_{cut}_{"ALL"}_{params.heatpmap_vis_name()}_{cfos_util.sanitize_folder_name(color_code)}_{params.stat_test_name()}.tiff'
            if not os.path.exists(merged_tiff_filename):
                merged_tiff = tifftools.read_tiff(tiff_files[0])

                # Iterate through the remaining files and append their IFDs
                for file in tiff_files[1:]:
                    tiff = tifftools.read_tiff(file)
                    merged_tiff['ifds'].extend(tiff['ifds'])
                tifftools.write_tiff(merged_tiff, merged_tiff_filename)
            
            '''
            
        

        
        ax = fig.add_subplot(spec[ax_row_index, :])
        ax.set_axis_off()
        #ax.axhline(color='k', linestyle='--', linewidth=2 )
        ax_row_index += 1

    ax_col_index = 0
    '''
    ax = fig.add_subplot(spec[ax_row_index,:])
    ax.set_axis_off()
    not_visualized_regions_text = ''
    if len(not_visualized_regions) > 0:
        not_visualized_regions_text += f'{not_visualized_region["Region Name"]}({not_visualized_region["Region ID"]}),'

    ax.text(0, 0.1, f'{len(not_visualized_regions)} regions are not visualized (mis match between TG and Altals): {not_visualized_regions_text}\n{params.stat_desc()}\nGreen color: Fold \u0394 ({params.group1_name}/{params.group2_name}) > {params.fold_up},  {len(color_2_dict_up[color_code])} regions visualized.\nRed color: Fold \u0394 ({params.group1_name}/{params.group2_name}) < {params.fold_down},  {len(color_2_dict_down[color_code])} regions visualized.\nFrontal(Rostal \u2192 Caudal), saggital, horizontal view, respectively\n',  fontsize = 8)
    '''
    plt.tight_layout()
    #plt.show()

    logger.info(f"not_visualized_region:{not_visualized_regions}")

    _filename = f'{output_dir}/one_heatmap_{params.heatpmap_vis_name()}_{cfos_util.sanitize_folder_name(color_code)}_{params.stat_test_name()}.png'
    fig.savefig(_filename, dpi=600, bbox_inches='tight', pad_inches=1)
    logger.info(f'brain heatmap saved into : {_filename}')



    #return plt

def gen_brain_heatmap(_cfos,output_dir, stat_test_result, color_list, 
                      color_2_dict_up,color_2_dict_down, params, single_core_mode = False):       
    
    global cfos
    cfos = _cfos
    output_dir_list = []
    
    ptest_list = []
    parama_list = []
    color_2_dict_up_list= []
    color_2_dict_down_list= []
    color_code_list = []
    for color_code in color_list:
        output_dir_list.append(output_dir)
        parama_list.append(params)
        color_code_list.append(color_code)
        ptest_list.append(stat_test_result)
        color_2_dict_up_list.append(color_2_dict_up)
        color_2_dict_down_list.append(color_2_dict_down)
        if single_core_mode:
            _gen_brain_heatmap(output_dir,params,stat_test_result,color_code, color_2_dict_up,color_2_dict_down )

    if not single_core_mode:
        print(f'the number of jobs:{len(color_code_list)}')
        with multiprocessing.Pool() as pool: # Use a pool of 4 processes
            pool.starmap(_gen_brain_heatmap, zip(output_dir_list,parama_list,ptest_list, color_code_list, color_2_dict_up_list,color_2_dict_down_list))
