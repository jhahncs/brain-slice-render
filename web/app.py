from flask import Flask, jsonify
from flask import Flask, render_template
from flask import request
import os
from flask import url_for, render_template
import json

app = Flask(__name__)


@app.route('/gemma')
def gemma():

    return render_template('gemma.html')#, answer = response)



def file_list(_dir, surfix):
    obj_filenames = os.listdir(os.path.join(app.static_folder, _dir))
    obj_filenames.sort()
    obj_urls = []
    for obj_filename in obj_filenames:
        obj_url = url_for('static', filename=os.path.join(_dir, obj_filename))
        obj_urls.append(obj_url)
    obj_urls = [f for f in obj_urls if f.endswith(surfix)]
    return obj_urls

@app.route('/slice/<sample_id>/<int:part_seq>')
def slice(sample_id, part_seq):

    if sample_id == '0083':
        obj_urls = file_list('0083/fractured_0',".obj")
        raw_urls = file_list('0083/Mouse_0083_Lhem_cFos_647_PV_488_Sagittal/Atlas Registration',".png")
        ann_urls = file_list('0083/Mouse_0083_Lhem_cFos_647_PV_488_Sagittal/Atlas Registration/Dembamaps',"_nl.png")
    else:
        obj_urls = file_list(f'{sample_id}/fractured_0',".obj")
        raw_urls = file_list(f'{sample_id.replace("_manual","")}/raw',".png")
        ann_urls = file_list(f'{sample_id.replace("_manual","")}/mask',".png")
        
    if part_seq == 0:
        obj_urls = obj_urls[:10]
        raw_urls = raw_urls[:10]
        ann_urls = ann_urls[:10]
    elif part_seq == 1:
        obj_urls = obj_urls[10:]
        raw_urls = raw_urls[10:]
        ann_urls = ann_urls[10:]

    print(obj_urls[:5])
    print(raw_urls[:5])
    print(ann_urls[:5])
    return render_template('slice.html', obj_urls = json.dumps(obj_urls), raw_urls = json.dumps(raw_urls), ann_urls = json.dumps(ann_urls))

@app.route('/brain')
def brain():
    _id_list = [13,136,211,341,424,454]
    print(_id_list)
    
    return render_template('brain.html', id_list = _id_list)

@app.route('/puzzle')
def puzzle():
    _id_list = [2,3,4,10,]
    print(_id_list)
    
    return render_template('puzzle.html', id_list = _id_list)

@app.route('/')
def index():

    
    return render_template('index.html')
    
if __name__ == '__main__':
    app.run(host='localhost')