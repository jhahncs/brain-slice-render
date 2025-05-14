import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
const scene = new THREE.Scene() 
//scene.background = new THREE.Color(0x000000) // 빨간 배경색 0xff0000 ,초록색 0x00ff00
const camera = new THREE.PerspectiveCamera( //원근 카메라PerspectiveCamera: 원근깊이가 있는 카메라입니다. Frustum 형태가 잘린 피라미드처럼 보입니다.
    75,//1번째 인자= 시야각Field of view
   1,//window.innerWidth/ window.innerHeight, //캠퍼스 크기를 바꾸려면 횡종비 업데이트와 카메라도 일치시키기위해여기도 조정이 필요함
   //2번째 인자= 종횡비
   0.1,
   //3번째 인자 Near and far: 카메라가 얼마나 멀리까지 볼 수 있는지, 그리고 얼마나 가까이에 있는 물체까지 볼 수 있는지를 결정해주는 인자
    10
)
const camera2 = new THREE.OrthographicCamera( //직교 카메라 :평평하게 보입니다.
   -2,2,2,-2
)

const camera3 = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10)
const camera4 = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10)

camera.position.z = 2
camera2.position.y = 1 // 카메라가 위에서 아래로 000위치에 있는 3d 정육각형을 바라봄
camera2.lookAt(new THREE.Vector3(0, 0, 0))
camera3.position.z = 1
camera4.position.x = 1
camera4.lookAt(new THREE.Vector3(0, 0, 0))

const canvas1 = document.getElementById("c1") as HTMLCanvasElement
const canvas2 = document.getElementById("c2") as HTMLCanvasElement
const canvas3 = document.getElementById("c3") as HTMLCanvasElement //html 파일내 아이디 c3 인 캠퍼스와 연결
const canvas4 = document.getElementById("c4") as HTMLCanvasElement

const renderer1 = new THREE.WebGLRenderer({canvas:canvas1})
renderer1.setSize(200, 200) 
const renderer2 = new THREE.WebGLRenderer({canvas:canvas2})
renderer2.setSize(200, 200) 
const renderer3 = new THREE.WebGLRenderer({canvas:canvas3})
renderer3.setSize(200, 200) 
const renderer4 = new THREE.WebGLRenderer({canvas:canvas4})
renderer4.setSize(200, 200) 

//const renderer = new THREE.WebGLRenderer()
//renderer.setSize(window.innerWidth, window.innerHeight) //캠퍼스의 크기를 창의 높이와 크기로 지정


//document.body.appendChild(renderer1.domElement) // 자동 html 파일에 <canvas> 태그 생성

new OrbitControls(camera, renderer1.domElement) //OrbitControls= 마우스로 객체와 상호작용(줌인/아웃,오른쪽마우스클릭+드래그 등)


const geometry = new THREE.BoxGeometry()
const material = new THREE.MeshBasicMaterial({
    color: 0x00ff00,
    wireframe: true,
})

const cube = new THREE.Mesh(geometry, material)
scene.add(cube)

// window.addEventListener('resize', onWindowResize, false) //브라우저창에 맞게 화면 조절
// function onWindowResize() {   //29~ 35줄을 주석처리하면  새로고침이후 브라우저창을 조절해도 브라우저창에 맞게 캠퍼스가 조절하지 않고 고정된다.
//     camera.aspect = window.innerWidth / window.innerHeight  
//     camera.updateProjectionMatrix()
//     renderer.setSize(window.innerWidth, window.innerHeight)
//     render()
// }

function animate() {
    requestAnimationFrame(animate)
 
    cube.rotation.x += 0.01  // x 축으로 회전
     cube.rotation.y += 0.01 // x 축으로 회전

    render()
}

function render() {
    renderer1.render(scene, camera)
    renderer2.render(scene, camera2)
    renderer3.render(scene, camera3) //주석처리하면  화면이 안보입니다.
    renderer4.render(scene, camera4)
}

animate()