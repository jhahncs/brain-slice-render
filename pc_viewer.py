from vedo import *
import os
from vedo.pyplot import plot

dir_obj = "C:/DATA/tg/0083/fractured_0"
dir_ann = "C:/DATA/0083/Mouse_0083_Lhem_cFos_647_PV_488_Sagittal/Atlas Registration/Dembamaps"
dir_raw = "C:/DATA/0083/Mouse_0083_Lhem_cFos_647_PV_488_Sagittal/Atlas Registration/"
filenames = os.listdir(dir_ann)
filenames = [f for f in filenames if f.endswith("nl.png")]


#plt = Plotter(shape=(2,10))
#plt.at(0).show(Image(dir_img+"/Mouse_0083_Lhem_cFos_647_PV_488_Sagittal_s002_nl.png").clone2d("bottom-right"))
# window shape can be expressed as "n/m" or "n|m"


plot_list = []



for _i, filename in enumerate(filenames[:4]):
    prefix = filename.replace('_nl.png',"")
    print(prefix)
    mesh = Mesh(dir_obj+"/"+prefix+"_nl.obj").c('blue5')
    img_ann = Image(dir_ann+"/"+prefix+"_nl.png").resize((800,600))
    img_raw  = Image(dir_raw+"/"+prefix+".png").resize((800,600))
    
    txt = Text3D(prefix,s=0.15, c='k', justify='center')
    #plot_mesh = plot(mesh,  title=filename)
    #plot_ann = plot(img_ann, title=filename)
    #plot_raw = plot(img_raw,  title=filename)
    #fig.insert(mesh)
    plot_list.append(txt)
    plot_list.append(mesh)
    plot_list.append(img_ann)
    plot_list.append(img_raw)

#mesh = Mesh("imgs/Mouse_0083_Lhem_cFos_647_PV_488_Sagittal_s002_nl.obj")
#mesh = Mesh("imgs/piece_0.obj")

plt = show(
     plot_list,
     shape="4|4|4|4|", 
     sharecam=False, size=(1300,900), zoom='tight',
)


plt.interactive().close()
