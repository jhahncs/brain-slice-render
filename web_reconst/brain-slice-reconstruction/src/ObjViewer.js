import React, { useEffect, useMemo, Suspense, useRef } from 'react';
import { Canvas, useLoader, useThree } from '@react-three/fiber';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';
import { OrbitControls, Html } from '@react-three/drei'; // Optional: for interactive camera control
import { PointsNodeMaterial, Points } from '@react-three/fiber'
import * as THREE from 'three'



const sharedCamera = new THREE.PerspectiveCamera(25, 1, 0.01, 1000)
sharedCamera.position.set(2, 2, 2)

function SharedControls() {
  const controlsRef = useRef()
  const { camera, gl } = useThree()

  // Assign the shared camera to this canvas
  useEffect(() => {
    camera.position.copy(sharedCamera.position)
    camera.rotation.copy(sharedCamera.rotation)
    camera.updateProjectionMatrix()

    // Sync orbit controls between canvases
    const updateCamera = () => {
      sharedCamera.position.copy(camera.position)
      sharedCamera.rotation.copy(camera.rotation)
    }

    gl.domElement.addEventListener('pointermove', updateCamera)
    gl.domElement.addEventListener('wheel', updateCamera)

    return () => {
      gl.domElement.removeEventListener('pointermove', updateCamera)
      gl.domElement.removeEventListener('wheel', updateCamera)
    }
  }, [camera, gl])

  return <OrbitControls ref={controlsRef} target={[0, 0, 0]} />
}
function ObjModel({ modelPath, color}) {
    
    const obj = useLoader(OBJLoader, modelPath);
    //const color = 'hotpink'
    //console.log(modelPath,color)
    const size = 0.01
    const pointCloud = useMemo(() => {
        const positions = []

        obj.traverse((child) => {
            if (child.geometry?.attributes?.position) {
                const posAttr = child.geometry.getAttribute('position')
                for (let i = 0; i < posAttr.count; i++) {
                    positions.push(posAttr.getX(i), posAttr.getY(i), posAttr.getZ(i))
                }
            }
        })
        const geometry = new THREE.BufferGeometry()
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))

        const material = new THREE.PointsMaterial({ color, size })
        return new THREE.Points(geometry, material)
    }, [obj, color, size])

    return <primitive object={pointCloud} scale={0.5} />; // Adjust scale as needed
}

export default function ObjViewer({ objFilePath_list }) {
    return (
        <Canvas camera={sharedCamera}>
            <ambientLight intensity={0.9} />
            <pointLight position={[5, 5, 5]} />
            <Suspense fallback={          <Html center>
            <div style={{ color: 'red', fontSize: '24px', textAlign: 'center' }}>
              Loading 3D content...
            </div>
          </Html>}>


                {objFilePath_list &&
                    ( Object.keys(objFilePath_list).map((item) => (
                        <ObjModel modelPath={item}  color={objFilePath_list[item]} />
                    )
                    ))

                }



            </Suspense>
            <SharedControls/>
            
        </Canvas>
    );
}

//<OrbitControls /> {/* Optional: allows camera interaction */}