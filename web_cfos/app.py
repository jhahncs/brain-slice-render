from flask import Flask, jsonify
from flask import Flask, render_template
from flask import request
import os
from flask import url_for, render_template
import json
from werkzeug.utils import secure_filename

# some_file.py
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../cfos')

app = Flask(__name__)


@app.route('/gemma')
def gemma():
    print("gemma")

    if request.method == 'POST':
        file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join("files", filename))
       
    
    import cfos_util
    importlib.reload(cfos_util)

    import cfos_stat
    importlib.reload(cfos_stat)

    output_dir = "output"
    import shutil
    #try:
    #    shutil.rmtree(output_dir)
    #except:
    #    pass
    try:
        os.mkdir(output_dir)
    except:
        pass  

    cfos = cfos_util.Cfos(f'resources/SST_PV_cfos_Summary_Jin_Mehdi_March25_EXP.csv',
    f'resources/SST_PV_cfos_Summary_Jin_Mehdi_March25_VEH.csv',
    'output')

    df_pvalue_permutation_test = cfos_stat.cal_pvalue(cfos.df_mean_cor_sag, 'permutation_test',cfos.region_id_2_tg_id, cfos.region_id_2_name,'output/pvalue_permutation_test.csv')
    df_pvalue_ttest = cfos_stat.cal_pvalue(cfos.df_mean_cor_sag, 't_test',cfos.region_id_2_tg_id, cfos.region_id_2_name,'output/pvalue_ttest.csv')


    df_fdr_permutation_test = cfos_stat.cal_fdr(df_pvalue_permutation_test, cfos.region_id_2_tg_id, cfos.region_id_2_name, _alpha = 0.05, result_filename='output/pvalue_permutation_test_fdr.csv')
    df_fdr_t_test = cfos_stat.cal_fdr(df_pvalue_ttest, cfos.region_id_2_tg_id, cfos.region_id_2_name, _alpha = 0.05, result_filename='output/pvalue_ttest_fdr.csv')


    cfos.gen_zero_value_heatmap_color(f'output/regions_with_zero_values.pdf')
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