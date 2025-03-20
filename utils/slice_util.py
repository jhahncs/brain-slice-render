import numpy as np
import os
from scipy.spatial.transform import Rotation as R

import random

import time
import itertools


def combine_obj_files(_dir_list, output_dir):
    _obj_list = []
    for _dir in _dir_list:
        files = [_dir+"/"+f for f in os.listdir(_dir) if os.path.isfile(_dir+"/"+f)]
        files.sort(key=lambda x: int(x.split("/")[-1].split("_")[-1].replace(".obj",'')), reverse=False)
        
        _pc_list = []
        f_2_last = []
        with open(output_dir+"/"+_dir.split("/")[-1]+".obj", 'w') as outfile:

            f_2_last.append(0)
            for _,fname in enumerate(files):
                
                _c = 0
                with open(fname) as infile:
                    if fname.endswith('piece.obj'):
                        continue
                    print(fname)
                    _pcs = []
                    for line in infile:
                        if line.lower().startswith('v'):
                            _c += 1
                            _arr = line[2:].split()
                            _arr = np.array([float(a) for a in _arr])                    
                            _pcs.append(_arr)
                    
                    _pcs = np.array(_pcs)
                    #_pcs = np.array(_pcs)
                    #_pcs = trans_pc(_pcs)
                    #_pcs = rotate_pc(_pcs)
                    print(_pcs.shape)                                
                    _pc_list.append(_pcs)
                    
                    for _arr in _pcs:
                        outfile.write(f'v {_arr[0]} {_arr[1]} {_arr[2]}\n')

                f_2_last.append(_c)

            _delta = 0
            for fi, fname in enumerate(files):
                _delta += f_2_last[fi]
                with open(fname) as infile:
                    if fname.endswith('piece.obj'):
                        continue                
                    for line in infile:
                        if line.lower().startswith('f'):
                            _arr = line[2:].split()
                            outfile.write(f'f {int(_arr[0])+_delta} {int(_arr[1])+_delta} {int(_arr[2])+_delta}\n')
        _obj_list.append(_pc_list)
    return _obj_list

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
