import { useState, useEffect, useMemo, HTMLProps, useRef } from 'react'
import { TransformWrapper, TransformComponent, useControls } from "react-zoom-pan-pinch";
import { useReactTable, getCoreRowModel, getPaginationRowModel, createColumnHelper, getFilteredRowModel } from '@tanstack/react-table'
import Table, { Show } from './Test.tsx';
import axios from "axios";
import { saveAs } from 'file-saver';
import './App.css'
import { downloadAsync, documentDirectory } from 'expo-file-system';


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

  const [pvalue, setPvalue] = useState(0.05);
  const [foldup, setFoldup] = useState(1.5);
  const [folddown, setFolddown] = useState(0.67);
  const [pvalue_cur, setPvalue_cur] = useState(0.05);
  const [foldup_cur, setFoldup_cur] = useState(1.5);
  const [folddown_cur, setFolddown_cur] = useState(0.67);
  const [isAllDownlodButtonVisible, setIsAllDownlodButtonVisible] = useState(true);

  const [isLoading, setIsLoading] = useState(false);
  const [selectedSignificantRegionRows, setSelectedSignificantRegionRows] = useState([]);
  const [loadingMessage, setLoadingMessage] = useState('');


  const [selectedFile, setSelectedFile] = useState(null);
  const [groupNames, setGroupNames] = useState([]);

    const [validationReport, setValidationReport] = useState({});

  const [preprocessSummary, setPreprocessSummary] = useState({});
  const [postprocessSummary, setPostprocessSummary] = useState(0);
  const [imageData, setImageData] = useState(1);
  const [imageBasicStat, setImageBasicStat] = useState(1);

  const [isSubmitting_add, setIsSubmitting_add] = useState(false);
  const [isSubmitting_analysis_list, setIsSubmitting_analysis_list] = useState(false);
  const [isSubmitting_analysis_both, setIsSubmitting_analysis_both] = useState(false);
  const [isFirstRender, setIsFirstRender] = useState(true); // Using useRef to track initial render
  const [downloadLink, setDownloadLink] = useState('');
  const [analysisMode, setAnalysisMode] = useState(null);
  const [checkedColors, setCheckedColors] = useState([]);
  const paramsInputDiv = useRef(null);
  const [isVisible_paramsInputDiv, setIsVisible_paramsInputDiv] = useState(false);


  const onFileInputClick = (event) => {
    //console.log(selectedFile)
    event.target.value = '';
    //setSelectedFile(null);
    //console.log(selectedFile)
    //console.log('onFileInputClick')
  }

  const handlePvalueChange = (event) => {
    setPvalue(event.target.value);
  };
  const handleFoldupChange = (event) => {
    setFoldup(event.target.value);
  };
  const handleFolddownChange = (event) => {
    setFolddown(event.target.value);
  };

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

      setPreprocessSummary(data.message);


    } catch (error) {
      console.error('업로드 실패', error);
    }
    finally {
      setIsSubmitting_add(false);

    }
  };
  const [significantRegions, setSignificantRegions] = useState([]);



  const Controls = () => {
    const { zoomIn, zoomOut, resetTransform } = useControls();

    return (
      <div style={Toolbox}>
        <button onClick={() => zoomIn()}>+</button>
        <button onClick={() => zoomOut()}>-</button>
        <button onClick={() => resetTransform()}>Reset</button>
      </div>
    );
  };

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
      setValidationReport(data['ValidationReport'])
      
      alert(data['message']);

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
    setPreprocessSummary({ 'processing..': "" });
    console.log('handleSelectItem')
    console.log(index)

         setImageData(null)
      setSignificantRegions(null);
      setIsAllDownlodButtonVisible(false)
          setIsVisible_paramsInputDiv(false)

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
      console.log(data['message'])
      console.log(data['group_names'])
      setGroupNames(data['group_names'])
      setGroup1_name(data['group_names'][0])
      setGroup2_name(data['group_names'][1])


      let temp_color_basic = {}
      let temp_color_minus = {}
      let temp_color_fraction = {}
      console.log(data['color_names'])
      for (const _color of data['color_names']) {

        if (_color.includes('+') || _color.includes('-'))
          temp_color_minus[_color] = 0
        else if (_color.includes('/'))
          temp_color_fraction[_color] = 0
        else
          temp_color_basic[_color] = 0

      }
      console.log(temp_color_basic)
      console.log(temp_color_minus)
      console.log(temp_color_fraction)


      setColor_basic(temp_color_basic)
      setColor_minus(temp_color_minus)
      setColor_fraction(temp_color_fraction)

      setPreprocessSummary(data['message']);
      setImageBasicStat(data['image'])
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
      setPreprocessSummary('no data selected');
    } catch (error) {
      console.error('업로드 실패', error);
    }
    finally {


    }


  };
  const [data, setData] = useState<Show[]>();

  const columnHelper = createColumnHelper<Show>();
  //define our table headers and data

  const columns = useMemo(
    () => [
      {
        id: 'select',
        header: ({ table }) => (
          <IndeterminateCheckbox
            {...{
              checked: table.getIsAllRowsSelected(),
              indeterminate: table.getIsSomeRowsSelected(),
              onChange: table.getToggleAllRowsSelectedHandler(),
            }}
          />
        ),
        cell: ({ row }) => (
          <div >
            <IndeterminateCheckbox
              {...{
                checked: row.getIsSelected(),
                disabled: !row.getCanSelect(),
                indeterminate: row.getIsSomeSelected(),
                onChange: row.getToggleSelectedHandler(),
              }}
            />
          </div>
        ),
      },

      columnHelper.accessor("TG number", {
        header: "TG number",
        cell: (info) => info.getValue(),
        size: '5%'
      }),
      columnHelper.accessor("Region Name", {
        header: "Region Name",
        cell: (info) => info.getValue(),
        size: '70%'
      }),
      columnHelper.accessor("fold", {
        header: "fold",
        cell: (info) => parseFloat(info.getValue().toFixed(3)),
        enableColumnFilter: false,
        size: '10%'
      }),
      columnHelper.accessor("Region ID", {
        header: "Region ID",
        cell: (info) => info.getValue(),
        size: '5%'
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
  useEffect(() => {



    async function fetchBrainheatmap() {



      /*
      console.log(significantRegions[Object.keys(selectedSignificantRegionRows)[0]])

      console.log(significantRegions[Object.keys(selectedSignificantRegionRows)[0]])
      try{
          console.log(significantRegions[Object.keys(selectedSignificantRegionRows)[0]]['color'])
      }catch (error) {
        return
      }
      finally {


      }
      */
      setImageData(null)
      setSignificantRegions(null);
      setIsAllDownlodButtonVisible(false)
      if (checkedColors.length == 0)
        return

      setIsLoading(true)
      setLoadingMessage('Loading brain heatmaps... If this is your first time setting these parameters, it may take a few minutes.');

      console.log(checkedColors[0])

      const formData = build_form();


      try {
        const response = await fetch('/brainheatmap', {
          method: 'POST',
        'Content-Type': 'multipart/form-data',
      
          
          body: formData
        });

        const data = await response.json();
        if (checkedColors[0] == 'ALL') {
          setIsAllDownlodButtonVisible(true)
          setDownloadLink(data.zip)
        }
        else {

          setImageData(data.image)
          setSignificantRegions(data.df);
        }
      } catch (error) {
        console.error('업로드 실패', error);
      }
      finally {
        setIsLoading(false)

      }
    }


    fetchBrainheatmap()





  }, [checkedColors]);

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

  const handleAllDownload = async (event) => {
    event.preventDefault();
    if (selectedProjects.length == 0) {

      alert("please select a data")
      return
    }
    console.log(event.target)
    console.log(event.target.checked)
    console.log(checkedColors)
    setIsLoading(true)
    setCheckedColors([]);
    setLoadingMessage('Generating brain heatmaps... If this is your first time setting these parameters, it may take a few minutes.');



    const formData = build_form()



    try {
      const response = await fetch('/downloadall', {
        method: 'POST',
        'Content-Type': 'multipart/form-data',
        responseType: 'blob',
        body: formData
      });
      //const { uri: localUri } = await downloadAsync('http://192.168.0.12:5000/video.mp4', documentDirectory + 'video.mp4');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob)
      //document.location = url

      const a = document.createElement('a');
      a.href = url;
      a.download = 'heatmaps.zip';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);


    } catch (error) {
      console.error('request failed', error);
    }
    finally {
      setIsLoading(false)

    }



  }

  const [group1_name, setGroup1_name] = useState(null);
  const [group2_name, setGroup2_name] = useState(null);

  const [pairwiseCompareMethod, setPairwiseCompareMethod] = useState('permutation-test');
  const [multipleCompareCorrectionMethod, setMultipleCompareCorrectionMethod] = useState('FDR');
  const [fdr_alpha, setfdr_alpha] = useState(0.05);


  const handlePairwiseCompareMethodSelect = async (event) => {
    event.preventDefault();
    setIsVisible_paramsInputDiv(false)
    setPairwiseCompareMethod(event.target.value)

  };
  const handleMultipleCompareCorrectionMethodSelect = async (event) => {
    event.preventDefault();
    setIsVisible_paramsInputDiv(false)
    setMultipleCompareCorrectionMethod(event.target.value)

  };





  const handleGroup1NameSelect = async (event) => {
    event.preventDefault();
    setIsVisible_paramsInputDiv(false)
    setGroup1_name(event.target.value)

  };

  const handleGroup2NameSelect = async (event) => {
    event.preventDefault();
    setIsVisible_paramsInputDiv(false)
    setGroup2_name(event.target.value)

  };
  function build_form()
  {

    const formData = new FormData();
    formData.append('pvalue', pvalue)
    formData.append('fold_up', foldup)
    formData.append('fold_down', folddown)
    formData.append('group1_name', group1_name)
    formData.append('group2_name', group2_name)
    formData.append('pairwiseCompareMethod', pairwiseCompareMethod)
    formData.append('multipleCompareCorrectionMethod', multipleCompareCorrectionMethod)
    formData.append('fdr_alpha', fdr_alpha)

    formData.append('distanceLabel', distanceLabel)
    formData.append('numOfSlices', numOfSlices)

    //formData.append('color', significantRegions[Object.keys(selectedSignificantRegionRows)[0]]['color'])
    formData.append('color', checkedColors[0])
    formData.append('dataname', selectedProjects[0])
    console.log('distanceLabel',formData.get('distanceLabel'))
    return formData
  }

  const handleUpdateParams = async (event) => {
    event.preventDefault();
    if (selectedProjects.length == 0) {

      alert("please select a data")
      return
    }
    if (group1_name == group2_name) {

      alert("Please select different groups")
      return
    }
    setCheckedColors([]);
    setIsVisible_paramsInputDiv(false);
    setImageData(null)
    setSignificantRegions(null);
    setIsAllDownlodButtonVisible(false)

    setIsLoading(true)
    setLoadingMessage('Calculating fold changes... If this is your first time setting these parameters, it may take a few minutes.');

    setColor_basic(color_basic_const)
    setColor_minus(color_minus_const)
    setColor_fraction(color_fraction_const)
    const formData = build_form()


    try {
      const response = await fetch('/fold', {
        method: 'POST',
        'Content-Type': 'multipart/form-data',
        body: formData
      });
      let temp_color_basic = {}
      let temp_color_minus = {}
      let temp_color_fraction = {}
      const data = await response.json();
      for (const color in data['freq']) {
        if (color in color_basic) {
          temp_color_basic[color] = data['freq'][color]
        }
        else if (color in color_minus) {
          temp_color_minus[color] = data['freq'][color]
        }
        else if (color in color_fraction) {
          temp_color_fraction[color] = data['freq'][color]
        }

      }
      setColor_basic(temp_color_basic)
      setColor_minus(temp_color_minus)
      setColor_fraction(temp_color_fraction)
      setNumOfRegionsWithZero(data['region_ids_with_all_zero'])
      
      setFoldup_cur(foldup)
      setFolddown_cur(folddown)
      setPvalue_cur(pvalue)
      setIsVisible_paramsInputDiv(true);

    } catch (error) {
      console.error('업로드 실패', error);
    }
    finally {
      setIsLoading(false)

    }
  };
  const pairwiseCompareMethods = ['t-test', 'permutation-test']
  const multipleCompareCorrectionMethods = ['None', 'FDR']


  const [numOfRegionsWithZero, setNumOfRegionsWithZero] = useState(0);

  const [numOfSlices, setNumOfSlices] = useState(10);
  const [distanceLabel, setDistanceLabel] = useState(false);
  const color_basic_const = { 'SST': { 'up': 0, 'down': 0 }, 'PV': { 'up': 0, 'down': 0 }, 'cfos': { 'up': 0, 'down': 0 }, 'cfos total': { 'up': 0, 'down': 0 } }
  const color_minus_const = { 'SST-PV-cfos': { 'up': 0, 'down': 0 }, 'SST-cfos': { 'up': 0, 'down': 0 }, 'PV-cfos': { 'up': 0, 'down': 0 }, 'SST-PV': { 'up': 0, 'down': 0 } }
  const color_fraction_const = { 'SST-PV/cfos fraction': { 'up': 0, 'down': 0 }, 'SST/cfos fraction': { 'up': 0, 'down': 0 }, 'PV/cfos fraction': { 'up': 0, 'down': 0 } }
  const [color_basic, setColor_basic] = useState(color_basic_const);
  const [color_minus, setColor_minus] = useState(color_minus_const);
  const [color_fraction, setColor_fraction] = useState(color_fraction_const);

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


  useEffect(() => {
    setCheckedColors([])
    //const f = build_form()
    //
    // console.log(f.get('distanceLabel'))
    //console.log(build_form()['numOfSlices'])
  }, [distanceLabel, numOfSlices])


  return (

    <div style={{ cursor: isLoading ? 'wait' : 'default' }}>
      {isLoading && <div className="overlay"><div className="loading-message">{loadingMessage}</div></div>}

      <div>
        <h3>Data uploaded in the server </h3>
        <table border='true'>
          <thead></thead>
          <tbody>
            <tr>
              <td width='80%'>


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
                <b>Upload an Excel file</b>
                <div className={isSubmitting_add ? 'submitting' : ''}>

                  <form onSubmit={handleAddData}>
                    <input type="file" id="myFileInput" onClick={onFileInputClick} onChange={handleFileChange} />
                    Data Name: <input type="text" id='new_data_name' defaultValue={newDataName} onChange={handleNewDataNameChange} />
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
      <div>
        <p>
        {preprocessSummary &&
            (Object.keys(preprocessSummary).map((key) => (
              <div key={key}>
                <strong>{key}: </strong> {preprocessSummary[key]}
              </div>
            )
            ))

          }
        </p>
      </div>
              <p>
          {validationReport &&
            (Object.keys(validationReport).map((key) => (
              <div style={{  'color': 'red' }} key={key}>
                <strong>{key}: </strong> {validationReport[key]}
              </div>
            )
            ))

          }
        </p>
      <div className="collapsible-header" onClick={toggleVisibility_basic}>
        <span><b>Regions having zero values</b></span>
        <span className={`arrow ${isVisible_basic ? 'up' : 'down'}`}>
          {isVisible_basic ? '▲' : '▼'}
        </span>
      </div>

      <div className={`collapsible-content ${isVisible_basic ? 'open' : ''}`}>




        <div style={{ 'borderStyle': 'solid', 'borderWidth': '2px', 'borderColor': 'black' }}>
          <TransformWrapper
            defaultScale={1}
            defaultPositionX={200}
            defaultPositionY={100}
          >

            {({ zoomIn, zoomOut, resetTransform, positionX, positionY, ...rest }) => (
              <>
                <Controls />

                <TransformComponent >
                  <img
                    src={`data:image/jpeg;base64,${imageBasicStat}`}
                    //src="https://cdn.sstatic.net/Img/unified/sprites.svg?v=e5e58ae7df45"
                    width='100%'
                    alt="A data heatmap will be shown here" />
                </TransformComponent>
              </>
            )}
          </TransformWrapper>
        </div>

        <hr></hr>
      </div>

      <div className="collapsible-header" onClick={toggleVisibility_foldchange}>
        <span><b>Fold Change</b></span>
        <span className={`arrow ${isVisible_foldchange ? 'up' : 'down'}`}>
          {isVisible_foldchange ? '▲' : '▼'}
        </span>
      </div>

      <div className={`collapsible-content ${isVisible_foldchange ? 'open' : ''}`}>



        <form >

          <b>Group1:</b>&nbsp;
          <select
            value={group1_name} // ...force the select's value to match the state variable...
            onChange={e => handleGroup1NameSelect(e)} // ... and update the state variable on any change!
          >

            {groupNames &&
              groupNames.map(item => (

                <option style={{ cursor: isLoading ? 'wait' : 'default' }} name={item} key={item} value={item}>{item}</option>
              ))}
          </select>&nbsp;&nbsp;
          <b>Group2:</b>&nbsp;
          <select
            value={group2_name} // ...force the select's value to match the state variable...
            onChange={e => handleGroup2NameSelect(e)} // ... and update the state variable on any change!
          >

            {groupNames &&
              groupNames.map(item => (

                <option style={{ cursor: isLoading ? 'wait' : 'default' }} name={item} key={item} value={item}>{item}</option>
              ))}
          </select>


          <table border='1px'>
            <thead></thead>
            <tbody>
              <tr padding='20px'>
                <td padding='20px'>
                  <span style={{ color: 'green' }}>Fold(Group1/Group2) &#8805; </span>  <input type="number" onChange={handleFoldupChange} name='fold_up' value={foldup} style={{ width: "60px",color: 'green',textAlign: 'center'   }} />
                  
                </td>
                <td padding='20px'>
                  <span style={{ color: 'red' }}>Fold(Group1/Group2) &#8804; </span><input type="number" onChange={handleFolddownChange} name='fold_down' value={folddown} style={{ width: "60px",color: 'red',textAlign: 'center'  }} />
                  
                </td>

              </tr>


            </tbody>
          </table>
          <table border='1px'>
            <thead></thead>
            <tbody>
              <tr>
                <td>Pairwise comparison</td>
                <td>Multiple comparison correction</td>
                  <td rowSpan='2' style={{verticalAlign:'middle'}}>
                P-value &#60;  <input type="number" onChange={handlePvalueChange} name='pvalue'  style={{ width: "60px",color: 'black',textAlign: 'center'  }} value={pvalue} />

                </td>
                <td rowSpan='2'  style={{verticalAlign:'middle'}}>               <input style={{ cursor: isLoading ? 'wait' : 'default' }} type="button" id={"UPDATE"} name={"UPDATE"} value={"UPDATE"}
                    onClick={handleUpdateParams}
                  ></input></td>
              </tr>

            
              <tr padding='20px'>
                <td padding='20px'>
                  <select
                    value={pairwiseCompareMethod} // ...force the select's value to match the state variable...
                    onChange={e => handlePairwiseCompareMethodSelect(e)} // ... and update the state variable on any change!
                  >

                    {pairwiseCompareMethods &&
                      pairwiseCompareMethods.map(item => (

                        <option style={{ cursor: isLoading ? 'wait' : 'default' }} name={item} key={item} value={item}>{item}</option>
                      ))}
                  </select>
                </td>
                <td padding='20px'>
                  <select
                    value={multipleCompareCorrectionMethod} // ...force the select's value to match the state variable...
                    onChange={e => handleMultipleCompareCorrectionMethodSelect(e)} // ... and update the state variable on any change!
                  >

                    {multipleCompareCorrectionMethods &&
                      multipleCompareCorrectionMethods.map(item => (

                        <option style={{ cursor: isLoading ? 'wait' : 'default' }} name={item} key={item} value={item}>{item}</option>
                      ))}
                  </select>
                  {
                    multipleCompareCorrectionMethod == 'FDR' &&
                    <>&nbsp;
                      &#60; <input type="number" onChange={e => setfdr_alpha(e.target.value)} name='fdr_alphaalue' style={{ width: "50px" }} value={fdr_alpha} />
                    </>
                  }


                </td>
                
  
              </tr>


            </tbody>
          </table>
          <hr></hr>
          <table border='1px'>
            <thead>


            </thead>
            <tbody>
              <tr padding='20px'>
                <td padding='20px'>

                  Render distance label: &nbsp; <input type="checkbox" checked = {distanceLabel} onChange={e => setDistanceLabel(e.target.checked)} name='distanceLabel' style={{ width: "50px" }}/>

                </td>
                <td padding='20px'>
                  
                  The number of slices: &nbsp; <input type="number" onChange={e => setNumOfSlices(e.target.value)} name='numOfSlices' style={{ width: "50px" }} value={numOfSlices} />



                </td>
                <td>



                </td>
              </tr>


            </tbody>
          </table>


          <div ref={paramsInputDiv} style={{ cursor: isLoading ? 'wait' : 'default', display: isVisible_paramsInputDiv ? 'block' : 'none' }}>
                          The number of regions with all zero: {numOfRegionsWithZero}
              
            <br></br>
            <div key='fold params'>Current parameters settings: <br></br>Group1 = {group1_name}, Group2 = {group2_name}, fold up = {foldup_cur}, fold down = {folddown_cur}, pvalue = {pvalue_cur}</div>
            <br></br>
                          

            {color_basic &&
              Object.keys(color_basic).map(item => (

                <><input style={{ cursor: isLoading ? 'wait' : 'default' }} type="checkbox" key={item} id={item} name={item} value={item}
                  checked={checkedColors.includes(item)}
                  onChange={handleCheckboxColorsChange}></input>
                  <span key={item + 'span'} style={{ fontWeight: checkedColors.includes(item) ? 'bold' : 'normal' }}>{item}  ( <span style={{ color: 'green' }}> {upArrowUnicode} {color_basic[item]['up']}</span>,  <span style={{ color: 'red' }}> {downArrowUnicode} {color_basic[item]['down']}</span>) </span>&nbsp;&nbsp;&nbsp;</>
              ))}
            <br></br>
            {color_minus &&
              Object.keys(color_minus).map(item => (

                <><input style={{ cursor: isLoading ? 'wait' : 'default' }} type="checkbox" key={item} id={item} name={item} value={item}
                  checked={checkedColors.includes(item)}
                  onChange={handleCheckboxColorsChange}></input>
                  <span key={item + 'span'} style={{ fontWeight: checkedColors.includes(item) ? 'bold' : 'normal' }}>{item} ( <span style={{ color: 'green' }}> {upArrowUnicode} {color_minus[item]['up']}</span>,  <span style={{ color: 'red' }}> {downArrowUnicode} {color_minus[item]['down']}</span>) </span>&nbsp;&nbsp;&nbsp;</>
              ))}
            <br></br>
            {color_fraction &&
              Object.keys(color_fraction).map(item => (

                <><input style={{ cursor: isLoading ? 'wait' : 'default' }} type="checkbox" key={item} id={item} name={item} value={item}
                  checked={checkedColors.includes(item)}
                  onChange={handleCheckboxColorsChange}></input>
                  <span key={item + 'span'} style={{ fontWeight: checkedColors.includes(item) ? 'bold' : 'normal' }}>{item} ( <span style={{ color: 'green' }}> {upArrowUnicode} {color_fraction[item]['up']}</span>,  <span style={{ color: 'red' }}> {downArrowUnicode} {color_fraction[item]['down']}</span>)</span> &nbsp;&nbsp;&nbsp;</>
              ))}
            <br></br>
            <><input style={{ cursor: isLoading ? 'wait' : 'default' }} type="button" id={"ALL"} name={"ALL"} value={"Download All Heatmaps"}
              onClick={handleAllDownload}></input>
            </>


          </div>

          <i>For new threshold settings, it takes time to generate a heatmap for these thresholds.</i><br></br>

        </form>

        <br></br>

      </div>
      <div className="collapsible-header" onClick={toggleVisibility_brainheatmap}>
        <span><b>Brain Heatmaps</b></span>
        <span className={`arrow ${isVisible_brainheatmap ? 'up' : 'down'}`}>
          {isVisible_brainheatmap ? '▲' : '▼'}
        </span>
      </div>

      <div className={`collapsible-content ${isVisible_brainheatmap ? 'open' : ''}`} style={{ 'borderStyle': 'solid', 'borderWidth': '2px', 'borderColor': 'black' }}>


        <TransformWrapper
          defaultScale={1}
          defaultPositionX={200}
          defaultPositionY={100}
        >

          {({ zoomIn, zoomOut, resetTransform, positionX, positionY, ...rest }) => (
            <>
              <Controls />

              <TransformComponent >
                <img
                  src={`data:image/jpeg;base64,${imageData}`}
                  //src="https://cdn.sstatic.net/Img/unified/sprites.svg?v=e5e58ae7df45"
                  width='100%'
                  alt="A brain heatmap will be shown here" />
              </TransformComponent>
            </>
          )}
        </TransformWrapper>
        <i>- You can use the mouse wheel to zoom in or out of the image.</i><br></br>
        <i>- Some regions has not been visualized that are not matched to <a target='_blank' href='https://www.sciencedirect.com/science/article/pii/S0092867420304025?via%3Dihub'>Allen Mouse Brain</a></i><br></br>

      </div>

      <div className="collapsible-header" onClick={toggleVisibility_significantregion}>
        <span><b>Regions shown in the brain heatmap</b></span>
        <span className={`arrow ${isVisible_significantregion ? 'up' : 'down'}`}>
          {isVisible_significantregion ? '▲' : '▼'}
        </span>
      </div>

      <div className={`collapsible-content ${isVisible_significantregion ? 'open' : ''}`} style={{ 'border-style': 'solid', 'border-width': '2px', 'border-color': 'black' }}>


        <>{significantRegions && <Table columns={columns} data={significantRegions} setSelectedRows={setSelectedSignificantRegionRows} />}</>
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
