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
from zipfile import ZipFile
import glob

UPLOAD_FOLDER = 'static/files_temp'
TRAINED_MODEL_FOLDER = 'static/trained_models'

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

ALLOWED_EXTENSIONS = set(['zip'])

fiberColors = [
  'red',
  'green',
  'blue',
  'yellow',
  'cyan',
  'magenta',
  'orange',
  'lime',
  'pink',
  'purple',
  'hotpink',
  'deepskyblue',
  'aqua',
  'teal',
  'gold',
  'salmon',
  'tomato',
  'skyblue',
  'indigo',
  'white'
];


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
        
    
        
        
        output_dir = UPLOAD_FOLDER+"/"+request.form.get('newDataName')+"/tiff"
        print(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        with ZipFile(filepath, 'r') as zip_obj:
            zip_obj.extractall(output_dir)
        
        
        msg = 'ok'
        response = {
            'message': msg,
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
        traind_models = []
        for f in os.listdir(TRAINED_MODEL_FOLDER):
            if os.path.isdir(TRAINED_MODEL_FOLDER+"/"+f):
                traind_models.append(f)

        output_dir = UPLOAD_FOLDER+"/"+request.form.get('dataname')+"/tiff"

        tiff_imgs = []
        tiff_filenames = []
        for f in os.listdir(output_dir):
            if f.endswith('.tif'):
                tiff_filenames.append(request.form.get('dataname')+"/tiff/"+f)
            '''
            img = Image.open(output_dir+"/"+f)
            byte_arr = io.BytesIO()
            img.save(byte_arr,  format='PNG')
            encoded_image = base64.b64encode(byte_arr.getvalue()).decode('ascii')
            tiff_imgs.append(encoded_image)
            '''
            
        response = {
            'tiff_filenames':tiff_filenames,
            'traind_models':traind_models
            
        }
        
        return jsonify(response)

@app.route('/removedata', methods=['POST'])
def removedata():
    print("removedata")

    removed_data = UPLOAD_FOLDER+"/"+request.form.get('dataname')

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
    print("projects",UPLOAD_FOLDER)
    _dirs = os.listdir(UPLOAD_FOLDER)
    _dirs = [f for f in _dirs if os.path.isdir(UPLOAD_FOLDER+"/"+f) == True]

    print(_dirs)
    response = {
        'dirs': _dirs,
    }
    
    return jsonify(response)




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
    _filename_sig_regions = f'{temp_dir}/heatmap_significant_regions_{_stat_test_name}.csv'

    txtfiles = []
    txtfiles.append(_filename_sig_regions)
    for file in glob.glob(f'{temp_dir}/heatmap*'):
        if f'_{params.heatpmap_vis_name()}_' in file and f'{params.stat_test_name()}' in file:
            txtfiles.append(file)
    memory_file = io.BytesIO()
    zip_file_name = f"files/{str(sta)}_{_stat_test_name}.zip"
    with zipfile.ZipFile(memory_file, 'w') as myzip:
    # Add files to the archive
        for t in txtfiles:
            myzip.write(t,arcname=t.replace(temp_dir,""))
    memory_file.seek(0)
    with open(zip_file_name, 'wb') as file:
        file.write(memory_file.read())
    memory_file.seek(0)
    eta = time.time() # 시간 측정
    print('zip:',int(eta-sta))
    hostname = request.headers.get('Host')
    print(zip_file_name)
    if zip_file_name:   
        #secure_filename = secure_filename(f'{str(sta)}_{output_dir}_{_filename_from_params}.zip')
        #uploads_dir = os.path.join(app.root_path, 'files')
        return send_file(memory_file,mimetype='application/zip',  download_name=f'{_stat_test_name}.zip',as_attachment=True)

        #return send_from_directory(uploads_dir, secure_filename, as_attachment=True)
    
def load_params(params):
    tickness =  params.form.get('tickness')
    projectname = params.form.get('projectname')
    spacing =  params.form.get('spacing')
    traindModel =  params.form.get('trainedModel')
    return projectname, tickness, spacing, traindModel

config_dir = '/home/jhahn/puzzlefusion-plusplus/config'


@app.route('/reconstruct', methods=['POST'])
def fold():
    #sema.acquire() # 세마포어 획득

    print('reconstruct')
    projectname, tickness, spacing, traindModel = load_params(request)
    print(projectname, tickness, spacing, traindModel)
    files_root =  UPLOAD_FOLDER+"/"+projectname
    data_ids = [projectname]
    ckpt_path= traindModel+'/denoiser/everyday_2000epoch/training/last.ckpt'



    #cfg = test_pipeline.load_cfg(config_dir)
    #tiff_dir_root, obj_dir_root, pc_dir_root, inference_dir_root, render_output_dir = test_pipeline.init_dir(files_root,data_ids)


    sta = time.time() # 시간 측정
    #obj_dir_list_relative = test_pipeline.tiff_2_obj(cfg, tiff_dir_root, tickness,spacing, obj_dir_root, pc_dir_root)
    eta = time.time() # 시간 측정
    time_tiff_2_obj = int(eta-sta) 
    print('tiff_2_obj:',time_tiff_2_obj," sec")

    obj_dir_list_relative = ['0.001_0.007']
    #obj_dir_list_relative
    obj_dir_root = f'{files_root}/objs'
    obj_files = []
    for _o in os.listdir(obj_dir_root+"/"+obj_dir_list_relative[0]+"/fractured_0"):
        obj_files.append(projectname+"/objs/"+obj_dir_list_relative[0]+"/fractured_0/"+_o)
    #slice_util.combine_obj_files(obj_files, obj_dir_root+"/"+obj_dir_list_relative[0]+"/combined.obj")
    obj_trans_dir_root = f'{files_root}/render/0/trans'
    obj_pred_files = []
    for _o in os.listdir(obj_trans_dir_root):
        obj_pred_files.append(projectname+"/trans/"+_o)


    obj_init_gt_files = []
    for _o in os.listdir(f'{files_root}/render/0/init_gt'):
        obj_init_gt_files.append(projectname+"/init_gt/"+_o)



    sta = time.time() # 시간 측정
    #test_pipeline.inference(cfg, pc_dir_root, obj_dir_list_relative, ckpt_path, inference_dir_root)
    eta = time.time() # 시간 측정
    time_inference = int(eta-sta) 
    print('inference:',time_inference," sec")

    sta = time.time() # 시간 측정
    #test_pipeline.render(inference_dir_root, obj_dir_root, render_output_dir)
    eta = time.time() # 시간 측정
    time_render = int(eta-sta) 
    print('render:',time_render," sec")

    sta = time.time() # 시간 측정
    shape_cd = [0.3725, 0.3275, 0.3040, 0.2622, 0.2249, 0.1924, 0.1631, 0.1410, 0.1116,
        0.0861, 0.0712, 0.0544, 0.0421, 0.0277, 0.0198, 0.0124, 0.0061, 0.0033]
    #shape_cd = test_pipeline.eval( vertices_gt,inference_dir_root,render_output_dir)    
    eta = time.time() # 시간 측정
    time_eval= int(eta-sta) 
    print('eval:',time_eval," sec")

    render_output_dir= files_root+'/render'
    df_original_pos = pd.read_csv(render_output_dir+"/0/BoundingBoxOfInputParts.csv")
    df_trasformation = pd.read_csv(render_output_dir+"/0/Transformation.csv")
    df_original_pos.set_index('part_index', inplace=True)
    df_trasformation.set_index('part_index', inplace=True)
    from ast import literal_eval

    df_total = pd.concat([df_original_pos,df_trasformation],axis=1)
    df_total.reset_index(inplace=True)
    df_total['chamfer_dist'] = shape_cd
    df_total['color'] = fiberColors[:len(df_total)]
    postProcessSummary = {
        'time_tiff_2_obj': f'{time_tiff_2_obj} sec.',
        'time_inference':f'{time_inference} sec.',
        'time_render':f'{time_render} sec.',
        'time_eval':f'{time_eval} sec.',
    }
    response = {
        #'df':df_sig_region_fold.to_dict(orient='records'),
        'time_tiff_2_obj':time_tiff_2_obj,
        'time_inference': time_inference,
        'time_render':time_render,
        'obj_files':obj_files,
        'obj_init_gt_files':obj_init_gt_files,
        'obj_pred_files':obj_pred_files,
        'postProcessSummary': postProcessSummary,
        'df_total':df_total.to_dict(orient='records'),
        #'elapsed_time': eta - sta
    }
    return jsonify(response)



from PIL import Image, ImageSequence
@app.route('/<projectname>/objs/<exp>/fractured_0/<filename>')
def serve_obj(projectname,exp,filename):
    return send_from_directory(f'{UPLOAD_FOLDER}/{projectname}/objs/{exp}/fractured_0', filename)

@app.route('/<projectname>/<filetype>/<filename>')
def serve_image(projectname,filetype,filename):

    if filetype == 'tiff':            
        png_dir = f'{UPLOAD_FOLDER}/{projectname}/png'
        os.makedirs(png_dir, exist_ok=True)
        
        tiff_filename = f'{UPLOAD_FOLDER}/{projectname}/{filetype}/{filename}'
        output_png_path = filename.replace('.tif','.png')

        if not os.path.exists(f'{png_dir}/{output_png_path}'):
            im = Image.open(tiff_filename)            
            if hasattr(im, 'n_frames') and im.n_frames > 1:
                for i, page in enumerate(ImageSequence.Iterator(im)):
                    output_png_path = f"output_page_{i}.png"
                    page.save(output_png_path)
                    print(f"Saved {output_png_path}")
            else:
                # If it's a single-page TIFF, directly save as PNG
                im.save(f'{png_dir}/{output_png_path}')
                print(f"Saved {output_png_path}")
            im.close()

        return send_from_directory(f'{png_dir}', output_png_path)
    elif filetype == 'video':
        return send_from_directory(f'{UPLOAD_FOLDER}/{projectname}/render/0/', filename)
    elif filetype == 'trans' or filetype == 'init_gt':
        return send_from_directory(f'{UPLOAD_FOLDER}/{projectname}/render/0/{filetype}', filename)
    
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

if __name__ == '__main__':
    app.run(host='localhost',threaded=True)