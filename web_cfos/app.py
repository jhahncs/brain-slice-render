from flask import Flask, jsonify, session
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

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../cfos')

UPLOAD_FOLDER = 'files'
app = Flask(__name__)
CORS(app)



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

import cfos_util
importlib.reload(cfos_util)

import cfos_stat
importlib.reload(cfos_stat)


def allowed_file(filename): # filename을 보고 지원하는 media type인지 판별
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    sta = time.time() # 시간 측정
    #sema.acquire() # 세마포어 획득


    
    print(session.items())
    if not session.get("username"):
        client_port = request.environ.get('REMOTE_PORT')
        user_agent = request.headers.get('User-Agent')
        session['username'] = str(request.remote_addr) + ":" + str(user_agent)
        print('new user session',session['username'])
    else:
        print("LOGGEDIN")
    print(session.items())

    time.sleep(10)   



    if 'image' not in request.files:
        return {'message': '파일을 선택해주세요.'}, 400

    file = request.files['image']
    if file.filename == '':
        return {'message': '파일을 선택해주세요.'}, 400

    if file and allowed_file(file.filename.lower()):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        

        if not session.get("cfos_obj"):
            print(filepath)
            #cfos = cfos_util.Cfos(filepath,'output')
            cfos = str(sta)
            session['cfos_obj'] = cfos
            print("cfos object created",cfos)
        else:
            
            cfos = session['cfos_obj']
            print("cfos object exists",cfos)
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
            'message': cfos,
        }
        print("done")
        #sema.release() # 세마포어 릴리즈
        return jsonify(response)

        

        return jsonify({'message': '파일이 업로드되었습니다.', 'filename': filepath, 'image_path':'files/heatmap_cfos total.png'}), 200
    else:
        return {'message': '업로드에 실패했습니다.'}, 500



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
        
        data = request.json
        dirname = data['dirname']
        cfos = cfos_util.Cfos(None, "projects/"+dirname, load_from_files=True)
        
        response = {
            'message': cfos.preprocess_summary(),
            
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

    print('analysis',session['username'])
    pvalue = request.form['pvalue']
    fold_up = request.form['fold_up']
    fold_down = request.form['fold_down']
    dirname = request.form['dir']
    print(pvalue,fold_up,fold_down,dirname)
    cfos = cfos_util.Cfos(None, "projects/"+dirname, load_from_files=True)
    if not session.get("username"):
        response.data = json.dumps({
            "code": "no file",
        })
        response.content_type = "application/json"
        return response

    

    
    output_img_filename = f'files/heatmap_cfos_total.png'
    print('beging')
    #cfos.gen_zero_value_heatmap_color(output_img_filename)
    print('end')
    img = Image.open(output_img_filename)
    byte_arr = io.BytesIO()
    img.save(byte_arr,  format='PNG')


    encoded_image = base64.b64encode(byte_arr.getvalue()).decode('ascii')
    eta = time.time() # 시간 측정
    response = {
        'message': f'{pvalue} {fold_up} {fold_down}',
        'image': encoded_image,
        'elapsed_time': eta - sta
    }
    
    return jsonify(response)
    
        
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