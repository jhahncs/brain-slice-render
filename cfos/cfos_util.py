import logging

import pandas as pd
from collections import OrderedDict

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import itertools
from openpyxl import Workbook
from openpyxl import load_workbook

import logging.handlers
import re
import os
from datetime import datetime
import glob
#print(logging)
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
    os.makedirs('logs')
except:
    pass

fileHandler = logging.handlers.TimedRotatingFileHandler(
    filename='logs/log.txt', 
    when = "midnight" ,  interval=1, backupCount=30
    )
fileHandler.suffix = "-%Y%m%d"

fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

def filename_from_params(group1_name, group2_name, pvalue_th, fold_up, fold_down):
    return f'{group1_name}_{group2_name}_p_{str(pvalue_th)}_up_{str(fold_up)}_down_{str(fold_down)}'
def sanitize_folder_name(folder_name):
  """Sanitizes a folder name by replacing invalid characters with underscores."""
  # Replace invalid characters with underscores
  sanitized_name = re.sub(r'[\\/:*?"<>|]', '_', folder_name)
  # Remove leading and trailing spaces
  sanitized_name = sanitized_name.strip()
  # Replace multiple spaces with a single space
  sanitized_name = re.sub(r'\s+', ' ', sanitized_name)
  return sanitized_name
class Cfos():
    def __init__(self, filename, output_dir='output', load_from_files = False):
        logger.info("cfos init begin")
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.prefix_to_remove_column = ['Mean_','SEM_','Unnamed',"average","VEH","EXP","mean","sem","%error",'Analyses']

        
        self.df_dict = {}
        
        if not load_from_files :
            logger.info(f'loading: {filename}')
            #filename = 'resources/SST_PV_cfos_Summary_Jin_Mehdi_March25 (1).xlsx'
            wb = load_workbook(filename)
            for sheet in wb.worksheets:
                df_name = sanitize_folder_name(sheet.title)
                df_temp = pd.read_excel(open(filename, 'rb'), sheet_name=sheet.title)

                self.df_dict[df_name] = df_temp
                wb = load_workbook(filename)
                logger.info(f'{sheet.title} -> {df_name}')
            wb.close()

            for _name in self.df_dict:
                logger.info(f"preprocessed:{_name}")
                self.df_dict[_name] = self._proprocess(self.df_dict[_name])
                
                filename_df_temp =f'{output_dir}/df_sheet_{_name}.csv'
                logger.info(f"{_name} sheet was saved into: {filename_df_temp}")
                self.df_dict[_name].to_csv(filename_df_temp, index=None)

        self.df_dict = {}
        self.group_names = []
        for _i, file in enumerate(glob.glob(f'{output_dir}/df_sheet_*.csv')):
            _name = file[len(f'{output_dir}/df_sheet_'):-4]
            self.group_names.append(_name)
            logger.info(f"{_name} sheet loaded from:{file}'")
            self.df_dict[_name] = pd.read_csv(f'{file}')
            self._int_2_str(self.df_dict[_name])
            
            if _i == 0:
                self.color_list_full = list(set([c.split("_")[1] for c in self.df_dict[_name].columns if len(c.split("_")) == 2]))
                logger.info(f"{self.color_list_full}")
                id_mapping_filename = f'{output_dir}/id_name.csv'
                logger.info(f"id mappings saved into: {id_mapping_filename}")
                self.build_id_mappings(self.df_dict[_name], id_mapping_filename)

            logger.info(f"{_name}: {self._get_sample_ids(_name)}")
            logger.info(f"{_name}: {len(self.df_dict[_name])} regions")
            logger.info(f"{_name}: {len(self.df_dict[_name].columns)} columns")
            logger.info(list(self.df_dict[_name].columns[:5]))

        #assert len(self.df_exp) == len(self.df_veh), 'not the same size in EXP and VEH'

        self.group_names = sorted(self.group_names)
        logger.info(f"group names:{self.group_names}")
        logger.info("cfos init done")
        #df_exp.head()


    def preprocess_summary(self):
        summary = OrderedDict()
        summary['color'] = ", ".join(self.color_list_full)

        for _group_name in self.group_names:
            summary[_group_name] = ", ".join(self._get_sample_ids(_group_name))

        #summary['The number of regions with all zero in exp and veh:'] = len(self.region_ids_with_all_zero_exp_veh)

        
        return summary



    def build_group1_and_group2(self, df_group1_name, df_group2_name, load_from_files = False):
        df_group1 = self.df_dict[df_group1_name]
        df_group2 = self.df_dict[df_group2_name]
        filename_df_exp_veh = f'{self.output_dir}/df_{df_group1_name}_{df_group2_name}.csv'

        filename_df_raw = f'{self.output_dir}/df_{df_group1_name}_{df_group2_name}_by_color.csv'

        if not load_from_files or (load_from_files and not os.path.exists(filename_df_raw)):
            self.df_by_two_group_and_region = pd.concat([df_group1.drop(['TG number','Region ID','Region name'] ,axis=1),df_group2.drop(['Region ID','Region name'] ,axis=1)], axis=1)
            self.df_by_two_group_and_region.set_index('TG number', inplace=True)
            logger.info(f'saved ({df_group1_name} and {df_group2_name}) into : {filename_df_exp_veh}')
            self.df_by_two_group_and_region.to_csv(filename_df_exp_veh)
            

            #self._get_metadata(self.df_by_two_group_and_region, df_group1_name, df_group2_name)

            df_total = pd.concat([df_group1.drop(['TG number','Region ID','Region name'] ,axis=1),df_group2.drop(['TG number','Region name'] ,axis=1)], axis=1)
            #df_total.set_index('TG number', inplace=True)
            df_total.set_index('Region ID', inplace=True)
            df_total = df_total.T
            df_total['sample_id'] = [a.split('_')[0] for a in df_total.index]
            subject_id_group1 = self._get_sample_ids(df_group1_name)
            df_total['group_name'] = [df_group1_name if a.split('_')[0] in subject_id_group1 else df_group2_name for a in df_total.index]
            df_total['color'] =[ a.split('_')[1] for a in df_total.index]
            df_total.to_csv(filename_df_raw)
            logger.info(f'two group by color data saved into : {filename_df_raw}')



        logger.info(f'loaded ({df_group1_name} and {df_group2_name}) from : {filename_df_exp_veh}')
        self.df_by_two_group_and_region = pd.read_csv(filename_df_exp_veh)
        self._int_2_str(self.df_by_two_group_and_region)
        self.df_by_two_group_and_region.set_index('TG number', inplace=True)
                
        
        self._get_metadata(self.df_by_two_group_and_region, df_group1_name, df_group2_name)

        self.df_by_two_group_and_color = pd.read_csv(filename_df_raw)
        logger.info(f'two group by color data loaded from : {filename_df_raw}')
        self.df_by_two_group_and_color.set_index('Unnamed: 0',inplace=True)



    def _int_2_str(self, _df):
        if 'Region ID' in _df.columns:
            _df['Region ID'] = _df['Region ID'].astype(str)    
        if 'TG number' in _df.columns:
            _df['TG number'] = _df['TG number'].astype(str)    
        


    def _get_columns_color(self, _df, _colors):


        return sorted(list(set([c for c in _df.columns if len(c.split("_")) == 2 and c.split("_")[1] in _colors])))
    

    def _get_sample_ids(self, group_name):
        df_group1 = self.df_dict[group_name]
        
        sample_ids = sorted(list(set([a.split("_")[0] for a in self._get_columns_color(df_group1, self.color_list_full)])))
        return sample_ids
    
    def _get_metadata(self,df_g1_g2, df_group1_name, df_group2_name):
        #print(self.df_exp.columns[3:])
        df_group1 = self.df_dict[df_group1_name]
        df_group2 = self.df_dict[df_group2_name]
        
        
        _df_temp = df_g1_g2[self._get_columns_color(df_g1_g2,self.color_list_full)]
        
        _tg_n = list(_df_temp[(_df_temp.sum(axis=1) == 0)].index)
        
        self.region_ids_with_all_zero_exp_veh = []
        for tg_number in _tg_n: # Taking key and values from dictionary.
            self.region_ids_with_all_zero_exp_veh.append(self.tg_num_2_region_id[tg_number])
        logger.info(f'The number of regions with all zero in {df_group1_name} and {df_group2_name} in {self.color_list_full}: {len(self.region_ids_with_all_zero_exp_veh)}')


        _df_temp = df_g1_g2[self._get_columns_color(df_g1_g2,self.color_list_full)]
        _tg_n = list(_df_temp[~(_df_temp.sum(axis=1) == 0)].index)
        self.region_ids_with_NOT_all_zero_exp_veh = []
        for tg_number in _tg_n: # Taking key and values from dictionary.
            self.region_ids_with_NOT_all_zero_exp_veh.append(self.tg_num_2_region_id[tg_number])
        logger.info(f'The number of regions with NOT all zero in {df_group1_name} and {df_group2_name} in {self.color_list_full}: {len(self.region_ids_with_NOT_all_zero_exp_veh)}')



        #for _c in color_list_full:
        #    _df_exp_veh_color_all = _df_exp_veh[[c for c in _df_exp_veh.columns  if len(c.split("_")) == 3 and c.split("_")[2] == _c]]
        #    s = (_df_exp_veh_color_all != 0).all(axis=1)
        #    print(_c, s.sum())


    def mean_value_by_color(self, region_ids, filename = 'mean_value_by_color.csv'):
        
        #color_columns = [c for c in df_total.columns if c not in ['TG number','Region Name','Region ID']]
        
        #_df_temp = self.df_total[region_ids + ['sample_id','veh_exp','cut_method','color']]
        _df_temp = self.df_total[region_ids + ['sample_id','veh_exp','cut_method','color']]
        _data_list = []
        _row_list = []
        for cut in self.cut_method_list:
            for color in ["SST/cfos fraction","SST-PV/cfos fraction"]:
                for veh_exp in [0,1]:
                    a1 = np.array(_df_temp.query(f'veh_exp == {veh_exp} and cut_method=="{cut}" and color=="{color}"')[_df_temp.columns[:-3]].set_index('sample_id').values.ravel().tolist())
                    a1 = np.nan_to_num(a1, nan=0)
                    
                    _data_list.append(a1)
                    
                    
                    _mean = np.nanmean(a1)
                    _var = np.nanvar(a1)
                    _num_of_zero = np.sum(np.isnan(a1)) + len(a1[a1 == 0])
                    _row = {}
                    _row["veh_exp"] = veh_exp
                    _row["cut"] = cut
                    _row["color"] = color
                    #_row["null"] = _num_of_zero
                    _row["max"] = np.max(a1)
                    _row["min"] = np.min(a1)
                    _row["mean"] = _mean
                    _row["var"] = _var
                    _row["sd"] = _var**2
                    _row_list.append(_row)
        _df_sst_mean = pd.DataFrame(_row_list)
        _df_sst_mean = _df_sst_mean.replace({'veh_exp': {0: 'VEH', 1: "EXP"}})
        _df_sst_mean.to_csv(f'{self.output_dir}/{filename}')
        '''
        fig, ax = plt.subplots()
        labels = list(_df_sst_mean['cut']+"_"+_df_sst_mean['color'])
        ax.boxplot(_data_list)
        ax.set_xticklabels(labels)
        ax.set_ylim(0.0, 80.0)
        ax.set_xlabel('Data Type')
        ax.set_ylabel('Value')

        plt.show()
        '''
        return _df_sst_mean,  _data_list


    def get_agg_df(self, filename='df_mean_cor_sag.csv', load_from_files=False):


        

        if not load_from_files:
            logger.info(f'creating agg data...')
            _df_total = self.df_total
            #print(_df_total.index)
            #print(_df_total.columns)
            #print(_df_total)
            df_mean_cor_sag = _df_total.groupby(['sample_id', 'color','veh_exp'], as_index=False)[_df_total.columns[:-4]].agg('mean')
            df_mean_cor_sag.index.name = None
            df_mean_cor_sag.to_csv(filename, encoding='utf-8', index=None)
            logger.info(f'agg data saved into {filename}')
            
        #self.df_mean_cor_sag = pd.read_csv(filename)
        logger.info(f'loaded agg data: {filename}')



    def _proprocess(self, _df):
        for prefix in self.prefix_to_remove_column:
            _df = _df.drop([a for a in _df.columns if a.startswith(prefix)], axis=1)
        #df_exp = df_exp.drop([a for a in df_exp.columns if a.endswith("fraction")], axis=1)
        _df.drop(_df[pd.isnull(_df['Region name'])].index, inplace=True)
        _df['Region ID'] = _df['Region ID'].astype(str)    
        if '.' in str(_df['Region ID'].values[0]):
            _df['Region ID'] = _df['Region ID'].str[:-2]
        _df['TG number'] = _df['TG number'].astype(int)
        for _c in _df.columns:
            if _c.endswith('SS/cfos fraction'):
                _df = _df.rename(columns={_c: _c.replace('SS/cfos fraction','SST/cfos fraction')})
                
        _df = _df.replace('#DIV/0!',0.0)
        _df = _df.fillna(0)
        for _c in _df.columns[3:]:
            _df[_c] = _df[_c].astype(float)
        return _df

    def build_id_mappings(self, _df, id_mapping_filename):
        self.tg_num_2_name = {}
        self.tg_num_2_region_id = {}
        self.region_id_2_name = {}
        self.region_id_2_tg_id = {}

        for _i, _row in _df[['TG number','Region ID','Region name']].iterrows():
            self.tg_num_2_name[str(_row['TG number'])] = _row['Region name']
            self.tg_num_2_region_id[str(_row['TG number'])] = str(_row['Region ID'])

            self.region_id_2_name[str(_row['Region ID'])] = _row['Region name']
            self.region_id_2_tg_id[str(_row['Region ID'])] = str(_row['TG number'])
        if not os.path.exists(id_mapping_filename):
            _df[['TG number','Region ID','Region name']].to_csv(id_mapping_filename, index = None)
            logger.info(f'id mappings are saved into {id_mapping_filename}')

    def gen_zero_value_heatmap_color(self, output_filename):
        _color = "SST"
        logger.info('gen_zero_value_heatmap')


        #_df_exp_veh_color[~region_ids_with_all_non_zero_exp] = False
        colors = ["white", "green", "red"]  # Define colors for 0 and 1
        cmap = LinearSegmentedColormap.from_list("Binary", colors, len(colors))

        plt.clf()
        fig, axes = plt.subplots(len(self.group_names)+1, 1,figsize=(10,len(self.group_names)*2), sharex=False)
        num_of_regions_with_all_non_zero = 0


        #_df_exp_veh_color = self.df_exp_veh[[c for c in self.df_exp_veh.columns]]
        #num_of_regions_with_all_zero = (_df_exp_veh_color == 0).all(axis=1).sum()


        ax_i = 0
        for _ax_i_ve, group_name in enumerate(self.group_names):
        #for _ax_i_ve, (veh_exp, ids) in enumerate([(0,self.subject_id_veh),(1,self.subject_id_exp)]):
            _this_df = self.df_dict[group_name]
            
            logger.info(f'{group_name}')
            ax = axes[ax_i]
            ax_i += 1
            valid_list = []
            for _color in self.color_list_full:
                #for _cut in ['cor','sag']:

                    _df_exp_veh_color_cor = _this_df[[c for c in _this_df.columns if len(c.split("_")) >= 2 and c.split("_")[1] == _color]]
                    columns_new = [c.split("_")[0] + "_" + c.split("_")[1] for c in _this_df.columns if len(c.split("_")) >= 2 and c.split("_")[1] == _color]
                    _df_exp_veh_color_cor.columns = columns_new
                    _df_exp_veh_color = _df_exp_veh_color_cor
                    s = (_df_exp_veh_color == 0).sum(axis=1)


                    #_df_exp_veh_color = _df_exp_veh[[c for c in _df_exp_veh.columns if c.split("_")[0] in ids and c.split("_")[2] == _color]]
                    #_df_exp_veh_color = _df_exp_veh[[c for c in _df_exp_veh.columns if c.endswith("_"+_color) and "_"+cut+"_" in c ]]

                    #s = (_df_exp_veh_color == 0).sum(axis=1)
                    valid_list.append(s)

            df_non_zero_regions = pd.concat(valid_list, axis=1).reindex(valid_list[0].index)
            #df_non_zero_regions.index = valid_list[0].index
            #print(df_non_zero_regions)
            df_non_zero_regions.columns = self.color_list_full
            #print(df_non_zero_regions)

        #cbar_kws = dict(use_gridspec=False,location="top")
            if ax_i == len(self.group_names): 
                _h = sns.heatmap(ax=ax , data = df_non_zero_regions.T,   xticklabels=True, yticklabels=True, cbar=False, cmap='Reds')
            else:
                _h = sns.heatmap(ax=ax , data = df_non_zero_regions.T,   xticklabels=False, yticklabels=True, cbar=False, cmap='Reds')
            
            # Drawing the frame 
            for _, spine in _h.spines.items(): 
                spine.set_visible(True) 
                spine.set_color('k')
                spine.set_linewidth(0.3) 
            #_h.axhline(y = 0, color='k',linewidth = 3) 
            #_h.axhline(y = df_non_zero_regions.T.shape[1], color = 'r', linewidth = 10)     
            #_h.axvline(x = 0, color = 'k', linewidth = 0.1)     
            #_h.axvline(x = df_non_zero_regions.T.shape[0], color = 'k', linewidth = 0.1) 


            ax.set_title(""+group_name+"",  x=1.04, y=0.4, fontsize=8)
            if ax_i == len(self.group_names):      
                
                ax.set_xlabel("TG number 1 (left) to 1398 (right)",fontsize=5)
                _index_ids = []
                _index_names = []
                for _i in df_non_zero_regions.T.columns:
                    if int(_i) == 1 or int(_i) % 50 == 0 or int(_i)  == df_non_zero_regions.T.columns[-1]:
                        _index_ids.append(int(_i))
                        _index_names.append(df_non_zero_regions.T.columns[int(_i)-1])
                
                ax.set_xticks(_index_ids)
                ax.set_xticklabels(_index_names, fontsize=4, rotation=90)
                ax.tick_params(axis='x', length=0, pad=2)

                
            else:
                ax.set_xlabel("")
                ax.set_xticklabels("")

            #_h.set_xticklabels(_h.get_xticklabels(), fontsize = 7)
            ax.set_yticks([a+0.5 for a in list(range(len(self.color_list_full))) ])
            ax.set_yticklabels(self.color_list_full, fontsize=5)
            ax.tick_params(axis='y', length=0, pad=5)
            #ax.legend()
        #fig.legend(labels=['Low', 'Medium', 'High'], loc="lower center", ncol=4)
        #fig.colorbar(axes[1].collections[0], cax=axes[1])
        axes[ax_i].set_axis_off()
        axes[ax_i].text(0, 0.5, f"The more samples that have a value of 0, the darker the red becomes.", fontsize=6)
        #plt.tight_layout()
        fig.suptitle('The number of samples with zero value')

        fig.savefig(output_filename, dpi=600, bbox_inches='tight', pad_inches=1)
        logger.info('saved:'+output_filename)
        return fig


    def gen_zero_value_heatmap(self, output_filename):
        _color = "SST"
        logger.info('gen_zero_value_heatmap')


        #_df_exp_veh_color[~region_ids_with_all_non_zero_exp] = False
        colors = ["white", "green", "red"]  # Define colors for 0 and 1
        cmap = LinearSegmentedColormap.from_list("Binary", colors, len(colors))

        plt.clf()
        fig, axes = plt.subplots(3, 1,figsize=(10,5), sharex=False)
        num_of_regions_with_all_non_zero = 0


        _df_exp_veh_color = self.df_exp_veh[[c for c in self.df_exp_veh.columns]]
        num_of_regions_with_all_zero = (_df_exp_veh_color == 0).all(axis=1).sum()


        ax_i = 0
        for _ax_i_ve, (veh_exp, ids) in enumerate([(0,self.subject_id_veh),(1,self.subject_id_exp)]):
            logger.info(f'{ids}')
            ax = axes[ax_i]
            ax_i += 1
            valid_list = []
            for _color in self.color_list_full:

                _df_exp_veh_color_cor = self.df_exp_veh[[c for c in self.df_exp_veh.columns if c.split("_")[0] in ids and c.split("_")[2] == _color and c.split("_")[1] == 'cor']]
                _df_exp_veh_color_sag = self.df_exp_veh[[c for c in self.df_exp_veh.columns if c.split("_")[0] in ids and c.split("_")[2] == _color and c.split("_")[1] == 'sag']]
                columns_new = [c.split("_")[0] + "_" + c.split("_")[2] for c in self.df_exp_veh.columns if c.split("_")[0] in ids and c.split("_")[2] == _color and c.split("_")[1] == 'cor']
                _df_exp_veh_color_cor.columns = columns_new
                _df_exp_veh_color_sag.columns = columns_new
                _df_exp_veh_color = _df_exp_veh_color_cor + _df_exp_veh_color_sag
                s = (_df_exp_veh_color == 0).sum(axis=1)


                #_df_exp_veh_color = _df_exp_veh[[c for c in _df_exp_veh.columns if c.split("_")[0] in ids and c.split("_")[2] == _color]]
                #_df_exp_veh_color = _df_exp_veh[[c for c in _df_exp_veh.columns if c.endswith("_"+_color) and "_"+cut+"_" in c ]]

                #s = (_df_exp_veh_color == 0).sum(axis=1)
                valid_list.append(s)


            df_non_zero_regions = pd.concat(valid_list, axis=1).reindex(valid_list[0].index)
            #df_non_zero_regions.index = valid_list[0].index
            df_non_zero_regions.columns = self.color_list_full
            #print(df_non_zero_regions)

        #cbar_kws = dict(use_gridspec=False,location="top")
            if ax_i == 2: 
                _h = sns.heatmap(ax=ax , data = df_non_zero_regions.T,   xticklabels=True, yticklabels=True, cbar=False, cmap='Reds')
            else:
                _h = sns.heatmap(ax=ax , data = df_non_zero_regions.T,   xticklabels=False, yticklabels=True, cbar=False, cmap='Reds')
            
            # Drawing the frame 
            for _, spine in _h.spines.items(): 
                spine.set_visible(True) 
                spine.set_color('k')
                spine.set_linewidth(0.3) 
            #_h.axhline(y = 0, color='k',linewidth = 3) 
            #_h.axhline(y = df_non_zero_regions.T.shape[1], color = 'r', linewidth = 10)     
            #_h.axvline(x = 0, color = 'k', linewidth = 0.1)     
            #_h.axvline(x = df_non_zero_regions.T.shape[0], color = 'k', linewidth = 0.1) 


            ax.set_title(""+str(veh_exp).replace("0","VEH").replace("1","EXP")+"",  x=1.02, y=0.4, fontsize=8)
            if ax_i == 2:      
                
                ax.set_xlabel("TG number 1 (left) to 1398 (right)",fontsize=5)
                _index_ids = []
                _index_names = []
                for _i in df_non_zero_regions.T.columns:
                    if int(_i) == 1 or int(_i) % 50 == 0 or int(_i)  == df_non_zero_regions.T.columns[-1]:
                        _index_ids.append(_i)
                        _index_names.append(df_non_zero_regions.T.columns[_i-1])
                
                ax.set_xticks(_index_ids)
                ax.set_xticklabels(_index_names, fontsize=4, rotation=90)
                ax.tick_params(axis='x', length=0, pad=2)

                
            else:
                ax.set_xlabel("")
                ax.set_xticklabels("")

            #_h.set_xticklabels(_h.get_xticklabels(), fontsize = 7)
            ax.set_yticks([a+0.5 for a in list(range(len(self.color_list_full))) ])
            ax.set_yticklabels(self.color_list_full, fontsize=5)
            ax.tick_params(axis='y', length=0, pad=5)
            #ax.legend()
        #fig.legend(labels=['Low', 'Medium', 'High'], loc="lower center", ncol=4)
        #fig.colorbar(axes[1].collections[0], cax=axes[1])
        axes[ax_i].set_axis_off()
        axes[ax_i].text(0, 0.5, f"VEH: {len(self.subject_id_veh)} samples, EXP: {len(self.subject_id_exp)} samples\nThe more samples that have a value of 0, the darker the red becomes.\nIf one of cor or sag region has non zero value, the region does not to be considered as having zero value", fontsize=6)
        #plt.tight_layout()
        fig.suptitle('The number of samples with zero value')

        fig.savefig(output_filename, dpi=600, bbox_inches='tight', pad_inches=1)
        logger.info('saved:'+output_filename)


    def gen_non_zero_heatmap():
        _color = "SST"
        from matplotlib.colors import LinearSegmentedColormap


        #_df_exp_veh_color[~region_ids_with_all_non_zero_exp] = False
        colors = ["white", "green", "red"]  # Define colors for 0 and 1
        cmap = LinearSegmentedColormap.from_list("Binary", colors, len(colors))
        fig, axes = plt.subplots(5, 1,figsize=(10,5), sharex=False)
        num_of_regions_with_all_non_zero = 0


        _df_exp_veh_color = _df_exp_veh[[c for c in _df_exp_veh.columns]]
        num_of_regions_with_all_zero = (_df_exp_veh_color == 0).all(axis=1).sum()


        ax_i = 0
        for _ax_i_ve, (veh_exp, ids) in enumerate([(0,subject_id_veh),(1,subject_id_exp)]):
            for _ax_i_cut, cut in enumerate(['cor','sag']):
                ax = axes[ax_i]
                ax_i += 1
                valid_list = []
                for _color in color_list:
                    _df_exp_veh_color_all = _df_exp_veh[[c for c in _df_exp_veh.columns  if len(c.split("_")) == 3 and c.split("_")[2] in color_list]]

                    all_non_zero = (_df_exp_veh_color_all != 0).all(axis=1) # all value is non zero
                    num_of_regions_with_all_non_zero = all_non_zero.sum()
                    all_non_zero = all_non_zero.replace(True,2).infer_objects(copy=False)
                    all_non_zero = all_non_zero.replace(False,0).infer_objects(copy=False)
                    
                    _df_exp_veh_color = _df_exp_veh[[c for c in _df_exp_veh.columns if c.split("_")[0] in ids and c.endswith(_color) and cut in c]]
                    #_df_exp_veh_color = _df_exp_veh[[c for c in _df_exp_veh.columns if c.endswith("_"+_color) and "_"+cut+"_" in c ]]

                    s = (_df_exp_veh_color != 0).all(axis=1) # all value is non zero
                    s = s + all_non_zero
                    valid_list.append(s)


                df_non_zero_regions = pd.concat(valid_list, axis=1).reindex(valid_list[0].index)
                #df_non_zero_regions.index = valid_list[0].index
                df_non_zero_regions.columns = color_list
                #print(df_non_zero_regions)

            #cbar_kws = dict(use_gridspec=False,location="top")
                if ax_i == 4: 
                    _h = sns.heatmap(ax=ax , data = df_non_zero_regions.T,   xticklabels=True, yticklabels=True, cbar=False, cmap=cmap)
                else:
                    _h = sns.heatmap(ax=ax , data = df_non_zero_regions.T,   xticklabels=False, yticklabels=True, cbar=False, cmap=cmap)
                
                # Drawing the frame 
                for _, spine in _h.spines.items(): 
                    spine.set_visible(True) 
                    spine.set_color('k')
                    spine.set_linewidth(0.3) 
                #_h.axhline(y = 0, color='k',linewidth = 3) 
                #_h.axhline(y = df_non_zero_regions.T.shape[1], color = 'r', linewidth = 10)     
                #_h.axvline(x = 0, color = 'k', linewidth = 0.1)     
                #_h.axvline(x = df_non_zero_regions.T.shape[0], color = 'k', linewidth = 0.1) 


                ax.set_title(cut+"("+str(veh_exp).replace("0","VEH").replace("1","EXP")+")",  x=1.05, y=0.4, fontsize=8)
                if ax_i == 4:      
                    
                    ax.set_xlabel("TG number 1 (left) to 1398 (right)",fontsize=5)
                    _index_ids = []
                    _index_names = []
                    for _i in df_non_zero_regions.T.columns:
                        if int(_i) == 1 or int(_i) % 50 == 0 or int(_i)  == df_non_zero_regions.T.columns[-1]:
                            _index_ids.append(_i)
                            _index_names.append(df_non_zero_regions.T.columns[_i-1])
                    
                    ax.set_xticks(_index_ids)
                    ax.set_xticklabels(_index_names, fontsize=4, rotation=90)
                    ax.tick_params(axis='x', length=0, pad=2)

                    
                else:
                    ax.set_xlabel("")
                    ax.set_xticklabels("")

                #_h.set_xticklabels(_h.get_xticklabels(), fontsize = 7)
                ax.set_yticks([0.5,1.5,2.5])
                ax.set_yticklabels(color_list, fontsize=5)
                ax.tick_params(axis='y', length=0, pad=5)
        #ax.legend()
        #fig.legend(labels=['Low', 'Medium', 'High'], loc="lower center", ncol=4)
        #fig.colorbar(axes[1].collections[0], cax=axes[1])
        axes[ax_i].set_axis_off()
        axes[ax_i].text(0, -0.01, f"Red: all samples has non zero values for all color in these {num_of_regions_with_all_non_zero} regions\nGreen: all VEH or EXP samples has non zero values in these regions\nWhite: all samples has zero values in these {num_of_regions_with_all_zero} regions", fontsize=6)
        #plt.tight_layout()
        fig.suptitle('Regions with non zero value')

        fig.savefig(f'output/none_zero_values.pdf', dpi=600, bbox_inches='tight', pad_inches=1)

            


'''
zero_region_ids_exp_1_veh_1 = list(set(df_exp_zeros['Region ID'].values).intersection(set(df_veh_zeros['Region ID'].values)))
zero_region_ids_exp_1_veh_0 = list(set(df_exp_zeros['Region ID'].values).difference(set(df_veh_zeros['Region ID'].values)))
zero_region_ids_exp_0_veh_1 = list(set(df_veh_zeros['Region ID'].values).difference(set(df_exp_zeros['Region ID'].values)))

#zero_region_ids_exp_1_veh_1 = list(set(df_exp_zeros.index).intersection(set(df_veh_zeros.index)))
#zero_region_ids_exp_1_veh_0 = list(set(df_exp_zeros.index).difference(set(df_veh_zeros.index)))
#zero_region_ids_exp_0_veh_1 = list(set(df_veh_zeros.index).difference(set(df_exp_zeros.index)))

print(len(zero_region_ids_exp_1_veh_1))
print(len(zero_region_ids_exp_1_veh_0),zero_region_ids_exp_1_veh_0)
print(len(zero_region_ids_exp_0_veh_1),zero_region_ids_exp_0_veh_1)
print(df_exp[df_exp['Region ID'].isin(zero_region_ids_exp_1_veh_0)]['Region name'])
print(df_veh[df_veh['Region ID'].isin(zero_region_ids_exp_0_veh_1)]['Region name'])

#print(df_veh.loc[zero_region_ids_exp_0_veh_1]['Region name'])
'''


'''
# C와 S는 cut angle 차이이기 때문에 값의 차이가 작아야 함

def draw_heatmap(_df_total, _color, ax):
    
    _df_vis = _df_total.query(f'color=="{_color}"').T
    _df_vis = _df_vis.loc[_df_vis.index[:-3]]
    for _c in _df_vis.columns:
        _df_vis[_c] = _df_vis[_c].astype(float)
    _df_vis = _df_vis.rename(index=tg_2_name)


    xticks_labels = []
    xticks = []
    subject_names = []
    subject_ids = []
    subject_sep_ids = []
    for _i in range(len(_df_vis.columns)):
        _name = _df_vis.columns[_i].split("_")
        xticks_labels.append(_name[1][0].upper())
        if _i % 2 == 0:
            
            subject_ids.append(_i+1)
            subject_sep_ids.append(_i+2)
            subject_names.append("\n\n" + _name[0])
        xticks.append(_i)

    
    
    _cmap = matplotlib.colormaps.get_cmap('Reds')
    _cmap.set_bad("tab:cyan")
    
    sns.heatmap(ax=ax, data = _df_vis, cmap=_cmap, rasterized=False, 
                cbar_kws = dict(use_gridspec=False,location="top"), mask=(_df_vis==0)) 
    
    #sns.move_legend(ax, "upper center")
    #fig.legend.set_bbox_to_anchor((0.6, 0.25))
    ax.set_title(_color, fontsize=10)

    if _color_index == 0:
        ax.set_ylabel("TG number 1 (top) to 1398 (bottom)",fontsize=10)
        _index_ids = []
        _index_names = []
        for _i in range(len(_df_vis.index)):
            if _i %2 == 0:
                _index_ids.append(_i)
                _index_names.append(list(_df_vis.index.values)[_i])
        
        ax.set_yticks(_index_ids)
        ax.set_yticklabels(_index_names, fontsize=2)
    else:
        ax.set_ylabel("")
        
    ax.set_xticklabels( xticks_labels, rotation = 0 )
    def forward(x):
        #print(x)
        return x - 0.8

    def backward(y):
        return y + 0.8
    #print(subject_names)
    sec = ax.secondary_xaxis(location= - 0.01, functions=(forward,backward))
    sec.set_xticks(subject_ids, labels=subject_names, rotation = 45, ha='right')
    sec.tick_params('x', length=0, labelsize = 7)
    
    
    sec2 = ax.secondary_xaxis(location=0)
    sec2.set_xticks(subject_sep_ids, labels=[])
    sec2.tick_params('x', length=40, width=0.5, color='grey')
    
    
    #plt.annotate('Experimental', (0,0), (80, -60), xycoords='axes points', textcoords='offset points', va='top')
    #plt.annotate('Vehicle', (0,0), (310, -60), xycoords='axes points', textcoords='offset points', va='top')
    
    #ax.set(xlabel="", ylabel="")
    for i in range(len(_df_vis.columns)):
        if i == 0:
            continue
        elif i % 6 == 0:
            ax.axvline(i, color='blue', lw=0.5)
        elif i % 2 == 0:
            ax.axvline(i, color='grey', lw=0.5)
    #plt.legend(loc='upper center')
    return _df_vis



_color_list = [['PV', 'PV-cfos', 'PV/cfos fraction'],[ 'SST', 'SST-cfos', 'SST/cfos fraction'],
               [ 'SST-PV', 'SST-PV-cfos', 'SST-PV/cfos fraction'],[ 'cfos', 'cfos total']]

for _color_list_sub in _color_list:
    logger.info(" ".join(_color_list_sub))
    num_of_figs = len(_color_list_sub)
    plt.clf()
    fig, axes = plt.subplots(1, num_of_figs,figsize=(num_of_figs*5,10), sharey=True)
    for _color_index, _color in enumerate(sorted(_color_list_sub)):
        ax = axes[_color_index]
        _df_vis = draw_heatmap(df_total, _color, ax)
    fig.savefig(f'output/heatmap_{_color_list_sub[0]}.pdf')


'''