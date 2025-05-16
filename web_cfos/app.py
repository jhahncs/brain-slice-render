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

from  cfos_util import Cfos

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

ALLOWED_EXTENSIONS = set(['xlsx'])




def allowed_file(filename): # filename을 보고 지원하는 media type인지 판별
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/newdata', methods=['POST'])
def newdata():
    sta = time.time() # 시간 측정
    #sema.acquire() # 세마포어 획득


    
    print("============================================")
    '''
    if not session.get("username"):
        client_port = request.environ.get('REMOTE_PORT')
        user_agent = request.headers.get('User-Agent')
        session['username'] = str(request.remote_addr) + ":" + str(user_agent)
        print('new user session',session['username'])
    else:
        print("LOGGEDIN")
    print(session.items())
    '''
    

    #time.sleep(10)   

    try:
        if 'file' not in request.files:
            return {'message': '파일을 선택해주세요.'}, 400

        file = request.files['file']
        if file.filename == '':
            return {'message': '파일을 선택해주세요.'}, 400

        if not file or not allowed_file(file.filename.lower()):
            return {'message': '파일을 선택해주세요.'}, 400
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        

        
                
        output_dir = DATA_FOLDER+"/"+request.form.get('newDataName')
        print(filepath)
        print(output_dir)
        cfos = Cfos(filename = filepath, output_dir = output_dir, load_from_files = False)
        df_fold = cal_fold(cfos, cfos.df_mean_cor_sag,output_dir+"/fold.csv")
        filename_pvalue_permutation_test = output_dir+"/pvalue_permutation_test.csv"
        filename_pvalue_ttest = output_dir+"/pvalue_ttest.csv"
        filename_pvalue_permutation_test_fdr = output_dir+"/pvalue_permutation_test_fdr.csv"
        filename_pvalue_ttest_fdr = output_dir+"/pvalue_ttest_fdr.csv"

        df_pvalue_permutation_test = cal_pvalue(cfos,cfos.df_mean_cor_sag, 'permutation_test',filename_pvalue_permutation_test)
        df_fdr_permutation_test = cal_fdr(cfos, df_pvalue_permutation_test, _alpha = 0.05, result_filename=filename_pvalue_permutation_test_fdr)
        df_pvalue_permutation_test = cal_pvalue(cfos,cfos.df_mean_cor_sag, 't_test',filename_pvalue_ttest)
        df_fdr_t_test = cal_fdr(cfos, df_pvalue_permutation_test, _alpha = 0.05, result_filename=filename_pvalue_ttest_fdr)

        #cfos = str(sta)
        #session['cfos_obj'] = cfos

        '''
        img = Image.open('files/heatmap_cfos total.png')
        byte_arr = io.BytesIO()
        img.save(byte_arr,  format='PNG')


        encoded_image = base64.b64encode(byte_arr.getvalue()).decode('ascii')
    
        response = {
            'message': 'Some text data',
            'image': encoded_image
        }
        '''
        response = {
            #'message': cfos.preprocess_summary(),
            'message': output_dir,
        }
        #sema.release() # 세마포어 릴리즈
        return jsonify(response)

        

        return jsonify({'message': '파일이 업로드되었습니다.', 'filename': filepath, 'image_path':'files/heatmap_cfos total.png'}), 200

    except Exception as e:
        print(e)
        return {'message': e}, 500


        if request.method == 'POST':
            file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filename = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filename)
        
        
        import cfos_util
        importlib.reload(cfos_util)

        import cfos_stat
        importlib.reload(cfos_stat)


        cfos = cfos_util.Cfos(filename,'output')

        df_pvalue_permutation_test = cfos_stat.cal_pvalue(cfos.df_mean_cor_sag, 'permutation_test',cfos.region_id_2_tg_id, cfos.region_id_2_name,'output/pvalue_permutation_test.csv')
        df_pvalue_ttest = cfos_stat.cal_pvalue(cfos.df_mean_cor_sag, 't_test',cfos.region_id_2_tg_id, cfos.region_id_2_name,'output/pvalue_ttest.csv')


        df_fdr_permutation_test = cfos_stat.cal_fdr(df_pvalue_permutation_test, cfos.region_id_2_tg_id, cfos.region_id_2_name, _alpha = 0.05, result_filename='output/pvalue_permutation_test_fdr.csv')
        df_fdr_t_test = cfos_stat.cal_fdr(df_pvalue_ttest, cfos.region_id_2_tg_id, cfos.region_id_2_name, _alpha = 0.05, result_filename='output/pvalue_ttest_fdr.csv')


        #cfos.gen_zero_value_heatmap_color(f'output/regions_with_zero_values.pdf')
        return render_template('gemma.html')#, answer = response)

@app.route('/load', methods=['POST'])
def load():
    print('load')
    if request.method == 'POST':
        

        output_dir = DATA_FOLDER+"/"+request.form.get('dataname')

        cfos = Cfos(filename = None,output_dir = output_dir, load_from_files=True)
        
        response = {
            'message': cfos.preprocess_summary(),
            
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

@app.route('/analysis', methods=['POST'])
def analysis():
    sta = time.time() # 시간 측정
    #sema.acquire() # 세마포어 획득

    print('analysis')
    pvalue_th = float(request.form.get('pvalue'))
    fold_up = float(request.form.get('fold_up'))
    fold_down = float(request.form.get('fold_down'))
    output_dir = request.form.get('dataname')
    analysisMode = request.form.get('analysisMode')
    print(pvalue_th,fold_up,fold_down,output_dir)

    filename_pvalue_permutation_test = DATA_FOLDER+"/"+output_dir+"/pvalue_permutation_test.csv"
    filename_pvalue_ttest = DATA_FOLDER+"/"+output_dir+"/pvalue_ttest.csv"
    filename_pvalue_permutation_test_fdr = DATA_FOLDER+"/"+output_dir+"/pvalue_permutation_test_fdr.csv"
    filename_pvalue_ttest_fdr = DATA_FOLDER+"/"+output_dir+"/pvalue_ttest_fdr.csv"
    
    cfos = Cfos(None, DATA_FOLDER+"/"+output_dir, load_from_files=True)
    df_fold = cal_fold(cfos, cfos.df_mean_cor_sag,DATA_FOLDER+"/"+output_dir+"/fold.csv")

    df_pvalue_permutation_test = cal_pvalue(cfos,cfos.df_mean_cor_sag, 'permutation_test',filename_pvalue_permutation_test)
    df_fdr_permutation_test = cal_fdr(cfos, df_pvalue_permutation_test, _alpha = 0.05, result_filename=filename_pvalue_permutation_test_fdr)
    df_pvalue_permutation_test = cal_pvalue(cfos,cfos.df_mean_cor_sag, 't_test',filename_pvalue_ttest)
    df_fdr_t_test = cal_fdr(cfos, df_pvalue_permutation_test, _alpha = 0.05, result_filename=filename_pvalue_ttest_fdr)


    color_2_dict_up, color_2_dict_down, df_sig_region_fold= build_dict(cfos, df_fold, df_fdr_permutation_test, pvalue_th,fold_up,fold_down)
    df_sig_region_fold.to_csv(DATA_FOLDER+"/"+output_dir+"/heatmap_significant_regions.csv",index=None)

    if analysisMode == 'both':

        color_list = list([c for c in df_fold.columns if c not in ['Region ID','TG number','Region Name']])
        color_list = color_list[:1]
        gen_brain_heatmap(DATA_FOLDER, color_list, df_fdr_permutation_test, pvalue_th, fold_up, fold_down,color_2_dict_up,color_2_dict_down)
    

    output_img_filename = f'files/heatmap_cfos_total.png'
    #print('beging')
    #gen_brain_heatmap(DATA_FOLDER+"/"+output_dir, color_list, df_fdr_permutation_test, pvalue_th, fold_up, fold_down,color_2_dict_up,color_2_dict_down)
    #print('end')
    #img = Image.open(output_img_filename)
    #byte_arr = io.BytesIO()
    #img.save(byte_arr,  format='PNG')
    txtfiles = []
    for file in glob.glob(DATA_FOLDER+"/"+output_dir+"/heatmap*"):
        txtfiles.append(file)
    memory_file = io.BytesIO()
    zip_file_name = f"files/{str(sta)}.zip"
    with zipfile.ZipFile(memory_file, 'w') as myzip:
    # Add files to the archive
        for t in txtfiles:
            myzip.write(t,arcname=t.replace(DATA_FOLDER+"/"+output_dir,""))
    memory_file.seek(0)
    with open(zip_file_name, 'wb') as file:
        file.write(memory_file.read())
    memory_file.seek(0)
    #response = make_response(memory_file.read())
    #response.headers.set('Content-Type', 'application/zip')
    #response.headers.set('Content-Disposition', 'attachment', filename='example.zip')

    #return response
    #return send_file(memory_file, download_name='result.zip', as_attachment=True)
    hostname = request.headers.get('Host')
    #port = request.headers.get('Port')
    #encoded_image = base64.b64encode(byte_arr.getvalue()).decode('ascii')
    eta = time.time() # 시간 측정
    response = {
        'message': f'{pvalue_th} {fold_up} {fold_down}',
        #'df':df_sig_region_fold.to_dict(orient='records'),
        'zip':f'http://{hostname}/download/{str(sta)}.zip',
    #    'image': encoded_image,
        'elapsed_time': eta - sta
    }
    
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