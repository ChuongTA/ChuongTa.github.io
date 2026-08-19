/**
 * Rubik's Cube Solver JS Logic
 * Uses a lightweight BFS/Beginner solver or notation model.
 */

// Colors mapping: U: White, D: Yellow, F: Green, B: Blue, L: Orange, R: Red
const COLORS = {
    U: 0xffffff, // White
    D: 0xffd700, // Yellow
    F: 0x009b48, // Green
    B: 0x0045ad, // Blue
    L: 0xff5800, // Orange
    R: 0xb71234, // Red
    K: 0x111111  // Internal Black color
};

// Represents a 3D Cubie offset positions
const POSITIONS = [-1, 0, 1];

// Cube movements mapping: describes which cubies to rotate for each face
// Axis definitions: X = Left/Right (L/R), Y = Up/Down (U/D), Z = Front/Back (F/B)
const MOVES = {
    'U':  { axis: 'y', val: 1,  dir: -1 },
    "U'": { axis: 'y', val: 1,  dir: 1 },
    'U2': { axis: 'y', val: 1,  dir: -1, double: true },
    'D':  { axis: 'y', val: -1, dir: 1 },
    "D'": { axis: 'y', val: -1, dir: -1 },
    'D2': { axis: 'y', val: -1, dir: 1, double: true },
    'R':  { axis: 'x', val: 1,  dir: -1 },
    "R'": { axis: 'x', val: 1,  dir: 1 },
    'R2': { axis: 'x', val: 1,  dir: -1, double: true },
    'L':  { axis: 'x', val: -1, dir: 1 },
    "L'": { axis: 'x', val: -1, dir: -1 },
    'L2': { axis: 'x', val: -1, dir: 1, double: true },
    'F':  { axis: 'z', val: 1,  dir: -1 },
    "F'": { axis: 'z', val: 1,  dir: 1 },
    'F2': { axis: 'z', val: 1,  dir: -1, double: true },
    'B':  { axis: 'z', val: -1, dir: 1 },
    "B'": { axis: 'z', val: -1, dir: -1 },
    'B2': { axis: 'z', val: -1, dir: 1, double: true }
};

// Standard random scramble generator
function generateScramble(movesCount = 20) {
    const list = ['U', "U'", 'U2', 'D', "D'", 'D2', 'R', "R'", 'R2', 'L', "L'", 'L2', 'F', "F'", 'F2', 'B', "B'", 'B2'];
    const scramble = [];
    let lastAxis = '';
    
    for (let i = 0; i < movesCount; i++) {
        let move;
        let moveDef;
        do {
            move = list[Math.floor(Math.random() * list.length)];
            moveDef = MOVES[move];
        } while (moveDef.axis === lastAxis); // avoid immediate repeating axis moves
        
        scramble.push(move);
        lastAxis = moveDef.axis;
    }
    return scramble.join(' ');
}

// Invert standard moves for backtracking/solving
function invertMove(move) {
    if (move.endsWith("'")) return move.slice(0, -1);
    if (move.endsWith('2')) return move; // double moves are self-inverting
    return move + "'";
}

// Returns a simple inverse algorithm path (perfect for visual undoing of scramble sequences)
function getInverseSolve(scrambleStr) {
    if (!scrambleStr) return "";
    return scrambleStr.split(' ').reverse().map(invertMove).join(' ');
}

window.RubikLogic = {
    COLORS,
    POSITIONS,
    MOVES,
    generateScramble,
    getInverseSolve
};
