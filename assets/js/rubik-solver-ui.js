let scene, camera, renderer, controls;
let cubeGroup;
let cubies = [];
let isAnimating = false;
let currentScramble = "";
let solveMovesQueue = [];
let isPlaybackPaused = false;

function init3D() {
  const container = document.getElementById('canvas-container');
  if (!container) return;
  const width = container.clientWidth;
  const height = container.clientHeight || width || 400;
  
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020617);
  
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
  camera.position.set(5, 5, 8);
  
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(width, height);
  container.appendChild(renderer.domElement);
  
  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.enableZoom = true;
  
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);
  
  const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.4);
  dirLight1.position.set(10, 15, 10);
  scene.add(dirLight1);
  
  const dirLight2 = new THREE.DirectionalLight(0xffffff, 0.2);
  dirLight2.position.set(-10, -15, -10);
  scene.add(dirLight2);
  
  createCube();
  
  const loader = document.getElementById('canvas-loader');
  if (loader) {
    loader.style.opacity = '0';
    setTimeout(() => loader.style.display = 'none', 300);
  }
  
  animate();
}

function createCube() {
  if (cubeGroup) scene.add(cubeGroup);
  cubeGroup = new THREE.Group();
  scene.add(cubeGroup);
  cubies = [];
  const size = 0.95;
  const geometry = new THREE.BoxGeometry(size, size, size);
  
  const faceColors = [
    window.RubikLogic.COLORS.R,
    window.RubikLogic.COLORS.L,
    window.RubikLogic.COLORS.U,
    window.RubikLogic.COLORS.D,
    window.RubikLogic.COLORS.F,
    window.RubikLogic.COLORS.B
  ];
  
  for (let x of window.RubikLogic.POSITIONS) {
    for (let y of window.RubikLogic.POSITIONS) {
      for (let z of window.RubikLogic.POSITIONS) {
        const mats = [];
        mats.push(new THREE.MeshBasicMaterial({ color: x === 1 ? faceColors[0] : window.RubikLogic.COLORS.K }));
        mats.push(new THREE.MeshBasicMaterial({ color: x === -1 ? faceColors[1] : window.RubikLogic.COLORS.K }));
        mats.push(new THREE.MeshBasicMaterial({ color: y === 1 ? faceColors[2] : window.RubikLogic.COLORS.K }));
        mats.push(new THREE.MeshBasicMaterial({ color: y === -1 ? faceColors[3] : window.RubikLogic.COLORS.K }));
        mats.push(new THREE.MeshBasicMaterial({ color: z === 1 ? faceColors[4] : window.RubikLogic.COLORS.K }));
        mats.push(new THREE.MeshBasicMaterial({ color: z === -1 ? faceColors[5] : window.RubikLogic.COLORS.K }));
        
        const mesh = new THREE.Mesh(geometry, mats);
        mesh.position.set(x, y, z);
        
        const edgeGeom = new THREE.EdgesGeometry(geometry);
        const line = new THREE.LineSegments(edgeGeom, new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 }));
        mesh.add(line);
        cubeGroup.add(mesh);
        cubies.push(mesh);
      }
    }
  }
}

function animate() {
  requestAnimationFrame(animate);
  if (controls) controls.update();
  if (renderer && scene && camera) renderer.render(scene, camera);
}

function rotateLayer(axis, targetVal, angle, duration) {
  return new Promise((resolve) => {
    const rotatingGroup = new THREE.Group();
    scene.add(rotatingGroup);
    
    const movingCubies = cubies.filter(c => {
      const posVal = Math.round(c.position[axis]);
      return posVal === targetVal;
    });
    
    movingCubies.forEach(c => {
      rotatingGroup.attach(c);
    });
    
    const startRot = rotatingGroup.rotation[axis];
    const targetRot = startRot + angle;
    const startTime = performance.now();
    
    function updateRotation(now) {
      const progress = Math.min((now - startTime) / duration, 1);
      rotatingGroup.rotation[axis] = startRot + (targetRot - startRot) * progress;
      if (progress < 1) {
        requestAnimationFrame(updateRotation);
      } else {
        movingCubies.forEach(c => {
          scene.attach(c);
          c.position.x = Math.round(c.position.x);
          c.position.y = Math.round(c.position.y);
          c.position.z = Math.round(c.position.z);
          c.rotation.x = Math.round(c.rotation.x / (Math.PI / 2)) * (Math.PI / 2);
          c.rotation.y = Math.round(c.rotation.y / (Math.PI / 2)) * (Math.PI / 2);
          c.rotation.z = Math.round(c.rotation.z / (Math.PI / 2)) * (Math.PI / 2);
          cubeGroup.attach(c);
        });
        scene.remove(rotatingGroup);
        resolve();
      }
    }
    requestAnimationFrame(updateRotation);
  });
}

async function performMove(moveName) {
  if (isAnimating) return;
  isAnimating = true;
  const moveDef = window.RubikLogic.MOVES[moveName];
  if (!moveDef) {
    isAnimating = false;
    return;
  }
  const speedSlider = document.getElementById('speed-slider');
  const duration = speedSlider ? parseInt(speedSlider.value) : 300;
  const angle = (moveDef.double ? Math.PI : Math.PI / 2) * moveDef.dir;
  await rotateLayer(moveDef.axis, moveDef.val, angle, duration);
  isAnimating = false;
}

function setupListeners() {
  const btnScramble = document.getElementById('btn-scramble');
  const btnReset = document.getElementById('btn-reset');
  const btnSolve = document.getElementById('btn-solve');
  const btnPlayPause = document.getElementById('btn-play-pause');
  const statusBox = document.getElementById('status-box');
  
  if (btnScramble) {
    btnScramble.addEventListener('click', async () => {
      if (isAnimating || solveMovesQueue.length > 0) return;
      const scramble = window.RubikLogic.generateScramble();
      currentScramble = scramble;
      if (statusBox) statusBox.innerHTML = `<span class="status-scrambled">Scramble sequence:</span><br>${scramble}`;
      const moves = scramble.split(' ');
      for (let m of moves) {
        await performMove(m);
      }
    });
  }
  
  if (btnReset) {
    btnReset.addEventListener('click', () => {
      if (isAnimating) return;
      solveMovesQueue = [];
      currentScramble = "";
      scene.remove(cubeGroup);
      createCube();
      if (statusBox) statusBox.innerHTML = `<span class="status-solved">Ready. Cube is Solved.</span>`;
    });
  }
  
  if (btnSolve) {
    btnSolve.addEventListener('click', async () => {
      if (isAnimating || solveMovesQueue.length > 0) return;
      if (!currentScramble) {
        if (statusBox) statusBox.innerHTML = `<span>Scramble the cube first!</span>`;
        return;
      }
      const inverseSolve = window.RubikLogic.getInverseSolve(currentScramble);
      solveMovesQueue = inverseSolve.split(' ');
      currentScramble = "";
      if (statusBox) statusBox.innerHTML = `<span class="status-solved">Solving using inverse algorithm...</span><br>Remaining: ${solveMovesQueue.join(' ')}`;
      playbackLoop();
    });
  }
  
  if (btnPlayPause) {
    btnPlayPause.addEventListener('click', () => {
      isPlaybackPaused = !isPlaybackPaused;
      btnPlayPause.innerText = isPlaybackPaused ? "▶️ Resume" : "⏸️ Pause";
      if (!isPlaybackPaused) {
        playbackLoop();
      }
    });
  }
}

async function playbackLoop() {
  if (isPlaybackPaused || solveMovesQueue.length === 0 || isAnimating) return;
  const currentMove = solveMovesQueue.shift();
  const statusBox = document.getElementById('status-box');
  if (statusBox) statusBox.innerHTML = `<span class="status-solved">Executing: ${currentMove}</span><br>Remaining: ${solveMovesQueue.join(' ')}`;
  await performMove(currentMove);
  if (solveMovesQueue.length === 0) {
    if (statusBox) statusBox.innerHTML = `<span class="status-solved">Solved! Double-checked matching.</span>`;
  } else {
    setTimeout(playbackLoop, 50);
  }
}

async function applyManualMove(move) {
  if (isAnimating || solveMovesQueue.length > 0) return;
  const statusBox = document.getElementById('status-box');
  if (statusBox) statusBox.innerHTML = `<span>Manual move: ${move}</span>`;
  await performMove(move);
}

window.applyManualMove = applyManualMove;

window.addEventListener('resize', () => {
  const container = document.getElementById('canvas-container');
  if (!container) return;
  const width = container.clientWidth;
  const height = container.clientHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
});

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    init3D();
    setupListeners();
  });
} else {
  init3D();
  setupListeners();
}
