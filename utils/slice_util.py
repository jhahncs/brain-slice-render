import numpy as np
import os
from scipy.spatial.transform import Rotation as R

import random

import time
import itertools

def _read_and_write_v(files, prefix, outfile):

    #_v_list = []
    f_2_last = []
    
    for _,fname in enumerate(files):
        
        _c = 0

        with open(fname) as infile:
            if fname.endswith('piece.obj'):
                continue
            print(fname)
            _v = []
            for line in infile:
                if line.lower().startswith(f'{prefix} '):
                    _c += 1
                    _arr = line[2:].split()
                    _arr = np.array([float(a) for a in _arr])                    
                    _v.append(_arr)
            
            _v = np.array(_v)
            #_pcs = np.array(_pcs)
            #_pcs = trans_pc(_pcs)
            #_pcs = rotate_pc(_pcs)
            print(_v.shape)                                
            #_v_list.append(_v)
            
            for _arr in _v:
                #output_lines +=  f'v {_arr[0]} {_arr[1]} {_arr[2]}\n'
                outfile.write(f'{prefix} {_arr[0]} {_arr[1]} {_arr[2]}\n')
        f_2_last.append(_c)

    return f_2_last


def combine_obj_file_list(_file_list, output_obj_filename):


    _vn_list = []
    f_2_last = []

    #with open(output_dir+"/"+_dir.split("/")[-1]+".obj", 'w') as outfile:
    with open(output_obj_filename, 'w') as outfile:

        f_2_last.append(0)

        _f_2_last = _read_and_write_v(_file_list, "v", outfile)
        f_2_last.extend(_f_2_last)
        

        _read_and_write_v(_file_list, "vn", outfile)

        _delta = 0
        for fi, fname in enumerate(_file_list):
            _delta += f_2_last[fi]
            with open(fname) as infile:
                if fname.endswith('piece.obj'):
                    continue                
                for line in infile:
                    if line.lower().startswith('f'):
                        _arr = line[2:].split()
                        outfile.write(f'f {int(_arr[0])+_delta} {int(_arr[1])+_delta} {int(_arr[2])+_delta}\n')



def combine_obj_files(_dir_list, output_dir):

    for _dir in _dir_list:
        files = [_dir+"/"+f for f in os.listdir(_dir) if os.path.isfile(_dir+"/"+f)]
        files.sort(key=lambda x: int(x.split("/")[-1].split("_")[-1].replace(".obj",'')), reverse=True)
        
        combine_obj_file_list(files, output_dir+"/"+_dir.split("/")[-1]+".obj")

'''
# very slow
def pcs_matched(pc_1, pc_2, point_dist_threshold = 0.03, matched_threshold = 0.5):
    _matched = 0
    #_bottom_flag = torch.zeros(len(pc_2), dtype=torch.bool)
    _b_idx_last = 0
    for _t in pc_1:
        for _b_idx in range(_b_idx_last, len(pc_2)):
            _dist = torch.cdist(_t.unsqueeze(dim=0), pc_2[_b_idx].unsqueeze(dim=0))[0][0]
            #print(_dist)
            if torch.lt(_dist, point_dist_threshold):
                #_bottom_flag[_b_idx] = True
                _matched += 1
                _b_idx_last = _b_idx
                break

    if _matched >= len(pc_1)*matched_threshold:
        return True, _matched
    else:
        return False, _matched
'''
