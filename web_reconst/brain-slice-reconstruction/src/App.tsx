import { useState, useEffect, useMemo, HTMLProps, useRef } from 'react'
import { TransformWrapper, TransformComponent, useControls } from "react-zoom-pan-pinch";
import { useReactTable, getCoreRowModel, getPaginationRowModel, createColumnHelper, getFilteredRowModel } from '@tanstack/react-table'
import Table, { Show } from './Test.tsx';
import './App.css'
import ObjViewer from './ObjViewer'; // Assuming ObjViewer is in ObjViewer.js
import { OrbitControls, Texture } from '@react-three/drei'; // Optional: for interactive camera control
import * as THREE from 'three'
import { Canvas, useThree } from '@react-three/fiber'
import { ImageList, ImageListItem, ImageListItemBar } from '@mui/material';
import { TIFFViewer } from 'react-tiff';
import ReactPlayer from "react-player";

import 'react-tiff/dist/index.css'
const fiberColors = [
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

const Toolbox = {
  display: "flex",
  width: "100%",
  margin_bottom: "10px",
};



function sanitizeFolderName(name) {
  // Replace special characters with a safe alternative (e.g., underscore)
  let sanitizedName = name.replace(/[<>:"/\\|?*\x00-\x1F]/g, "_");

  // Remove or replace leading/trailing spaces if needed
  sanitizedName = sanitizedName.trim();

  // Replace multiple spaces with a single space or underscore
  sanitizedName = sanitizedName.replace(/\s+/g, "_");

  // Optionally, convert to lowercase or uppercase
  //sanitizedName = sanitizedName.toLowerCase();

  return sanitizedName;
}


function App() {
  const [trainedModelList, setTrainedModelList] = useState([]);
  const [trainedModel, setTrainedModel] = useState(null);

  const [tickness, setTickness] = useState(0.001);
  const [spacing, setSpacing] = useState(0.007);
  const [isLoading, setIsLoading] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);



  const [isInferrenceDone, setIsInferrenceDone] = useState(false);

  const [loadingMessage, setLoadingMessage] = useState('');



  const [boundingBoxOfInputParts, setBoundingBoxOfInputParts] = useState([]);
  const [transformations, setTransformations] = useState([]);

  const [selectedBoundingBoxOfInputParts, setSelectedBoundingBoxOfInputParts] = useState([]);


  const [isVisible_transformations, setIsVisible_transformations] = useState(false);

  const toggleVisibility_transformations = () => {
    setIsVisible_transformations(!isVisible_transformations);
  };



  const [isVisible_model_setting, setIsVisible_model_setting] = useState(true);

  const toggleVisibility_model_setting = () => {
    setIsVisible_model_setting(!isVisible_model_setting);
  };

  const [isVisible_project_list, setIsVisible_project_list] = useState(true);

  const toggleVisibility_project_list = () => {
    setIsVisible_project_list(!isVisible_project_list);
  };

  const [isVisible_images, setIsVisible_images] = useState(false);

  const toggleVisibility_images = () => {
    setIsVisible_images(!isVisible_images);
  };

  const [isVisible_video, setIsVisible_video] = useState(false);

  const toggleVisibility_video = () => {
    setIsVisible_video(!isVisible_video);
  };
  const [isVisible_interactive_visualzation, setIsVisible_interactive_visualzation] = useState(false);

  const toggleVisibility_interactive_visualzation = () => {

    setIsVisible_interactive_visualzation(!isVisible_interactive_visualzation);
  };





  const [postprocessSummary, setPostprocessSummary] = useState("");
  const [tiffFilenames, setTiffFilenames] = useState([]);

  const [isSubmitting_add, setIsSubmitting_add] = useState(false);
  const [isFirstRender, setIsFirstRender] = useState(true); // Using useRef to track initial render
  const paramsInputDiv = useRef(null);
  const [isVisible_paramsInputDiv, setIsVisible_paramsInputDiv] = useState(false);

  const [objFile_pred_list, setObjFile_pred_list] = useState({
    "files/0/trans/0.obj": fiberColors[0],
    "files/0/trans/1.obj": fiberColors[1],
    "files/0/trans/2.obj": fiberColors[2],
    "files/0/trans/3.obj": fiberColors[3],
    "files/0/trans/4.obj": fiberColors[4],
    "files/0/trans/5.obj": fiberColors[5],
    "files/0/trans/6.obj": fiberColors[6],
    "files/0/trans/7.obj": fiberColors[7],
  });
  const [objFile_init_gt_list, setObjFile_init_gt_list] = useState({
    "files/0/trans/0.obj": fiberColors[0],
    "files/0/trans/1.obj": fiberColors[1],
    "files/0/trans/2.obj": fiberColors[2],
    "files/0/trans/3.obj": fiberColors[3],
    "files/0/trans/4.obj": fiberColors[4],
    "files/0/trans/5.obj": fiberColors[5],
    "files/0/trans/6.obj": fiberColors[6],
    "files/0/trans/7.obj": fiberColors[7],
  });
  const [objFile_list, setObjFile_list] = useState({
    "files/0/objs/0.001_0.007/fractured_0/0088.obj": fiberColors[0],
    "files/0/objs/0.001_0.007/fractured_0/0095.obj": fiberColors[1],
    "files/0/objs/0.001_0.007/fractured_0/0102.obj": fiberColors[2],
    "files/0/objs/0.001_0.007/fractured_0/0109.obj": fiberColors[3],
    "files/0/objs/0.001_0.007/fractured_0/0116.obj": fiberColors[4],
    "files/0/objs/0.001_0.007/fractured_0/0123.obj": fiberColors[5],
    "files/0/objs/0.001_0.007/fractured_0/0130.obj": fiberColors[6],
    "files/0/objs/0.001_0.007/fractured_0/0137.obj": fiberColors[7],
  });

  const onFileInputClick = (event) => {
    //console.log(selectedFile)
    event.target.value = '';
    //setSelectedFile(null);
    //console.log(selectedFile)
    //console.log('onFileInputClick')
  }


  const handleFileChange = (event) => {

    setSelectedFile(event.target.files[0]);

  };

  useEffect(() => {
    async function test() {
      if (selectedFile == null)
        return
      console.log('useEffect')
      console.log(selectedFile)
      var newDataName_ = sanitizeFolderName(selectedFile['name'])
      newDataName_ = newDataName_.replace('.zip', '')
      setNewDataName(newDataName_);
    }
    test();
  }, [selectedFile])

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting_add(true);

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      console.log('업로드 성공', data);



    } catch (error) {
      console.error('업로드 실패', error);
    }
    finally {
      setIsSubmitting_add(false);

    }
  };
  const [significantRegions, setSignificantRegions] = useState([]);




  const [projects, setProjects] = useState([]);

  useEffect(() => {
    async function fetchDataList() {
      try {
        const response = await fetch('/projects', { method: 'POST' });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const json = await response.json();
        setProjects(json.dirs);
      } catch (e) {
        console.log(e)
      }
    }

    if (isFirstRender) {
      console.log('project fetch')
      fetchDataList();
      setIsFirstRender(false)
    }
  }, [projects]);

  const [newDataName, setNewDataName] = useState('');
  const [selectedProjects, setSelectedProjects] = useState([]);

  const handleNewDataNameChange = (event) => {
    setNewDataName(event.target.value);
  };

  const handleAddData = async (event) => {
    event.preventDefault();
    if (newDataName.trim() == '') {
      console.log("new data name is empty!");
      return;
    }

    setIsSubmitting_add(true);
    setIsLoading(true);


    console.log(newDataName)
    console.log(selectedFile)
    const formData = new FormData();
    formData.append('newDataName', newDataName)
    formData.append('file', selectedFile);
    console.log(formData.get('file'))

    try {
      const response = await fetch('/newdata', {
        method: 'POST',
        'Content-Type': 'multipart/form-data',
        body: formData
      });

      const data = await response.json();
      setProjects([...projects, newDataName]);
      //setValidationReport(data['ValidationReport'])

      //alert(data['message']);

    } catch (error) {
      console.error('업로드 실패', error);

    }
    finally {


    }

    setSelectedFile(null);
    setNewDataName('');
    setIsSubmitting_add(false);
    setIsLoading(false);

  };





  const handleSelectItem = async (index) => {

    setIsLoading(true)

    console.log('handleSelectItem')
    console.log(index)

    //setImageData(null)
    setIsVisible_paramsInputDiv(false)
    setIsVisible_images(false)
    
    setIsVisible_video(false)
    setIsVisible_interactive_visualzation(false)

    setSelectedProjects([index]);
    console.log(selectedProjects)

    const formData = new FormData();
    formData.append('dataname', index);

    console.log(formData.get('dataname'))

    try {
      const response = await fetch('/load', {
        method: 'POST',

        'Content-Type': 'multipart/form-data',

        body: formData
      });

      const data = await response.json();
      //setProjects([...projects, newDataName]);
      //alert("Successfully removed:"+data['message']);
      setTiffFilenames(data['tiff_filenames'])
      setTrainedModelList(data['traind_models'])
      setTrainedModel(data['traind_models'][0])
      setIsVisible_images(true)
    } catch (error) {
      console.error('error', error);

    }
    finally {
      setIsLoading(false)


    }



  };

  const handleRemoveSelectedItems = async () => {


    if (selectedProjects.length == 0) {

      alert("please select a data")
      return
    }

    console.log(selectedProjects[0])
    const formData = new FormData();
    formData.append('dataname', selectedProjects[0])

    try {
      const response = await fetch('/removedata', {
        method: 'POST',
        'Content-Type': 'multipart/form-data',

        body: formData
      });

      const data = await response.json();

      alert("Successfully removed:" + data['message']);
      //setProjects(projects.filter((_, index) => !selectedProjects.includes(index)));
      setSelectedProjects([]);

      
    } catch (error) {
      console.error('업로드 실패', error);
    }
    finally {


    }


  };
  const [data, setData] = useState<Show[]>();

  const columnHelper = createColumnHelper<Show>();
  //define our table headers and data



  const handleCheckboxColorsChange = (event) => {
    event.preventDefault();
    if (selectedProjects.length == 0) {

      alert("please select a data")
      return
    }

    setIsLoading(true)
    const itemValue = event.target.value;
    const isChecked = event.target.checked;
    if (isChecked) {
      //setCheckedColors([...checkedColors, itemValue]);
      setCheckedColors([itemValue]);

    } else {
      //setCheckedColors(checkedColors.filter((item) => item !== itemValue));
      setCheckedColors([]);
    }
    setIsLoading(false)
  }





  const handleTrainedModelSelect = async (event) => {
    event.preventDefault();
    setTrainedModel(event.target.value)

  };






  function build_form() {

    const formData = new FormData();
    formData.append('trainedModel', trainedModel)
    formData.append('tickness', tickness)
    formData.append('spacing', spacing)
    formData.append('projectname', selectedProjects[0])
    console.log(formData)
    return formData
  }

  const handleInferenceParams = async (event) => {
    event.preventDefault();
    if (selectedProjects.length == 0) {

      alert("please select a project")
      return
    }

    setIsVisible_paramsInputDiv(false);

    setIsLoading(true)
    setLoadingMessage('Reconstructing into 3D... It may take a few minutes.');
    setIsInferrenceDone(false)
    
    setObjFile_list([])
    setObjFile_pred_list([])
    setObjFile_init_gt_list([])
    setTransformations([])

    const formData = build_form()
    console.log(formData)

    try {
      const response = await fetch('/reconstruct', {
        method: 'POST',
        'Content-Type': 'multipart/form-data',
        body: formData
      });
      const data = await response.json();

      setIsVisible_paramsInputDiv(true);
      


      let temp_obj_files = {}
      let temp_obj_pred_files = {}
      let temp_obj_init_gt_files = {}
      for (const i in data['obj_files']) {
        temp_obj_files[data['obj_files'][i]] = fiberColors[i]
      }
      for (const i in data['obj_init_gt_files']) {
        temp_obj_init_gt_files[data['obj_init_gt_files'][i]] = fiberColors[i]
      }

      for (const i in data['obj_pred_files']) {
        temp_obj_pred_files[data['obj_pred_files'][i]] = fiberColors[i]
      }
      setObjFile_list(temp_obj_files)
      setObjFile_pred_list(temp_obj_pred_files)
      setObjFile_init_gt_list(temp_obj_init_gt_files)

      setBoundingBoxOfInputParts(data['df_total'])

      setPostprocessSummary(data['postProcessSummary'])
      setIsInferrenceDone(true)

    } catch (error) {
      console.error('업로드 실패', error);
    }
    finally {
      setIsLoading(false)

    }
  };

  const [isVisible_basic, setIsVisible_basic] = useState(false);

  const toggleVisibility_basic = () => {
    setIsVisible_basic(!isVisible_basic);
  };
  const [isVisible_foldchange, setIsVisible_foldchange] = useState(true);

  const toggleVisibility_foldchange = () => {
    setIsVisible_foldchange(!isVisible_foldchange);
  };

  const [isVisible_brainheatmap, setIsVisible_brainheatmap] = useState(true);

  const toggleVisibility_brainheatmap = () => {
    setIsVisible_brainheatmap(!isVisible_brainheatmap);
  };


  const [isVisible_significantregion, setIsVisible_significantregion] = useState(true);

  const toggleVisibility_significantregion = () => {
    setIsVisible_significantregion(!isVisible_significantregion);
  };

  const upArrowUnicode = '\u2191';
  const downArrowUnicode = '\u2193';

  const columns_boundingBoxOfInputParts = useMemo(
    () => [


      columnHelper.accessor("part_index", {
        header: "part",
        cell: (info) => info.getValue(),
        size: '5%'
      }),
      columnHelper.accessor("color", {
        header: "color",
        cell: (info) => info.getValue(),
        size: '10%'
      }),
      columnHelper.accessor("chamfer_dist", {
        header: "chamfer_dist",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("x_min", {
        header: "x_min",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("x_max", {
        header: "x_max",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("y_min", {
        header: "y_min",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("y_max", {
        header: "y_max",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("z_min", {
        header: "z_min",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("z_max", {
        header: "z_max",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("tX", {
        header: "pred_tX",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("tY", {
        header: "pred_tY",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("tZ", {
        header: "pred_tZ",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("rW", {
        header: "pred_rW",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("rX", {
        header: "pred_rX",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("rY", {
        header: "pred_rY",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),
      columnHelper.accessor("rZ", {
        header: "pred_rZ",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        size: '10%'
      }),

      /*
      columnHelper.accessor("color", {
        header: "Color",
        cell: (info) => info.getValue(),
        //filterSelectOptions: ['Male', 'Female', 'Other'],

      }),
      */
    ],
    [],
  );


  
  return (

    <div style={{ cursor: isLoading ? 'wait' : 'default' }}>
      {isLoading && <div className="overlay"><div className="loading-message">{loadingMessage}</div></div>}


      <div className="collapsible-header" onClick={toggleVisibility_project_list}>
        <span><b>Projects stored in the server</b></span>
        <span className={`arrow ${isVisible_project_list ? 'up' : 'down'}`}>
          {isVisible_project_list ? '▲' : '▼'}
        </span>
      </div>

      <div className={`collapsible-content ${isVisible_project_list ? 'open' : ''}`}>


        <table border='true'>
          <thead></thead>
          <tbody>
            <tr>
              <td width='60%'>


                <ul>
                  {projects.map((item, index) => (
                    <li
                      key={item}
                      onClick={() => handleSelectItem(item)}
                      style={{
                        backgroundColor: selectedProjects.includes(item)
                          ? 'lightblue'
                          : 'transparent',
                        cursor: 'pointer',
                      }}
                    >
                      {item}
                    </li>
                  ))}
                </ul>
              </td>
              <td rowSpan='2'>
                <b>Upload an Zip file containing TIFF images</b>
                <div className={isSubmitting_add ? 'submitting' : ''}>

                  <form onSubmit={handleAddData}>
                    <input type="file" id="myFileInput" onClick={onFileInputClick} onChange={handleFileChange} /> <br></br>
                    Project Name: <input type="text" id='new_data_name' defaultValue={newDataName} onChange={handleNewDataNameChange} />
                    <button type="submit" disabled={isSubmitting_add}>{isSubmitting_add ? 'Processing...(may take a few minutes)' : 'Add Data'}</button>


                  </form>
                </div>
                <br></br>
                <button onClick={handleRemoveSelectedItems}>Remove Selected Data</button>



              </td>


            </tr>

          </tbody>
        </table>
      </div>





      <div className="collapsible-header" onClick={toggleVisibility_images}>
        <span><b>Images in the selected project</b></span>
        <span className={`arrow ${isVisible_images ? 'up' : 'down'}`}>
          {isVisible_images ? '▲' : '▼'}
        </span>
      </div>

      <div className={`collapsible-content ${isVisible_images ? 'open' : ''}`}>



        <ImageList sx={{ width: '100%', height: 210 }} cols={10} rowHeight={100}>
          {tiffFilenames && Object.keys(tiffFilenames).map((item) => (
            <ImageListItem key={item} sx={{ width: '100%', height: '100%' }}>
              <img src={tiffFilenames[item]} loading="lazy" style={{ width: '10', objectFit: 'scale-down' }} />
              <ImageListItemBar
                title={tiffFilenames[item].split("/")[2].replace('.tif',"")}
                subtitle={fiberColors[item]}
                position="bottom"
                sx={{

                    background:
                  "linear-gradient(to bottom, rgba(0,0,0,0.7) 0%, " +
                  "rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)"
                  ,
                  '& .MuiImageListItemBar-title': {
                    color: fiberColors[item],
                    fontSize: '15px'
                  },
                  '& .MuiImageListItemBar-subtitle': {
                    color: fiberColors[item],
                    fontSize: '15px'
                  }
                  
                }}
              />
            </ImageListItem>
          ))}
        </ImageList>
      </div>
      <div className="collapsible-header" onClick={toggleVisibility_model_setting}>
        <span><b>Perform reconstruction</b></span>
        <span className={`arrow ${isVisible_model_setting ? 'up' : 'down'}`}>
          {isVisible_model_setting ? '▲' : '▼'}
        </span>
      </div>

      <div className={`collapsible-content ${isVisible_model_setting ? 'open' : ''}`}>

        <table border='1px' cellspacing='2'>
          <thead></thead>
          <tbody>
            <tr align='center' >
              <td>Trained Model</td>
              <td>Tickness of one slice</td>
              <td>Spacing between slices</td>
              <td rowSpan='2' style={{ verticalAlign: 'middle' }}>
                <input style={{ cursor: isLoading ? 'wait' : 'default' }} type="button" id={"Reconstruct"} name={"Reconstruct"} value={"Reconstruct"}
                  onClick={handleInferenceParams}
                ></input></td>
            </tr>


            <tr padding='20px' align='center'>
              <td padding='20px' >
                <select
                  value={trainedModel} // ...force the select's value to match the state variable...
                  onChange={e => handleTrainedModelSelect(e)} // ... and update the state variable on any change!
                >

                  {trainedModelList &&
                    trainedModelList.map(item => (

                      <option style={{ cursor: isLoading ? 'wait' : 'default' }} name={item} key={item} value={item}>{item}</option>
                    ))}
                </select>
              </td>
              <td padding='20px'>
                {
                  <><input type="number" onChange={e => setTickness(e.target.value)} name='tickness' style={{ width: "50px" }} value={tickness} />
                  </>
                }


              </td>

              <td padding='20px'>
                {
                  <><input type="number" onChange={e => setSpacing(e.target.value)} name='spacing' style={{ width: "50px" }} value={spacing} />
                  </>
                }


              </td>


            </tr>


          </tbody>
        </table>

      <div>
        <p>
          {postprocessSummary &&
            (Object.keys(postprocessSummary).map((key) => (
              <div key={key}>
                <strong>{key}: </strong> {postprocessSummary[key]}
              </div>
            )
            ))

          }
        </p>
      </div>

      </div>

      <div className="collapsible-header" onClick={toggleVisibility_video}>
        <span><b>Reconstruction Result: Quater View</b></span>
        <span className={`arrow ${isVisible_video ? 'up' : 'down'}`}>
          {isVisible_video ? '▲' : '▼'}
        </span>
      </div>

      <div className={`collapsible-content ${isVisible_video ? 'open' : ''}`}>
        {isInferrenceDone &&
          <table>
            <tr>
              <td>Golden Standard</td>
              <td>Random Position</td>
              <td>Reconstruction(Video)</td>
              <td>Reconstruction</td>
            </tr>
            <tr>
              <td>
                <ObjViewer objFilePath_list={objFile_list}/>
              </td>
              <td>
                <ObjViewer objFilePath_list={objFile_init_gt_list}/>
              </td>
              <td>
                <ReactPlayer
                  url={selectedProjects[0] + "/video/video.mp4"}
                  width="400px"
                  playing={true}
                  controls={true}
                  loop={false}
                  muted={true}
                  playsinline={true}
                  
                />                
              </td>
              <td>            
                <ObjViewer objFilePath_list={objFile_pred_list} />
              </td>

            </tr>


          </table>
        }
      </div>

      <div className="collapsible-header" onClick={toggleVisibility_transformations}>
        <span><b>Predicted Transformations</b></span>
        <span className={`arrow ${isVisible_transformations ? 'up' : 'down'}`}>
          {isVisible_transformations ? '▲' : '▼'}
        </span>
      </div>

      <div className={`collapsible-content ${isVisible_transformations ? 'open' : ''}`} style={{ 'border-style': 'solid', 'border-width': '2px', 'border-color': 'black' }}>


        <span>{boundingBoxOfInputParts && <Table columns={columns_boundingBoxOfInputParts} data={boundingBoxOfInputParts} setSelectedRows={setSelectedBoundingBoxOfInputParts} />}</span> 
        
      </div>


    </div>

  );
}

function IndeterminateCheckbox({
  indeterminate,
  className = '',
  ...rest
}: { indeterminate?: boolean } & HTMLProps<HTMLInputElement>) {
  const ref = useRef<HTMLInputElement>(null!)

  useEffect(() => {
    if (typeof indeterminate === 'boolean') {
      ref.current.indeterminate = !rest.checked && indeterminate
    }
  }, [ref, indeterminate])

  return (
    <input
      type="checkbox"
      ref={ref}
      className={className + ' cursor-pointer'}
      {...rest}
    />
  )
}

export default App;
