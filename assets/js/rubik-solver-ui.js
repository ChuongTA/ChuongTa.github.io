let scene, camera, renderer, controls;
let cubeGroup;
let cubies = [];
let isAnimating = false;
let currentScramble = "";
let solveMovesQueue = [];
let isPlaybackPaused = false;

const TRANSLATIONS = {
  en: {
    scrambleSeq: "Scramble sequence:",
    readySolved: "Ready. Cube is Solved.",
    scrambleFirst: "Scramble the cube first!",
    solvingInverse: "Solving using inverse algorithm...",
    remaining: "Remaining:",
    resume: "▶️ Resume",
    pause: "⏸️ Pause",
    executing: "Executing:",
    solvedDouble: "Solved! Double-checked matching.",
    manualMove: "Manual move:",
    scrambleBtn: "🎲 Scramble",
    solveBtn: "✨ Solve"
  },
  vi: {
    scrambleSeq: "Chuỗi trộn:",
    readySolved: "Sẵn sàng. Rubik đã được giải.",
    scrambleFirst: "Xáo trộn khối rubik trước!",
    solvingInverse: "Đang giải bằng thuật toán nghịch đảo...",
    remaining: "Còn lại:",
    resume: "▶️ Tiếp tục",
    pause: "⏸️ Tạm dừng",
    executing: "Đang thực hiện:",
    solvedDouble: "Giải xong! Đã đối chiếu hoàn tất.",
    manualMove: "Xoay thủ công:",
    scrambleBtn: "🎲 Xáo Trộn",
    solveBtn: "✨ Giải Rubik"
  }
};

function getTxt(key) {
  const lang = window.currentLanguage || 'en';
  return TRANSLATIONS[lang][key] || TRANSLATIONS['en'][key];
}

function updateSolverUI() {
  const btnPlayPause = document.getElementById('btn-play-pause');
  if (btnPlayPause) {
    btnPlayPause.innerText = isPlaybackPaused ? getTxt('resume') : getTxt('pause');
  }
  
  const statusBox = document.getElementById('status-box');
  if (statusBox) {
    // Refresh text of active status dynamically based on current queue or scramble
    if (solveMovesQueue.length > 0) {
      const activeMove = window.activePlaybackMove || "";
      if (activeMove) {
        statusBox.innerHTML = `<span class="status-solved">${getTxt('executing')} ${activeMove}</span><br>${getTxt('remaining')} ${solveMovesQueue.join(' ')}`;
      } else {
        statusBox.innerHTML = `<span class="status-solved">${getTxt('solvingInverse')}</span><br>${getTxt('remaining')} ${solveMovesQueue.join(' ')}`;
      }
    } else if (currentScramble) {
      statusBox.innerHTML = `<span class="status-scrambled">${getTxt('scrambleSeq')}</span><br>${currentScramble}`;
    } else if (window.isCubeCurrentlySolved) {
      statusBox.innerHTML = `<span class="status-solved">${getTxt('readySolved')}</span>`;
    }
  }
}

window.updateSolverUI = updateSolverUI;

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
  window.isCubeCurrentlySolved = true;
  
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

async function rotateLayer(axis, targetVal, angle, duration) {
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
      window.isCubeCurrentlySolved = false;
      if (statusBox) statusBox.innerHTML = `<span class="status-scrambled">${getTxt('scrambleSeq')}</span><br>${scramble}`;
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
      window.activePlaybackMove = "";
      currentScramble = "";
      window.isCubeCurrentlySolved = true;
      scene.remove(cubeGroup);
      createCube();
      if (statusBox) statusBox.innerHTML = `<span class="status-solved">${getTxt('readySolved')}</span>`;
    });
  }
  
  if (btnSolve) {
    btnSolve.addEventListener('click', async () => {
      if (isAnimating || solveMovesQueue.length > 0) return;
      if (!currentScramble) {
        if (statusBox) statusBox.innerHTML = `<span>${getTxt('scrambleFirst')}</span>`;
        return;
      }
      const inverseSolve = window.RubikLogic.getInverseSolve(currentScramble);
      solveMovesQueue = inverseSolve.split(' ');
      currentScramble = "";
      window.isCubeCurrentlySolved = false;
      if (statusBox) statusBox.innerHTML = `<span class="status-solved">${getTxt('solvingInverse')}</span><br>${getTxt('remaining')} ${solveMovesQueue.join(' ')}`;
      playbackLoop();
    });
  }
  
  if (btnPlayPause) {
    btnPlayPause.addEventListener('click', () => {
      isPlaybackPaused = !isPlaybackPaused;
      btnPlayPause.innerText = isPlaybackPaused ? getTxt('resume') : getTxt('pause');
      if (!isPlaybackPaused) {
        playbackLoop();
      }
    });
  }
}

async function playbackLoop() {
  if (isPlaybackPaused || solveMovesQueue.length === 0 || isAnimating) return;
  const currentMove = solveMovesQueue.shift();
  window.activePlaybackMove = currentMove;
  const statusBox = document.getElementById('status-box');
  if (statusBox) statusBox.innerHTML = `<span class="status-solved">${getTxt('executing')} ${currentMove}</span><br>${getTxt('remaining')} ${solveMovesQueue.join(' ')}`;
  await performMove(currentMove);
  if (solveMovesQueue.length === 0) {
    window.isCubeCurrentlySolved = true;
    window.activePlaybackMove = "";
    if (statusBox) statusBox.innerHTML = `<span class="status-solved">${getTxt('solvedDouble')}</span>`;
  } else {
    setTimeout(playbackLoop, 50);
  }
}

async function applyManualMove(move) {
  if (isAnimating || solveMovesQueue.length > 0) return;
  window.isCubeCurrentlySolved = false;
  const statusBox = document.getElementById('status-box');
  if (statusBox) statusBox.innerHTML = `<span>${getTxt('manualMove')} ${move}</span>`;
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
