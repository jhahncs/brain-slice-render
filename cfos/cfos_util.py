import logging

import pandas as pd

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import itertools
from openpyxl import Workbook
from openpyxl import load_workbook

import logging.handlers

import os
from datetime import datetime

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


class Cfos():
    def __init__(self, filename, output_dir='output', load_from_files = False):
        logger.info("cfos init begin")
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.color_list = ['PV','cfos','SST']
        self.prefix_to_remove_column = ['Unnamed',"average","VEH","EXP","mean","sem","%error",'Analyses']
        
        filename_df_exp = output_dir+"/df_exp.csv"
        filename_df_veh = output_dir+"/df_veh.csv"
        filename_df_exp_veh = output_dir+"/df_exp_veh.csv"
        

        if load_from_files:
            self.df_exp = pd.read_csv(filename_df_exp)
            
            self.df_veh = pd.read_csv(filename_df_veh)
        else:
            logger.info(f'loading: {filename}')
            #filename = 'resources/SST_PV_cfos_Summary_Jin_Mehdi_March25 (1).xlsx'
            wb = load_workbook(filename)
            for sheet in wb.worksheets:
                if 'VEH' in sheet.title:        
                    self.df_exp = pd.read_excel(open(filename, 'rb'), sheet_name=sheet.title)
                elif 'EXP' in sheet.title:
                    self.df_veh = pd.read_excel(open(filename, 'rb'), sheet_name=sheet.title)
            wb.close()

            logger.info(f"loaded!")
            self.df_exp = self._proprocess(self.df_exp)
            self.df_veh = self._proprocess(self.df_veh)
            
            logger.info(f"saved into:{filename_df_exp}")
            self.df_exp.to_csv(filename_df_exp, index=None)

            logger.info(f"saved into:{filename_df_veh}")
            self.df_veh.to_csv(filename_df_veh, index=None)

        logger.info(f"EXP: {len(self.df_exp)} samples")
        logger.info(f"VEH: {len(self.df_veh)} samples")
        logger.info(self.df_exp.columns[:5])
        logger.info(self.df_exp.columns[-5:])


        self.color_list_full = list(set([c.split("_")[2] for c in self.df_exp.columns if len(c.split("_")) == 3]))

        logger.info(f"{self.color_list_full}")


        assert len(self.df_exp) == len(self.df_veh), 'not the same size in EXP and VEH'

        id_mapping_filename = f'{output_dir}/id_name.csv'

        if not load_from_files:
            self.df_exp[['TG number','Region ID','Region name']].to_csv(id_mapping_filename, index = None)
            logger.info(f'id mappings are saved into {id_mapping_filename}')

        self.get_id_mappings()

        logger.info(f'construct id mapping dict')

        if not load_from_files:
            self.df_exp_veh = pd.concat([self.df_exp.drop(['TG number','Region ID','Region name'] ,axis=1),self.df_veh.drop(['Region ID','Region name'] ,axis=1)], axis=1)
            self.df_exp_veh.set_index('TG number', inplace=True)
            logger.info(f'saved (exp and veh) into : {filename_df_exp_veh}')
            self.df_exp_veh.to_csv(filename_df_exp_veh)
        else:
            logger.info(f'loaded (exp and veh) from : {filename_df_exp_veh}')
            self.df_exp_veh = pd.read_csv(filename_df_exp_veh)
            self.df_exp_veh.set_index('TG number', inplace=True)
        
        
        
        self._get_metadata()

        self.get_raw_df(output_dir+'/df_raw.csv',load_from_files)
        self.get_agg_df(output_dir+'/df_mean_cor_sag.csv',load_from_files)
        

        logger.info("cfos init done")
        #df_exp.head()
    def preprocess_summary(self):
        summary = ''
        summary += f'EXP: {self.subject_id_exp}\n'
        summary += f'VEH: {self.subject_id_veh}\n'
        summary += f'color:{self.color_list_full}'
        summary += f'The number of regions with all zero in exp and veh: {len(self.region_ids_with_all_zero_exp_veh)}'

        
        return summary


    def verify(self):
        
        return [c for c in _df.columns if len(c.split("_")) == 3 and c.split("_")[2] in _color_list]

    def _get_columns_color(self, _df, _color_list):
        return [c for c in _df.columns if len(c.split("_")) == 3 and c.split("_")[2] in _color_list]

    def _get_metadata(self):
        #print(self.df_exp.columns[3:])

        _color_columns_exp = self._get_columns_color(self.df_exp, self.color_list)
        _color_columns_veh = self._get_columns_color(self.df_veh, self.color_list)
        self.cut_method_list = list(set([a.split("_")[1] for a in _color_columns_exp]))
        self.color_list_full = list(set([a.split("_")[2] for a in _color_columns_exp]))

        logger.info(f'cut:{self.cut_method_list}')
        logger.info(f'color:{self.color_list_full}')

        
        self.subject_id_exp = list(set([a.split("_")[0] for a in _color_columns_exp]))
        self.subject_id_veh = list(set([a.split("_")[0] for a in _color_columns_veh]))
        logger.info(f'sample ids in EXP: {self.subject_id_exp}')
        logger.info(f'sample ids in VEH: {self.subject_id_veh}')

        
        _df_temp = self.df_exp_veh[self._get_columns_color(self.df_exp_veh,self.color_list)]
        
        _tg_n = list(_df_temp[(_df_temp.sum(axis=1) == 0)].index)
        
        self.region_ids_with_all_zero_exp_veh = []
        for tg_number in _tg_n: # Taking key and values from dictionary.
            self.region_ids_with_all_zero_exp_veh.append(self.tg_num_2_region_id[tg_number])
        logger.info(f'The number of regions with all zero in exp and veh in {self.color_list}: {len(self.region_ids_with_all_zero_exp_veh)}')


        _df_temp = self.df_exp_veh[self._get_columns_color(self.df_exp_veh,self.color_list)]
        _tg_n = list(_df_temp[~(_df_temp.sum(axis=1) == 0)].index)
        self.region_ids_with_NOT_all_zero_exp_veh = []
        for tg_number in _tg_n: # Taking key and values from dictionary.
            self.region_ids_with_NOT_all_zero_exp_veh.append(self.tg_num_2_region_id[tg_number])
        logger.info(f'The number of regions with NOT all zero in exp and veh in {self.color_list}: {len(self.region_ids_with_NOT_all_zero_exp_veh)}')



        #for _c in color_list_full:
        #    _df_exp_veh_color_all = _df_exp_veh[[c for c in _df_exp_veh.columns  if len(c.split("_")) == 3 and c.split("_")[2] == _c]]
        #    s = (_df_exp_veh_color_all != 0).all(axis=1)
        #    print(_c, s.sum())

    def get_exp_veh():
        return self.df_exp_veh

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


        

        if load_from_files:
            self.df_mean_cor_sag = pd.read_csv(filename)
            logger.info(f'loaded agg data: {filename}')
            return
        logger.info(f'creating agg data...')
        _df_total = self.df_total
        print(_df_total.index)
        print(_df_total.columns)
        print(_df_total)
        df_mean_cor_sag = _df_total.groupby(['sample_id', 'color','veh_exp'], as_index=False)[_df_total.columns[:-4]].agg('mean')
        df_mean_cor_sag.index.name = None
        df_mean_cor_sag.to_csv(filename, encoding='utf-8', index=None)
        logger.info(f'agg data saved into {filename}')

        self.df_mean_cor_sag = df_mean_cor_sag


    def get_raw_df(self, raw_file_name='df_raw.csv', load_from_files = False):

        if load_from_files:
            self.df_total = pd.read_csv(raw_file_name)
            self.df_total.set_index('Unnamed: 0',inplace=True)
            return
            
        df_total = pd.concat([self.df_exp.drop(['TG number','Region ID','Region name'] ,axis=1),self.df_veh.drop(['TG number','Region name'] ,axis=1)], axis=1)
        #df_total.set_index('TG number', inplace=True)
        df_total.set_index('Region ID', inplace=True)
        df_total = df_total.T
        df_total['sample_id'] = [a.split('_')[0] for a in df_total.index]
        df_total['veh_exp'] = [1 if a.split('_')[0] in self.subject_id_exp else 0 for a in df_total.index]
        df_total['cut_method'] = ['cor' if a.split('_')[1] == 'cor' else 'sag' for a in df_total.index]
        df_total['color'] =[ a.split('_')[2] for a in df_total.index]
        df_total.to_csv(raw_file_name)
        logger.info(f'Raw data saved into {raw_file_name}')

        self.df_total = df_total


    def _proprocess(self, _df):
        for prefix in self.prefix_to_remove_column:
            _df = _df.drop([a for a in _df.columns if a.startswith(prefix)], axis=1)
        #df_exp = df_exp.drop([a for a in df_exp.columns if a.endswith("fraction")], axis=1)
        _df.drop(_df[pd.isnull(_df['Region name'])].index, inplace=True)
        _df['Region ID'] = _df['Region ID'].astype(str)    
        #_df['Region ID'] = _df['Region ID'].str[:-2]
        _df['TG number'] = _df['TG number'].astype(int)
        for _c in _df.columns:
            if _c.endswith('SS/cfos fraction'):
                _df = _df.rename(columns={_c: _c.replace('SS/cfos fraction','SST/cfos fraction')})
                
        _df = _df.replace('#DIV/0!',0.0)
        _df = _df.fillna(0)
        for _c in _df.columns[3:]:
            _df[_c] = _df[_c].astype(float)
        return _df

    def get_id_mappings(self):
        self.tg_num_2_name = {}
        self.tg_num_2_region_id = {}
        self.region_id_2_name = {}
        self.region_id_2_tg_id = {}

        for _i, _row in self.df_exp[['TG number','Region ID','Region name']].iterrows():
            self.tg_num_2_name[_row['TG number']] = _row['Region name']
            self.tg_num_2_region_id[_row['TG number']] = _row['Region ID']

            self.region_id_2_name[_row['Region ID']] = _row['Region name']
            self.region_id_2_tg_id[_row['Region ID']] = _row['TG number']
        
    def gen_zero_value_heatmap_color(self, output_filename):
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
            for _color in self.color_list:
                for _cut in ['cor','sag']:

                    _df_exp_veh_color_cor = self.df_exp_veh[[c for c in self.df_exp_veh.columns if c.split("_")[0] in ids and c.split("_")[2] == _color and c.split("_")[1] == _cut]]
                    columns_new = [c.split("_")[0] + "_" + c.split("_")[2] for c in self.df_exp_veh.columns if c.split("_")[0] in ids and c.split("_")[2] == _color and c.split("_")[1] == _cut]
                    _df_exp_veh_color_cor.columns = columns_new
                    _df_exp_veh_color = _df_exp_veh_color_cor
                    s = (_df_exp_veh_color == 0).sum(axis=1)


                    #_df_exp_veh_color = _df_exp_veh[[c for c in _df_exp_veh.columns if c.split("_")[0] in ids and c.split("_")[2] == _color]]
                    #_df_exp_veh_color = _df_exp_veh[[c for c in _df_exp_veh.columns if c.endswith("_"+_color) and "_"+cut+"_" in c ]]

                    #s = (_df_exp_veh_color == 0).sum(axis=1)
                    valid_list.append(s)
            _columns2 = []
            for element in itertools.product(self.color_list, ['cor','sag']):
                _columns2.append(str(element[0])+"_"+element[1])

            df_non_zero_regions = pd.concat(valid_list, axis=1).reindex(valid_list[0].index)
            #df_non_zero_regions.index = valid_list[0].index
            #print(df_non_zero_regions)
            df_non_zero_regions.columns = _columns2
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
            ax.set_yticks([a+0.5 for a in list(range(len(_columns2))) ])
            ax.set_yticklabels(_columns2, fontsize=5)
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