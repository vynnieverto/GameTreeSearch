import argparse
import copy
import sys
import time
import pdb

cache = {} # you can use this to implement state caching

class State:
    # This class is used to represent a state.
    # board : a list of lists that represents the 8*8 board
    def __init__(self, board):

        self.board = board
        self.width = 8
        self.height = 8
        self.depth = 0

        self.r = 0
        self.b = 0
        self.r_king = 0
        self.b_king = 0

        self.is_terminal = False

    def display(self):
        for i in self.board:
            for j in i:
                print(j, end="")
            print("")
        print("")

def get_opp_char(player):
    if player in ['b', 'B']:
        return ['r', 'R']
    else:
        return ['b', 'B']

def get_next_turn(curr_turn):
    if curr_turn == 'r':
        return 'b'
    else:
        return 'r'

def read_from_file(filename):

    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    # board = []
    # r = []
    # b = []
    # r_king = []
    # b_king = []
    # for l in lines:
    #     temp = []
    #     for x in l.rstrip():
    #         tile = str(x)
    #         temp.append(tile)
    #         if x == 'r':
    #             r.append((len(board), len(temp) - 1))
    #         elif x == 'b':
    #             b.append((len(board), len(temp) - 1))
    #         elif x == 'R':
    #             r_king.append((len(board), len(temp) - 1))
    #         elif x == 'B':
    #             b_king.append((len(board), len(temp) - 1))

    #     board.append(temp)

    f.close()

    return board

def alpha_beta_search(state, curr_depth, alpha, beta, turn, max_depth):
    

    best_move = None
    move_ordering = []
    # breakpoint()
    successors = generate_successors(state, turn)
    # breakpoint()
    if state.depth == max_depth or state.is_terminal or curr_depth == max_depth:
        return evaluate(state, turn), None
    
    for s in successors:
        move_ordering.append((s, evaluate(s, turn)))
    


    if turn == 'r':
        val = -float('inf')
        move_ordering = sorted(move_ordering, key=lambda x: x[1], reverse=True)
    else:
        val = float('inf')
        move_ordering = sorted(move_ordering, key=lambda x: x[1])
    for s, v in move_ordering:
        # print(s.depth)
        # s.display()
        # breakpoint()
        # breakpoint()
        if s in cache:
            if cache[s][4] == turn and cache[s][1] <= curr_depth and alpha <= cache[s][2] and beta >= cache[s][3]:
                eval_val = cache[s][0]
            else:
                eval_val, next_move = alpha_beta_search(s, curr_depth + 1, alpha, beta, get_next_turn(turn), max_depth)
        else:
            eval_val, next_move = alpha_beta_search(s, curr_depth + 1, alpha, beta, get_next_turn(turn), max_depth)
        # breakpoint()
        # eval_val, next_move = alpha_beta_search(s, curr_depth + 1, alpha, beta, get_next_turn(turn), max_depth)
        if turn == 'r':
            if val < eval_val:
                val = eval_val
                best_move = s
            if val >= beta:
                return val, best_move
            alpha = max(alpha, val)

        if turn == 'b':
            if val > eval_val:
                val = eval_val
                best_move = s
            if val <= alpha:
                return val, best_move
            beta = min(beta, val)
        s.depth = curr_depth + 1
        cache[s] = (val, curr_depth, alpha, beta, turn)
    return val, best_move


def evaluate(state, turn):
    # This function is used to evaluate a state
    # state : the current state
    # turn : the player who is going to play next
    # return : the evaluation value
    # breakpoint()
    if state.is_terminal:
        if turn == 'b':
            return 10000 - state.depth
        else:
            return -10000 + state.depth
    
    else:
        return state.r +  2 * state.r_king - state.b -  2 * state.b_king


def generate_successors(state, turn):
    # This function generates all the possible successors of a state
    # state : the current state
    # turn : the player who is going to play next
    # return : a list of states
    # breakpoint()        
    successors = []
    if turn == 'r':
        check = set(['r', 'R'])
        up = -1
    else:
        check = set(['b', 'B'])
        up = 1

    pieces_to_move = []

    for i in range(8):
        for j in range(8):
            if state.board[i][j] in check:
                pieces_to_move.append((i, j))
                # breakpoint()
                if state.board[i][j].islower():
                    # breakpoint()
                    check_piece_take(state, i, j, up, successors, state.board, False)

                else:
                    # new_state = duplicate_state(state)
                    
                    # breakpoint()
                    check_piece_take(state, i, j, up, successors, state.board, True)
                    # check_piece_take(state, i, j, -up, successors, state.board)
                
                    
    if len(successors) == 0:
        for piece in pieces_to_move:
            if state.board[piece[0]][piece[1]].islower():
                check_piece_move(state, piece[0], piece[1], up, successors)
            else:
                check_piece_move(state, piece[0], piece[1], up, successors)
                check_piece_move(state, piece[0], piece[1], -up, successors)

    if len(successors) == 0:
        state.is_terminal = True
    return successors


def generate_new_board(old_board):
    new_board = []
    for i in range(8):
        temp = []
        for j in range(8):
            temp.append(old_board[i][j])
        new_board.append(temp)

    return new_board

def check_piece_move(state, i, j, up, successors):
    if check_valid_move(state.board, (i, j), (i + up, j - 1)):
        new_state = duplicate_state(state)
        new_board = new_state.board
        if i + up == 0 and state.board[i][j] == 'r':
            new_state.r_king += 1
            new_state.r -= 1
            new_board[i + up][j - 1] = 'R'

        elif i + up == 7 and state.board[i][j] == 'b':
            new_state.b_king += 1
            new_state.b -= 1
            new_board[i + up][j - 1] = 'B'
        else:
            new_board[i + up][j - 1] = new_board[i][j]
        
        new_board[i][j] = '.'
        new_state.depth = state.depth + 1
        successors.append(new_state)

    if check_valid_move(state.board, (i, j), (i + up, j + 1)):
        new_state = duplicate_state(state)
        new_board = new_state.board
        if i + up == 0 and state.board[i][j] == 'r':
            new_state.r_king += 1
            new_state.r -= 1
            new_board[i + up][j + 1] = 'R'

        elif i + up == 7 and state.board[i][j] == 'b':
            new_state.b_king += 1
            new_state.b -= 1
            new_state.board[i + up][j + 1] = 'B'
        else:
            new_state.board[i + up][j + 1] = new_state.board[i][j]
        
        new_state.board[i][j] = '.'
        new_state.depth = state.depth + 1
        successors.append(new_state)
        
def check_piece_take(state, i, j, up, successors, original_board, king):
    # breakpoint()
    enemy = get_opp_char(state.board[i][j])
    moved = False
    direction = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    for d in direction:
        # breakpoint()
        x, y = d
        if not in_board(i + y, j + x):
            if state.board != original_board and state not in successors:
                state.depth = state.depth + 1
                successors.append(state)
            continue

        if up == y:
            if state.board[i + y][j + x] in enemy and check_valid_move(state.board, (i, j), (i + 2 * y, j + 2 * x)):
                if state.board[i][j] == 'b' and i + 2 * y == 0:
                    new_state = apply_capture(state, i, j, i + 2 * y, j + 2 * x, i + y, j + x)
                    new_state.b_king += 1
                    new_state.b -= 1
                    
                    new_state.depth = state.depth + 1
                    successors.append(new_state)
                elif state.board[i][j] == 'r' and i + 2 * y == 7:
                    new_state = apply_capture(state, i, j, i + 2 * y, j + 2 * x, i + y, j + x)
                    new_state.r_king += 1
                    new_state.r -= 1
                    new_state.depth = state.depth + 1
                    successors.append(new_state)
                
                else:

                    new_state = apply_capture(state, i, j, i + 2 * y, j + 2 * x, i + y, j + x)

                    # if state.board[i][j] == 'b' or state.board[i][j] == 'B':
                    #     if state.board[i + y][j + x] == 'r':
                    #         state.r -= 1
                    #     else:
                    #         state.r_king -= 1
                    # else:
                    #     if state.board[i + y][j + x] == 'b':
                    #         state.b -= 1
                    #     else:
                    #         state.b_king -= 1
                    # state.board[i + 2 * y][j + 2 * x] = state.board[i][j]
                    # state.board[i][j] = '.'
                    # state.board[i + y][j + x] = '.'

                    check_piece_take(new_state, i + 2 * y, j + 2 * x, up, successors, original_board, king)
                    moved = True
            
            # else:
            #     if not king:
            #         if state.board != original_board and state not in successors:
            #             state.depth = state.depth + 1
            #             successors.append(state)
            #     else:
            #         pass

        else:
            if king:
                if state.board[i + y][j + x] in enemy and check_valid_move(state.board, (i, j), (i + 2 * y, j + 2 * x)):
                    new_state = apply_capture(state, i, j, i + 2 * y, j + 2 * x, i + y, j + x)
                    # if state.board[i][j] == 'b' or state.board[i][j] == 'B':
                    #     if state.board[i + y][j + x] == 'r':
                    #         state.r -= 1
                    #     else:
                    #         state.r_king -= 1
                    # else:
                    #     if state.board[i + y][j + x] == 'b':
                    #         state.b -= 1
                    #     else:
                    #         state.b_king -= 1
                    
                    # state.board[i + 2 * y][j + 2 * x] = state.board[i][j]
                    # state.board[i][j] = '.'
                    # state.board[i + y][j + x] = '.'
                    

                    check_piece_take(new_state, i + 2 * y, j + 2 * x, up, successors, original_board, king)
                    moved = True
                # else:
                #     if state.board != original_board and state not in successors and not moved:
                #         state.depth = state.depth + 1
                #         successors.append(state)


    if not moved and state.board != original_board and state not in successors:
        state.depth = state.depth + 1
        successors.append(state)



def apply_capture(state, i, j, ni, nj, ci, cj):
    new_state = duplicate_state(state)
    
    if new_state.board[ci][cj] == 'r':
        new_state.r -= 1
    elif new_state.board[ci][cj] == 'b':
        new_state.b -= 1
    elif new_state.board[ci][cj] == 'R':
        new_state.r_king -= 1
    elif new_state.board[ci][cj] == 'B':
        new_state.b_king -= 1

    new_state.board[ni][nj] = new_state.board[i][j]
    new_state.board[i][j] = '.'
    new_state.board[ci][cj] = '.'
    return new_state


def in_board(x, y):
    return 0 <= x < 8 and 0 <= y < 8           
            

def print_solution(solution):
    sys.stdout = open(args.outputfile, 'w')
    for s in solution:
        s.display()
        # print("\n")

    sys.stdout = sys.__stdout__

            

def duplicate_state(state):
    new_board = generate_new_board(state.board)
    new_state = State(new_board)
    new_state.r = state.r
    new_state.b = state.b
    new_state.r_king = state.r_king
    new_state.b_king = state.b_king
    new_state.is_terminal = state.is_terminal
    new_state.depth = state.depth
    # new_state = copy.deepcopy(state)
    return new_state

def check_valid_move(board, start, end):
    x2, y2 = end

    return 0 <= x2 < 8 and 0 <= y2 < 8 and board[x2][y2] == '.'

    # if x2 < 0 or x2 >= 8 or y2 < 0 or y2 >= 8:
    #     return False
    # elif board[x2][y2] != '.':
    #     return False
    # else: 
    #     return True
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    args = parser.parse_args()

    initial_board = read_from_file(args.inputfile)
    state = State(initial_board)

    for i in range(state.height):
        for j in range(state.width):
            if state.board[i][j] == 'r':
                state.r += 1
            elif state.board[i][j] == 'b':
                state.b += 1
            elif state.board[i][j] == 'R':
                state.r_king += 1
            elif state.board[i][j] == 'B':
                state.b_king += 1
    
    turn = 'r'
    ctr = 0
    print("Initial State")
    state.display()
    depth = 10
    solution = []
    solution.append(state)
    
    while True:
        # breakpoint()
        state.depth = 0
        eval, best_move = alpha_beta_search(state,0,  -100000, 100000, turn, depth)
        

        if best_move is None:
            break
        solution.append(best_move)
        state = best_move
        # state.display()
        # print(state.depth + len(solution) - 2) 
        turn = get_next_turn(turn)
        ctr += 1

    print_solution(solution)

    # print(ctr)
    # print("Final State")
    # state.display()
    # # breakpoint()
    # successors = generate_successors(state, turn)
    # for state in successors:
    #     state.display()
    #     print(state.r, state.b, state.r_king, state.b_king)
    #     print(state.depth)
    #     print("\n")



    # sys.stdout = open(args.outputfile, 'w')

    # sys.stdout = sys.__stdout__

