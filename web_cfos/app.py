from flask import Flask, jsonify, session, send_file, make_response, send_from_directory
from flask import Flask, render_template
from flask import request
import os
from flask import url_for, render_template, send_file
import json
from werkzeug.utils import secure_filename
from flask_cors import CORS
# some_file.py
from PIL import Image
import pandas as pd
import io
import threading
import time
import base64
import importlib
#from flask_session import Session
from flask_session import Session
import sys
from datetime import timedelta
import shutil
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../cfos')
import zipfile
import glob
UPLOAD_FOLDER = 'files'
DATA_FOLDER = 'projects'

app = Flask(__name__)
CORS(app)

from  cfos_util import Cfos, Cfos_params, sanitize_folder_name

from cfos_stat import cal_fold, cal_pvalue, cal_fdr
from cfos_brainheatmap import build_dict, gen_brain_heatmap

#server_session.config["SESSION_PERMANENT"] = False     # Sessions expire when the browser is closed
#server_session.config["SESSION_TYPE"] = "filesystem"     # Store session data in files
#server_session.secret_key = "asdfawerf32fwfwf"

#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)

app.config["SESSION_PERMANENT"] = True      # Sessions expire when the browser is closed
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1) # Example: Session lasts for 7 days
#app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_sessions') # Ensure this directory exists

app.config["SESSION_TYPE"] = "filesystem"     # Store session data in files
app.secret_key = "asdfawerf32fwfwf"
# Initialize Flask-Session
#Session(app)
Session(app)



import shutil
#try:
#    shutil.rmtree(output_dir)
#except:
#    pass

#sema = threading.Semaphore(1)

if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
if not os.path.exists(DATA_FOLDER):
    os.mkdir(DATA_FOLDER)

ALLOWED_EXTENSIONS = set(['xlsx'])




def allowed_file(filename): # filename을 보고 지원하는 media type인지 판별
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/newdata', methods=['POST'])
def newdata():
    sta = time.time() # 시간 측정
    #sema.acquire() # 세마포어 획득


    
    print("newdata")


    try:
        if 'file' not in request.files:
            return {'message': 'Please choose a file'}, 400

        file = request.files['file']
        if file.filename == '':
            return {'message': 'Please choose a file'}, 400

        if not file or not allowed_file(file.filename.lower()):
            return {'message': 'Please choose a file.'}, 400
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
    
        
                
        output_dir = DATA_FOLDER+"/"+request.form.get('newDataName')

        print(output_dir)
        cfos = Cfos(filename = filepath, output_dir = output_dir, load_from_files = False)
        ValidationReport = cfos.validation_report()
        msg =''
        if ValidationReport['TG number consistent check'] == 'Valid':
            msg = 'Successfully uploaded'
        else:
            msg = 'invalid format!'
        
        response = {
            'message': msg,
            'ValidationReport':ValidationReport
        }
        #sema.release() # 세마포어 릴리즈
        return jsonify(response)

    
    except Exception as e:
        print(e)
        return {'message': e}, 500




@app.route('/load', methods=['POST'])
def load():
    print('load')
    if request.method == 'POST':
        

        output_dir = DATA_FOLDER+"/"+request.form.get('dataname')

        cfos = Cfos(filename = None,output_dir = output_dir, load_from_files=True)
        filename = f'{output_dir}/regions_with_zero_values.png'
        if not os.path.exists(filename):
            cfos.gen_zero_value_heatmap_color(filename)

        img = Image.open(filename)
        byte_arr = io.BytesIO()
        img.save(byte_arr,  format='PNG')
        encoded_image = base64.b64encode(byte_arr.getvalue()).decode('ascii')
        group_name_dict = []
        for g in cfos.group_names:
            _ro = {}
            _ro['label'] = g
            _ro['value'] = g
            group_name_dict.append(_ro)
        response = {
            'message': cfos.preprocess_summary(),
            'image':encoded_image,
            'group_names':cfos.group_names,
            'color_names':cfos.color_list_full,

            
        }
        
        return jsonify(response)

@app.route('/removedata', methods=['POST'])
def removedata():
    print("removedata")

    removed_data = DATA_FOLDER+"/"+request.form.get('dataname')

    print(removed_data)
    #os.removedirs(removed_data)
    try:
        shutil.rmtree(removed_data)
    except:
        pass
    response = {
        'message': removed_data,
    }
    
    return jsonify(response)

@app.route('/projects', methods=['GET','POST'])
def projects():
    print("projects")
    _dirs = os.listdir('projects')
    print(_dirs)
    response = {
        'dirs': _dirs,
    }
    
    return jsonify(response)



def load_object(params: Cfos_params):

    cfos = Cfos(None, DATA_FOLDER+"/"+params.dataname, load_from_files=True)
    cfos.build_group1_and_group2(params.group1_name, params.group2_name, load_from_files = True)
    stat_name = params.stat_test_name()
    filename_fold= f'{DATA_FOLDER}/{params.dataname}/{stat_name}/fold.csv'

    df_fold = cal_fold(cfos, cfos.df_by_two_group_and_color, params.group1_name, params.group2_name, filename_fold)
    
    filename_pairwiseCompare= f'{DATA_FOLDER}/{params.dataname}/{stat_name}/pairwise_{params.pairwiseCompareMethod}.csv'

    df_pairwise_test = cal_pvalue(cfos,cfos.df_by_two_group_and_color, params.pairwiseCompareMethod,filename_pairwiseCompare, sigle_core_mode = False, test_mode = False)

    df_multiple_correction = None
    if params.multipleCompareCorrectionMethod != 'None':
        filename_multiplecorrection = f'{DATA_FOLDER}/{params.dataname}/{stat_name}/multiplecorrection_{params.multipleCompareCorrectionMethod}.csv'
        df_multiple_correction = cal_fdr(cfos, df_pairwise_test, _alpha = params.fdr_alpha, result_filename=filename_multiplecorrection)

        return cfos, df_fold, df_multiple_correction
    else:
        return cfos, df_fold, df_pairwise_test
#df_sig_region_fold = None
@app.route('/downloadall', methods=['POST'])
def downloadall():
    print('downloadall')

    
    params = Cfos_params(request)

    print(params)

    _stat_test_name = params.stat_test_name()
    temp_dir = DATA_FOLDER+"/"+params.dataname+"/"+_stat_test_name
    heatmap_files = []
    for file in glob.glob(f'{temp_dir}/heatmap*'):
        if f'_{params.heatpmap_vis_name()}_' in file and f'{params.stat_test_name()}' in file and '.png' in file:
            heatmap_files.append(file)

    output_img_filename = f'{temp_dir}/heatmap_{params.heatpmap_vis_name()}_{sanitize_folder_name(params.color)}_{_stat_test_name}.png'
    print(output_img_filename)
    if len(heatmap_files) == 0:

        sta = time.time() # 시간 측정
        cfos, df_fold, df_stat_test = load_object(params)
        eta = time.time() # 시간 측정
        print('loading: ',int(eta-sta))


        with open(f'{temp_dir}/color_2_dict_up_{_stat_test_name}.json', 'r') as f:
            color_2_dict_up = json.load(f)
        with open(f'{temp_dir}/color_2_dict_down_{_stat_test_name}.json', 'r') as f:
            color_2_dict_down = json.load(f)
        #color_list = color_list[:1]

        #color_list = color_list[:1]

        #color_list = [color]
        sta = time.time() # 시간 측정
       
        gen_brain_heatmap(cfos, temp_dir, df_stat_test, cfos.color_list_full, color_2_dict_up,color_2_dict_down, params, single_core_mode = False)

        eta = time.time() # 시간 측정
        print('gen_brain_heatmap: ',int(eta-sta))
   






    sta = time.time() # 시간 측정
    zip_file_name = f"files/{str(sta)}_{_stat_test_name}.zip"



    # 메모리 버퍼를 사용하여 압축 파일 생성
    memory_file = io.BytesIO()

    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as myzip:
        # 1. 기존에 압축하려던 파일들을 추가
        '''
        files_to_zip = []
        _filename_sig_regions = os.path.join(temp_dir, f'heatmap_significant_regions_{_stat_test_name}.csv')
        files_to_zip.append(_filename_sig_regions)
        for file in glob.glob(f'{temp_dir}/heatmap*'):
            if f'_{params.heatpmap_vis_name()}_' in file and f'{params.stat_test_name()}' in file:
                files_to_zip.append(file)
                
        for file_path in files_to_zip:
            if os.path.exists(file_path):
                arcname = os.path.relpath(file_path, temp_dir)
                myzip.write(file_path, arcname=arcname)
        '''
        # 2. temp_dir 내 모든 하위 폴더와 파일들을 재귀적으로 추가
        for dirpath, dirnames, filenames in os.walk(temp_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                # 기존에 추가한 파일은 건너뛰기
                if 'color_2_dict_' in file_path:
                    continue
                #if file_path not in files_to_zip:
                arcname = os.path.relpath(file_path, temp_dir)
                myzip.write(file_path, arcname=arcname)

    memory_file.seek(0)

    # ZIP 파일을 실제 디스크에 저장
    with open(zip_file_name, 'wb') as file:
        file.write(memory_file.read())

    #memory_file.close()


    '''
    _filename_sig_regions = f'{temp_dir}/heatmap_significant_regions_{_stat_test_name}.csv'

    txtfiles = []
    txtfiles.append(_filename_sig_regions)
    for file in glob.glob(f'{temp_dir}/heatmap*'):
        if f'_{params.heatpmap_vis_name()}_' in file and f'{params.stat_test_name()}' in file:
            txtfiles.append(file)

    memory_file = io.BytesIO()
    
    for file_path in txtfiles:
        if os.path.exists(file_path):
            arcname = os.path.relpath(file_path, temp_dir)
            myzip.write(file_path, arcname=arcname)
    
    # 2. temp_dir 내 모든 하위 폴더와 파일들을 재귀적으로 추가
    for dirpath, dirnames, filenames in os.walk(temp_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            # 기존에 추가한 파일은 건너뛰기
            if file_path not in txtfiles:
                arcname = os.path.relpath(file_path, temp_dir)
                myzip.write(file_path, arcname=arcname)

    with zipfile.ZipFile(memory_file, 'w') as myzip:
    # Add files to the archive
        for file_path in txtfiles:
            #myzip.write(t,arcname=t.replace(temp_dir,""))

            if os.path.exists(file_path):
                # ZIP 파일 내부에 저장될 경로를 'temp_dir' 기준으로 상대 경로로 설정합니다.
                # 이렇게 하면 'temp_dir/slices/file.txt'는 'slices/file.txt'로 저장됩니다.
                arcname = os.path.relpath(file_path, temp_dir)
                myzip.write(file_path, arcname=arcname)
            else:
                print(f"경고: 파일을 찾을 수 없어 압축에서 제외되었습니다: {file_path}")


    memory_file.seek(0)
    
    with open(zip_file_name, 'wb') as file:
        file.write(memory_file.read())
    '''
    
    memory_file.seek(0)
    
    hostname = request.headers.get('Host')
    print(zip_file_name)

    

    if zip_file_name:   
        #secure_filename = secure_filename(f'{str(sta)}_{output_dir}_{_filename_from_params}.zip')
        #uploads_dir = os.path.join(app.root_path, 'files')
        return send_file(memory_file,mimetype='application/zip',  download_name=f'{_stat_test_name}.zip',as_attachment=True)

        #return send_from_directory(uploads_dir, secure_filename, as_attachment=True)
    
@app.route('/fold', methods=['POST'])
def fold():
    #sema.acquire() # 세마포어 획득

    print('fold')
    params = Cfos_params(request)


    print(params)
    _filename_from_params = params.stat_test_name()
    temp_dir = DATA_FOLDER+"/"+params.dataname+"/"+_filename_from_params
    _filename_sig_regions = f'{temp_dir}/heatmap_significant_regions_{_filename_from_params}.csv'
    print(_filename_sig_regions)
    if not os.path.exists(_filename_sig_regions):

        os.makedirs(temp_dir, exist_ok=True)
        sta = time.time() # 시간 측정
        cfos, df_fold, df_stat_test = load_object(params)
        eta = time.time() # 시간 측정
        print('loading:',int(eta-sta)," sec")
        print(df_fold.index)

        sta = time.time() # 시간 측정
        color_2_dict_up, color_2_dict_down, df_sig_region_fold= build_dict(cfos, df_fold, df_stat_test, params)

        df_sig_region_fold.to_csv(_filename_sig_regions,index=None)
        eta = time.time() # 시간 측정
        print('build_dict:',int(eta-sta)," sec")

        #color_list = color_list[:1]
        
        with open(f'{temp_dir}/color_2_dict_up_{_filename_from_params}.json', 'w') as f:
            json.dump(color_2_dict_up, f)
        with open(f'{temp_dir}/color_2_dict_down_{_filename_from_params}.json', 'w') as f:
            json.dump(color_2_dict_down, f)
        
   
    

    filename_df_regions_zero = f'{DATA_FOLDER}/{params.dataname}/df_{params.group1_name}_{params.group2_name}_zero_regions.csv'
    try:
        df_zero_regions = pd.read_csv(filename_df_regions_zero)
    except:
        df_zero_regions = []
        pass
    with open(f'{temp_dir}/color_2_dict_up_{_filename_from_params}.json', 'r') as f:
        color_2_dict_up = json.load(f)
    with open(f'{temp_dir}/color_2_dict_down_{_filename_from_params}.json', 'r') as f:
        color_2_dict_down = json.load(f)



    color_2_updown = {}
    for k in color_2_dict_up:
        color_2_updown[k] = {}
        color_2_updown[k]['up'] = len(color_2_dict_up[k])
        color_2_updown[k]['down'] = len(color_2_dict_down[k])
    

    response = {
        #'df':df_sig_region_fold.to_dict(orient='records'),
        'freq':color_2_updown,
        'region_ids_with_all_zero': len(df_zero_regions)
        #'elapsed_time': eta - sta
    }
    return jsonify(response)


    
@app.route('/brainheatmap', methods=['POST'])
def brainheatmap():
    #sema.acquire() # 세마포어 획득

    print('brainheatmap')

    params = Cfos_params(request)

    print(params)

    _stat_test_name = params.stat_test_name()
    temp_dir = DATA_FOLDER+"/"+params.dataname+"/"+_stat_test_name
    _filename_sig_regions = f'{temp_dir}/heatmap_significant_regions_{_stat_test_name}.csv'

    print(_filename_sig_regions)
    #if not os.path.exists(temp_dir):
    os.makedirs(temp_dir, exist_ok=True)
    heatmap_files = glob.glob(temp_dir+"/heatmap*.png")


    sta = time.time() # 시간 측정
    #color_2_dict_up, color_2_dict_down, df_sig_region_fold= build_dict(cfos, df_fold, df_fdr_permutation_test, pvalue_th,fold_up,fold_down)
    #df_sig_region_fold.to_csv(f'{temp_dir}/heatmap_significant_regions_{_filename_from_params}.csv',index=None)

    
    df_sig_region_fold = pd.read_csv(_filename_sig_regions)
    with open(f'{temp_dir}/color_2_dict_up_{_stat_test_name}.json', 'r') as f:
        color_2_dict_up = json.load(f)
    with open(f'{temp_dir}/color_2_dict_down_{_stat_test_name}.json', 'r') as f:
        color_2_dict_down = json.load(f)

    eta = time.time() # 시간 측정
    print('build_dict: ',int(eta-sta))

    output_img_filename = f'{temp_dir}/one_heatmap_{params.heatpmap_vis_name()}_{sanitize_folder_name(params.color)}_{_stat_test_name}.png'
    print(output_img_filename)
    if not os.path.exists(output_img_filename):

        sta = time.time() # 시간 측정
        cfos, df_fold, df_stat_test = load_object(params)
        eta = time.time() # 시간 측정
        print('loading: ',int(eta-sta))


    


        #color_list = [color]
        sta = time.time() # 시간 측정
        #os.makedirs(temp_dir + "/slices", exist_ok=True)
        gen_brain_heatmap(cfos, temp_dir ,  df_stat_test, cfos.color_list_full, color_2_dict_up,color_2_dict_down, params, single_core_mode = False)

        eta = time.time() # 시간 측정
        print('gen_brain_heatmap: ',int(eta-sta))
   




    
    #heatmap_{color_code.replace("/","_")}.png
    df_sig_region_fold = df_sig_region_fold.query(f'color=="{params.color}"')

    #print('beging')
    #gen_brain_heatmap(DATA_FOLDER+"/"+output_dir, color_list, df_fdr_permutation_test, pvalue_th, fold_up, fold_down,color_2_dict_up,color_2_dict_down)
    #print('end')
    sta = time.time() # 시간 측정
    
    img = Image.open(output_img_filename)
    byte_arr = io.BytesIO()
    img.save(byte_arr,  format='PNG')
    encoded_image = base64.b64encode(byte_arr.getvalue()).decode('ascii')
    
    response = {
        'message': f'{params.pvalue_th} {params.fold_up} {params.fold_down}',
        'image': encoded_image,
        
        'df':df_sig_region_fold.to_dict(orient='records'),
        #'elapsed_time': eta - sta
    }
    eta = time.time() # 시간 측정
    print('image to byte: ',int(eta-sta))
    return jsonify(response)

@app.route("/download/<path:filename>")
def download_test(filename):
	#return send_file("files/test.text", mimetype="text/plain", as_attachment=True)
    filepath = os.path.join('files', filename)

    # Check if the file exists
    if os.path.isfile(filepath):
        return send_from_directory('files', filename, as_attachment=True)
    else:
        return "File not found", 404
@app.route('/get_image', methods=['GET'])
def get_image():
    
    img = Image.open('files/heatmap_cfos total.png')
    img_io = io.BytesIO()
    img.save(img_io, 'PNG', quality=70)
    img_io.seek(0)
    #return send_file(img_io, mimetype='image/jpeg')
    print(img_io)
    try:

        return jsonify({'image_data': img_io.decode('utf-8')})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/')
def index():

    
    return render_template('index.html')
    
if __name__ == '__main__':
    app.run(host='localhost',threaded=True)