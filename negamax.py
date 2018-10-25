def move_ties_game():
    return all([cell is not None for board in boards for row in board for cell in row])

def get_possible_moves():
    possible_moves = []
    for a,board in enumerate(boards[:1]):
        for b,row in enumerate(board):
            for c,cell in enumerate(row):
                if cell is None:
                    possible_moves.append((a,c,b))
    return possible_moves

import math
def negamax(previous_move, depth, alpha, beta, color):
    #print_boards(boards)
    #print(depth)
    
    if (move_ties_game()):
        return (0, previous_move)
        
    global computer_turn
        
    cross_wins = previous_move is not None and check_boards(previous_move,True)
    noughts_wins = previous_move is not None and check_boards(previous_move,False)
    if (cross_wins or noughts_wins):
        score = -1000/depth
        if (noughts_wins and not computer_turn):
            score = 1000/depth
        
        return (color*score, previous_move)
    
    value = (-math.inf,None)
    for move in get_possible_moves():
        
        boards[move[0]][move[2]][move[1]] = not computer_turn
        computer_turn = not computer_turn
        
        result = negamax(move, depth+1, -beta, -alpha, -color)
        result = (-result[0],result[1])
        value = max(value, result, key=lambda x: x[0])
        
        boards[move[0]][move[2]][move[1]] = None
        computer_turn = not computer_turn
        
        #alpha = max(alpha, value[0])
        #if alpha >= beta:
        #    break
    return value

def minimax(previous_move, depth, alpha, beta, human):
    if (move_ties_game()):
        return (0, previous_move)
        
    cross_wins = previous_move is not None and check_boards(previous_move,True)
    noughts_wins = previous_move is not None and check_boards(previous_move,False)
    if (cross_wins):
        print_boards(boards)
        if (human):
            score = 1000-depth if human_is_cross else -1000+depth
        else:
            score = 1000-depth if not human_is_cross else -1000+depth
        return (score,previous_move)
        
    if (noughts_wins):
        if (human):
            score = 1000-depth if not human_is_cross else -1000+depth
        else:
            score = 1000-depth if human_is_cross else -1000+depth
        return (score,previous_move)
        
    if (human):
        value = (-math.inf,None)
        for move in get_possible_moves():
            boards[move[0]][move[2]][move[1]] = human_is_cross

            result = minimax(move, depth+1, alpha, beta, False)
            value = max(value, result, key=lambda x: x[0])
            
            boards[move[0]][move[2]][move[1]] = None
        return value
    else:
        value = (math.inf,None)
        for move in get_possible_moves():
            boards[move[0]][move[2]][move[1]] = not human_is_cross

            result = minimax(move, depth+1, alpha, beta, True)
            value = min(value, result, key=lambda x: x[0])
            
            boards[move[0]][move[2]][move[1]] = None
        return value

def get_perfect_computer_move():
    return minimax(None, 0, -math.inf, math.inf, False)

def get_computer_move():
    pass
