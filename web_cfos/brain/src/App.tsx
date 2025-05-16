import { useState, useEffect , useMemo } from 'react'
import { TransformWrapper, TransformComponent, useControls } from "react-zoom-pan-pinch";
import { useReactTable,getCoreRowModel, getPaginationRowModel ,createColumnHelper} from '@tanstack/react-table'
import Table, {Show} from './Test.tsx';
import axios from "axios";
import { saveAs } from 'file-saver';


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

    const [isLoading, setIsLoading] = useState(false);


  const [selectedFile, setSelectedFile] = useState(null);
  const [preprocessSummary, setPreprocessSummary] = useState('');
  const [postprocessSummary, setPostprocessSummary] = useState(0);
  const [imageData, setImageData] = useState(1);
  const [isSubmitting_add, setIsSubmitting_add] = useState(false);
  const [isSubmitting_analysis_list, setIsSubmitting_analysis_list] = useState(false);
  const [isSubmitting_analysis_both, setIsSubmitting_analysis_both] = useState(false);
  const [isFirstRender, setIsFirstRender] = useState(true); // Using useRef to track initial render
const [downloadLink, setDownloadLink] = useState('');
  const [analysisMode, setAnalysisMode] = useState(null);


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




  const handleGenerate = async (event) => {
    event.preventDefault();
    if(selectedProjects.length == 0)
    {

      alert("please select a data")
      return
    }

    setIsSubmitting_analysis_list(true)
    setIsSubmitting_analysis_both(true)
    setIsLoading(true);

    
    console.log(projects)
    console.log(selectedProjects[0])
    const formData = new FormData();
    formData.append('pvalue', pvalue)
    formData.append('fold_up', foldup)
    formData.append('fold_down', folddown)
    formData.append('analysisMode', analysisMode)
    formData.append('dataname', selectedProjects[0])


    try {
      const response = await fetch('/analysis', {
        method: 'POST',
        body: formData,
        //responseType: 'arraybuffer',
      });

      //const blob = new Blob([response.data], { type: 'application/zip' });
      //saveAs(blob, 'archive.zip');
      
      const data = await response.json();
      setPostprocessSummary(data.message);
      console.log(data)
      setImageData(data.image)
      //setSignificantRegions(data.df);
      setDownloadLink(data.zip)
      alert("please click the download button ")
    } catch (error) {
      console.error('업로드 실패', error);
    }
    finally {
          setIsSubmitting_analysis_list(false)
    setIsSubmitting_analysis_both(false)
        setIsLoading(false);


    }
  };
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
      alert("Successfully uploaded:" + data['message']);

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

    setPreprocessSummary('processing..');
    console.log('handleSelectItem')
    console.log(index)


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
      setPreprocessSummary(data['message']);
    } catch (error) {
      console.error('업로드 실패', error);

    }
    finally {


    }



  };

  const handleRemoveSelectedItems = async () => {

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
      //create a header group:
      columnHelper.group({
        id: "tv_show",
        header: () => <span>TV Show</span>,
        //now define all columns within this group
        columns: [
          columnHelper.accessor("show.name", {
            header: "Name",
            cell: (info) => info.getValue(),
          }),
          columnHelper.accessor("show.type", {
            header: "Type",
            cell: (info) => info.getValue(),
          }),
        ],
      }),
      //create another group:
      columnHelper.group({
        id: "details",
        header: () => <span> Details</span>,
        columns: [
          columnHelper.accessor("show.language", {
            header: "Language",
            cell: (info) => info.getValue(),
          }),
          columnHelper.accessor("show.genres", {
            header: "Genres",
            cell: (info) => info.getValue(),
          }),
          columnHelper.accessor("show.runtime", {
            header: "Runtime",
            cell: (info) => info.getValue(),
          }),
          columnHelper.accessor("show.status", {
            header: "Status",
            cell: (info) => info.getValue(),
          }),
        ],
      }),
    ],
    [],
  );
  const fetchDataTV = async () => {
    const result = await axios("https://api.tvmaze.com/search/shows?q=snow");
    console.log(result)
    setData(result.data);
  };
  useEffect(() => {
    fetchDataTV();
  }, []);
  return (

    <div style={{ cursor: isLoading ? 'wait' : 'default' }}>

      <table border='true'>
        <thead></thead>
        <tbody>
          <tr>
            <td width="80%"><h4>Select a data uploaded in the server </h4></td>
            <td rowSpan='2'>
              <b>Upload an Excel file</b>
              <div className={isSubmitting_add ? 'submitting' : ''}>

                <form onSubmit={handleAddData}>
                  <input type="file" id="myFileInput" onClick={onFileInputClick} onChange={handleFileChange} />
                  Data Name: <input type="text" id='new_data_name' defaultValue={newDataName} onChange={handleNewDataNameChange} />
                  <button type="submit" disabled={isSubmitting_add}>{isSubmitting_add ? 'Processing...(may take a few seconds)' : 'Add Data'}</button>


                </form>
              </div>
              <br></br>
              <button onClick={handleRemoveSelectedItems}>Remove Selected Data</button>



            </td>


          </tr>
          <tr>

            <td>


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

          </tr>
        </tbody>
      </table>




      <h3>Contents in the selected data</h3>

      <p>{preprocessSummary.replace("/\n/g", "<br />")}</p>
<h3>Significant Regions</h3>

      <form onSubmit={handleGenerate}>
        <table>
          <thead></thead>
          <tbody>
            <tr>
              <td>
                P-value : <input type="number" onChange={handlePvalueChange} name='pvalue' style={{ width: "50px" }} value={pvalue} />

              </td>
              <td>
                Fold EXP/VEH (up) : <input type="number" onChange={handleFoldupChange} name='fold_up' value={foldup} style={{ width: "50px" }} />

              </td>
              <td>
                Fold EXP/VEH (down) : <input type="number" onChange={handleFolddownChange} name='fold_down' value={folddown} style={{ width: "50px" }} />

              </td>

            </tr>

          </tbody>
        </table>
        <button type="submit" onClick={() => setAnalysisMode('list')} disabled={isSubmitting_analysis_list}>{isSubmitting_analysis_list ? 'Processing...(may take a few seconds)' : 'Region List Only'}</button> &nbsp;&nbsp;
        <button type="submit" onClick={() => setAnalysisMode('both')} disabled={isSubmitting_analysis_both}>{isSubmitting_analysis_both ? 'Processing...(may take a few minutes)' : 'Region List & Heatmap (may take a few miniutes)'}</button>
      </form>

<a href={downloadLink}  disabled="disabled">download</a>
<hr></hr>

      <h3>Brain heatmap</h3>
<i>Some regions has not been visualized that are not matched to Brain Atlas.</i><br></br>

      <br></br>





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
                alt="brain heatmap will be shown here" />
            </TransformComponent>
          </>
        )}
      </TransformWrapper>

    </div>

  );
}

export default App;
