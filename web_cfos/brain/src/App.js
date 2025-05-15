import { useState, useEffect } from 'react'
import { TransformWrapper, TransformComponent, useControls } from "react-zoom-pan-pinch";

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

  const [selectedFile, setSelectedFile] = useState(null);
  const [preprocessSummary, setPreprocessSummary] = useState('');
  const [postprocessSummary, setPostprocessSummary] = useState(0);
  const [imageData, setImageData] = useState(1);
  const [isSubmitting_add, setIsSubmitting_add] = useState(false);
  const [isSubmitting_gen, setIsSubmitting_gen] = useState(false);
  const [isFirstRender, setIsFirstRender] = useState(true); // Using useRef to track initial render

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


  const handleGenerate = async (event) => {
    event.preventDefault();
    setIsSubmitting_gen(true);

    console.log(projects)
    console.log(selectedProjects)
    const formData = new FormData();
    formData.append('pvalue', pvalue)
    formData.append('fold_up', foldup)
    formData.append('fold_down', folddown)
    formData.append('dir', projects[selectedProjects[0]])


    try {
      const response = await fetch('/analysis', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setPostprocessSummary(data.message);

      setImageData(data.image)

    } catch (error) {
      console.error('업로드 실패', error);
    }
    finally {
      setIsSubmitting_gen(false);

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


  return (

    <div>

      <table border='true'>
        <thead></thead>
        <tbody>
          <tr>
            <td width="80%"><h4>Data available in the server </h4>(reflesh this page if data is not shown as you expected)</td>
            <td rowSpan='2'>

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




      <h4>Contents in the selected data</h4>

      <p>{preprocessSummary.replace("/\n/g", "<br />")}</p>




      <h3>Brain heatmap</h3>

      <form onSubmit={handleGenerate}>
        <table>
          <thead></thead>
          <tbody>
            <tr>
              <td>
                P-value : <input type="number" onChange={handlePvalueChange} name='pvalue' style={{ width: "50px" }} value={pvalue} />

              </td>
              <td>
                Fold change(up) : <input type="number" onChange={handleFoldupChange} name='fold_up' value={foldup} style={{ width: "50px" }} />

              </td>
              <td>
                Fold change(down) : <input type="number" onChange={handleFolddownChange} name='fold_down' value={folddown} style={{ width: "50px" }} />

              </td>

            </tr>

          </tbody>
        </table>
        <button type="submit" disabled={isSubmitting_gen}>{isSubmitting_gen ? 'Processing...' : 'Generate'}</button>
      </form>
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
