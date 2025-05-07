#!/usr/bin/env python
# coding: utf-8

# In[3]:


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

import brainglobe_heatmap.heatmaps as bgh
from mpl_toolkits.axes_grid1 import make_axes_locatable


# In[4]:


bg_atlas = BrainGlobeAtlas("allen_mouse_50um", check_latest=False)
#bg_atlas.lookup_df.acronym.values
#regions = ['root']
#obj_file_names = [ str(bg_atlas.meshfile_from_structure(region)) for region in regions ]
#combined_obj_file_name = 'output/combined.obj'
#slice_util.combine_obj_file_list(obj_file_names,combined_obj_file_name)
#root_mesh = load_mesh_from_file(combined_obj_file_name, alpha=0.1, color="black")


# In[5]:


bg_atlas.structures['MOB']


# In[18]:


df_fold =  pd.read_csv('resources/fold.csv')
df_fold.set_index("TG number", inplace=True)

df_id_2_tg_name= pd.read_csv('resources/tg_id_2_tg_name.csv')
tg_id_2_tg_name = {}
tg_name_2_tg_id = {}
for _i, _row in df_id_2_tg_name[['Region ID','Region name']].iterrows():
    tg_id_2_tg_name[_row['Region ID']] = _row['Region name']
    tg_name_2_tg_id[_row['Region name']] = _row['Region ID']






# In[33]:


def get_dict_of_fold_change_values(_df_fold, name_2_id, _column):
    
    data_dict_up = {}
    data_dict_down = {}
    not_found_region_tg_name = []
    for tg_name, _row in _df_fold[[_column]].iterrows():
        if tg_name in ['root','grey','fiber tracts','VS']:
            continue
        
        _id = tg_name
        if tg_name in name_2_id:
            _id = name_2_id[tg_name]

        try:
            value = bg_atlas.structures[str(_id)]
            if abs(_row[_column]) != np.inf:
                if _row[_column] > 2.0:
                    data_dict_up[value['acronym']] = _row[_column]
                elif _row[_column] < 0.5 and _row[_column] > 0:
                    data_dict_down[value['acronym']] = _row[_column]
        except:
            not_found_region_tg_name.append(tg_name)

    df_fold_with_not_found_region = _df_fold[_df_fold.index.isin(not_found_region_tg_name)]
    not_found_region_id_with_no_zero_value = df_fold_with_not_found_region[df_fold_with_not_found_region.sum(axis=1) > 0].index
    not_found_region_id_with_no_zero_value = [a.lower() for a in not_found_region_id_with_no_zero_value]

    return data_dict_up, data_dict_down, not_found_region_id_with_no_zero_value

data_dict_up, data_dict_down, not_found_region_id_with_no_zero_value = get_dict_of_fold_change_values(df_fold,tg_name_2_tg_id,'sag_PV')

print(len(data_dict_up),len(data_dict_down))
print(len(not_found_region_id_with_no_zero_value))




# In[ ]:


color_2_dict_up = {}
color_2_dict_down = {}
num_of_regions_with_fold = []
for c in df_fold.columns:
    data_dict_up, data_dict_down, not_found_region_id_with_no_zero_value = get_dict_of_fold_change_values(df_fold,tg_name_2_tg_id,c)
    color_2_dict_up[c] = data_dict_up
    color_2_dict_down[c] = data_dict_down

    color_2_up_down = {}
    color_2_up_down['cut_method'] = c.split("_")[0]
    color_2_up_down['color'] = c.split("_")[1]
    color_2_up_down['Fold > 2'] = len(data_dict_up)
    color_2_up_down['Fold < 0.5'] = len(data_dict_down)
    num_of_regions_with_fold.append(color_2_up_down)
    
df_num_regions = pd.DataFrame(num_of_regions_with_fold)

df_num_regions.set_index(['cut_method','color'], inplace=True)

_ttest_count = pd.read_csv('resources/ttest_count.csv', encoding='utf-8')
_ttest_count.set_index(['cut_method','color'], inplace=True)

df_num_regions = pd.concat([_ttest_count,df_num_regions], axis=1)
df_num_regions.to_csv('output/sig_regions.csv')


# In[ ]:


# Create a list of scenes to plot
# Note: it's important to keep reference to the scenes to avoid a
# segmentation fault

color_code = 'sag_PV'
for color_code in df_fold:


    plt.clf()
    # Create a figure with 6 subplots and plot the scenes

    fig = plt.figure(figsize=(25, 10))
    #fig, axs = plt.subplots(2,7, figsize=(30, 10))
    fig.suptitle(f'{color_code}', fontsize=20)
    spec = gridspec.GridSpec(ncols=21, nrows=9, width_ratios=[1]*20 + [0.05], height_ratios = [1,1,1,0.2,1,1,1,0.2,0.5], wspace=0.001,
                            hspace=0.6)


    ax_row_index = 0
    ax_col_index = 0
    spec_index = 0
    for subtitle, color, data_dict in [('Fold > 2','Greens',color_2_dict_up[color_code]),('Fold < 0.5',"Reds_r",color_2_dict_down[color_code])]:
        
        print(subtitle,color_code,len(data_dict))
        if len(data_dict) == 0:
            continue
        
        #ax_col_index = 0
        #ax = fig.add_subplot(spec[ax_row_index:ax_row_index+3,ax_col_index])
        #ax.set_axis_off()
        #ax.text(0.5, 0.5,f'{subtitle}',  fontsize = 20)
        
        _max = np.max(list(data_dict.values()))
        _min = np.min(list(data_dict.values()))
        
        
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
            print(cut, len(distance_list))
            
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
m
    ax_col_index = 0
    ax = fig.add_subplot(spec[ax_row_index,:])
    ax.set_axis_off()
    ax.text(0, 0.1, f'The first three rows: Fold \u0394 > 2,  {len(color_2_dict_up[color_code])} regions visualized\nThe last three rows: Fold \u0394 < 0.5,  {len(color_2_dict_down[color_code])} regions visualized\nEach three rows is with frontal(Rostal \u2192 Caudal), saggital, horizontal view, respectively\n',  fontsize = 8)
    plt.tight_layout()
    #plt.show()
    fig.savefig(f'output/heatmap_{color_code.replace("/","_")}.png', dpi=600, bbox_inches='tight', pad_inches=1)


# In[ ]:





# In[ ]:





# In[ ]:




