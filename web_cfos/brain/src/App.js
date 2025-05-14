import { useState, useEffect} from 'react'
import { TransformWrapper, TransformComponent, useControls } from "react-zoom-pan-pinch";

const Toolbox = {
  display: "flex",
  width: "100%",
  margin_bottom: "10px",
};

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

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };
  const handlePvalueChange = (event) => {
    console.log(event.target.value)
    setPvalue(event.target.value);
  };
  const handleFoldupChange = (event) => {
    setFoldup(event.target.value);
  };
  const handleFolddownChange = (event) => {
    setFolddown(event.target.value);
  };

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
    finally
    {
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
      formData.append('fold_down',  folddown)
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
        finally
    {
            setIsSubmitting_gen(false);

    }
  };
const Controls = () => {
  const { zoomIn, zoomOut, resetTransform } = useControls();

  return (
    <div  style={Toolbox}>
      <button onClick={() => zoomIn()}>+</button>
      <button onClick={() => zoomOut()}>-</button>
      <button onClick={() => resetTransform()}>Reset</button>
    </div>
  );
};

const [projects, setProjects] = useState([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/projects',{ method: 'POST'});
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const json = await response.json();
        setProjects(json.dirs);
      } catch (e) {
        console.log(e)
      }
    }
    fetchData();
  }, []);

  const [inputValue, setInputValue] = useState('');
  const [selectedProjects, setSelectedProjects] = useState([]);

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleAddItem = () => {
    if (inputValue.trim() !== '') {
      setProjects([...projects, inputValue]);
      setInputValue('');
    }
  };


  async function fetchData(index) {
  const response = await fetch('/load', {
    method: 'POST', // or 'GET', 'PUT', 'DELETE'
    headers: {
      'Content-Type': 'application/json',
      // Add any other headers as needed
    },
    body: JSON.stringify({ "dirname": projects[index] }), // For POST/PUT requests
  });

  /*
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }*/

  const data = await response.json();


  
  return data;
}


  async function   handleSelectItem (index) {

    console.log(selectedProjects)


    if (selectedProjects.includes(index)) {
      setSelectedProjects(selectedProjects.filter((i) => i !== index));


    } else {

      setSelectedProjects([...selectedProjects, index]);
      //setSelectedProjects(index);
      const data = await fetchData(index)
      console.log(data)
          setPreprocessSummary(data['message']);
    }
  }

  const handleRemoveSelectedItems = () => {
     setProjects(projects.filter((_, index) => !selectedProjects.includes(index)));
     setSelectedProjects([]);
  };

  
  return (

      <div>

<table border='true'>
  <thead></thead>
  <tbody>
  <tr>
      <td width="80%"><h4>Data available in the server </h4></td>
<td rowSpan='2'>          
  
  <div className={isSubmitting_add ? 'submitting' : ''}>

            <form onSubmit={handleSubmit}>
              New data<br></br>
              <input type="file" id="myFileInput"  onChange={handleFileChange}  />
              name: <input type="text" value={inputValue} onChange={handleInputChange} />
              <button type="submit"  disabled={isSubmitting_add}>{isSubmitting_add ? 'Processing...' : 'Add Data'}</button>
      

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
            key={index}
            onClick={() => handleSelectItem(index)}
            style={{
              backgroundColor: selectedProjects.includes(index)
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
              P-value : <input type="number"  onChange={handlePvalueChange}  name='pvalue'  style={{ width: "50px" }} value={pvalue} />  

                    </td>
                    <td>
                                    Fold change(up) : <input type="number"  onChange={handleFoldupChange}  name='fold_up' value={foldup}   style={{ width: "50px" }}/> 

                    </td>
                    <td>
                                    Fold change(down) : <input type="number"  onChange={handleFolddownChange}  name='fold_down' value={folddown}   style={{ width: "50px" }}/> 

                    </td>

                  </tr>

                </tbody>
              </table>
              <button type="submit"  disabled={isSubmitting_gen}>{isSubmitting_gen ? 'Processing...' : 'Generate'}</button>
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
