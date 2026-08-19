import numpy as np

class RubikEnv:
    """
    A gym-like environment representing a 3x3x3 Rubik's Cube.
    Stickers mapping:
    Faces are ordered: Up (0), Down (1), Front (2), Back (3), Left (4), Right (5)
    Each face has a 3x3 grid.
    Colors are represented as integers:
    0: White (U), 1: Yellow (D), 2: Green (F), 3: Blue (B), 4: Orange (L), 5: Red (R)
    """
    def __init__(self):
        self.reset()
        
    def reset(self):
        # 6 faces, 3x3 per face
        self.state = np.zeros((6, 3, 3), dtype=np.int32)
        for face in range(6):
            self.state[face, :, :] = face
        return self.get_state_flat()

    def get_state_flat(self):
        return self.state.flatten()

    def is_solved(self):
        for face in range(6):
            if not np.all(self.state[face, :, :] == face):
                return False
        return True

    def step(self, move):
        """
        Executes a move. Returns: next_state, reward, done, info
        Moves list: 'U', "U'", 'D', "D'", 'F', "F'", 'B', "B'", 'L', "L'", 'R', "R'"
        """
        self._rotate_face_state(move)
        solved = self.is_solved()
        reward = 100.0 if solved else -1.0
        return self.get_state_flat(), reward, solved, {}

    def _rotate_face_state(self, move):
        # Helper mapping for clockwise rotation of a single face matrix
        def cw(face_idx):
            self.state[face_idx] = np.rot90(self.state[face_idx], -1)

        def ccw(face_idx):
            self.state[face_idx] = np.rot90(self.state[face_idx], 1)

        # Implementation of face changes (adjacent edges shift)
        if move == 'U':
            cw(0)
            # F, L, B, R top rows shift
            temp = self.state[2, 0, :].copy()
            self.state[2, 0, :] = self.state[5, 0, :]
            self.state[5, 0, :] = self.state[3, 0, :]
            self.state[3, 0, :] = self.state[4, 0, :]
            self.state[4, 0, :] = temp
        elif move == "U'":
            ccw(0)
            temp = self.state[2, 0, :].copy()
            self.state[2, 0, :] = self.state[4, 0, :]
            self.state[4, 0, :] = self.state[3, 0, :]
            self.state[3, 0, :] = self.state[5, 0, :]
            self.state[5, 0, :] = temp
        elif move == 'D':
            cw(1)
            # F, R, B, L bottom rows shift
            temp = self.state[2, 2, :].copy()
            self.state[2, 2, :] = self.state[4, 2, :]
            self.state[4, 2, :] = self.state[3, 2, :]
            self.state[3, 2, :] = self.state[5, 2, :]
            self.state[5, 2, :] = temp
        elif move == "D'":
            ccw(1)
            temp = self.state[2, 2, :].copy()
            self.state[2, 2, :] = self.state[5, 2, :]
            self.state[5, 2, :] = self.state[3, 2, :]
            self.state[3, 2, :] = self.state[4, 2, :]
            self.state[4, 2, :] = temp
        elif move == 'F':
            cw(2)
            # U bottom, R left, D top, L right shift
            temp = self.state[0, 2, :].copy()
            self.state[0, 2, :] = self.state[4, :, 2][::-1]
            self.state[4, :, 2] = self.state[1, 0, :]
            self.state[1, 0, :] = self.state[5, :, 0][::-1]
            self.state[5, :, 0] = temp
        elif move == "F'":
            ccw(2)
            temp = self.state[0, 2, :].copy()
            self.state[0, 2, :] = self.state[5, :, 0]
            self.state[5, :, 0] = self.state[1, 0, :][::-1]
            self.state[1, 0, :] = self.state[4, :, 2]
            self.state[4, :, 2] = temp[::-1]
        elif move == 'B':
            cw(3)
            # U top, L left, D bottom, R right shift
            temp = self.state[0, 0, :].copy()
            self.state[0, 0, :] = self.state[5, :, 2]
            self.state[5, :, 2] = self.state[1, 2, :][::-1]
            self.state[1, 2, :] = self.state[4, :, 0]
            self.state[4, :, 0] = temp[::-1]
        elif move == "B'":
            ccw(3)
            temp = self.state[0, 0, :].copy()
            self.state[0, 0, :] = self.state[4, :, 0][::-1]
            self.state[4, :, 0] = self.state[1, 2, :]
            self.state[1, 2, :] = self.state[5, :, 2][::-1]
            self.state[5, :, 2] = temp
        elif move == 'L':
            cw(4)
            # U left, F left, D left, B right shift
            temp = self.state[0, :, 0].copy()
            self.state[0, :, 0] = self.state[3, :, 2][::-1]
            self.state[3, :, 2] = self.state[1, :, 0][::-1]
            self.state[1, :, 0] = self.state[2, :, 0]
            self.state[2, :, 0] = temp
        elif move == "L'":
            ccw(4)
            temp = self.state[0, :, 0].copy()
            self.state[0, :, 0] = self.state[2, :, 0]
            self.state[2, :, 0] = self.state[1, :, 0]
            self.state[1, :, 0] = self.state[3, :, 2][::-1]
            self.state[3, :, 2] = temp[::-1]
        elif move == 'R':
            cw(5)
            # U right, B left, D right, F right shift
            temp = self.state[0, :, 2].copy()
            self.state[0, :, 2] = self.state[2, :, 2]
            self.state[2, :, 2] = self.state[1, :, 2]
            self.state[1, :, 2] = self.state[3, :, 0][::-1]
            self.state[3, :, 0] = temp[::-1]
        elif move == "R'":
            ccw(5)
            temp = self.state[0, :, 2].copy()
            self.state[0, :, 2] = self.state[3, :, 0][::-1]
            self.state[3, :, 0] = self.state[1, :, 2][::-1]
            self.state[1, :, 2] = self.state[2, :, 2]
            self.state[2, :, 2] = temp
