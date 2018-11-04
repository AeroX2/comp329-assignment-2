import random

def get_input(message,valid):
    print(message,end='')
    s = input().lower()
    while True:
        if (valid(s)):
            return s
        print("Invalid input")
        print(message,end='')
        s = input().lower()

class Game:
    def __init__(self,player1_first=True,player1_is_cross=True):
        import operator

        self.player1_is_cross = player1_is_cross
        self.player1_move = player1_first

        self.size = 3
        self.move_counter = 0
        self.boards = [[[None]*self.size for _ in range(self.size)] for _ in range(self.size)]

    def print_boards(self):
        for row in range(self.size):
            string = ""
            for board in self.boards:
                v = board[row]
                def check(x):
                    if x is None:
                        return " "
                    elif x:
                        return "X" if self.player1_is_cross else "O"
                    return "O" if self.player1_is_cross else "X"
                v = map(check,v)
                string += "|" + "|".join(v) + "|   "    
            print(string.strip())

    def check_valid_move(self,m):
        try:
            a,b,c = m
            if ((a<0 or a>=self.size) or 
                (b<0 or b>=self.size) or 
                (c<0 or c>=self.size)):
                return False
            return self.boards[a][c][b] is None
        except:
            return False

    def check_valid_move_string(self,s):
        try:
            a,b,c = map(int,s.split())
            if ((a<0 or a>=self.size) or 
                (b<0 or b>=self.size) or 
                (c<0 or c>=self.size)):
                return False
            return self.boards[a][c][b] is None
        except:
            return False
        
    def check_boards(self, move, check):
        for direction in [(0,0,1),(0,1,0),(0,1,1),(1,0,0),(1,0,1),
                          (1,1,0),(1,1,1),(0,-1,1),(-1,0,1),(-1,1,0),
                          (-1,1,1),(1,-1,1),(1,1,-1)]:

            total = 1 if self.boards[move[0]][move[2]][move[1]] == check else 0
            for _ in range(2):
                new_pos = tuple(map(sum,zip(move,direction)))
                while True:
                    if (any([x<0 or x>=self.size for x in new_pos])):
                        break

                    new_space = self.boards[new_pos[0]][new_pos[2]][new_pos[1]]
                    if (new_space != check):
                        break

                    total += 1
                    new_pos = tuple(map(sum,zip(new_pos,direction)))
                direction = tuple(map(lambda x: -x,direction))

            if (total >= self.size):
                return True
        return False

    def move_ends_game(self,move):
        return self.check_boards(move,True) or self.check_boards(move,False)

    def move_ties_game(self):
        return not any([cell is None for board in self.boards for row in board for cell in row])

    def play(self, move):
        if (not self.check_valid_move(move)):
            return -2

        self.boards[move[0]][move[2]][move[1]] = self.player1_move

        self.move_counter += 1
        if (self.move_counter >= self.size**3):
            return 0

        if (self.move_ends_game(move)):
            return 1 if self.player1_move else -1

        self.player1_move = not self.player1_move

        return None

    def get_possible_moves(self,check):
        possible_moves = []
        for a,board in enumerate(self.boards):
            for b,row in enumerate(board):
                for c,cell in enumerate(row):
                    if cell == check:
                        possible_moves.append((a,c,b))
        return possible_moves

    def check_directions(self, move, check):
        valid_moves = []
        for direction in [(0,0,1),(0,1,0),(0,1,1),(1,0,0),(1,0,1),
                          (1,1,0),(1,1,1),(0,-1,1),(-1,0,1),(-1,1,0),
                          (-1,1,1),(1,-1,1),(1,1,-1)]:

            line_count = 0
            valid_moves.append([])
            total = 1 if self.boards[move[0]][move[2]][move[1]] == check else 0

            for _ in range(2):
                new_pos = tuple(map(sum,zip(move,direction)))
                while True:
                    line_count += 1
                    if (any([x<0 or x>=self.size for x in new_pos])):
                        break

                    new_space = self.boards[new_pos[0]][new_pos[2]][new_pos[1]]
                    if (new_space == (not check)): 
                        break

                    if (new_space == check):
                        total += 1

                    if (new_space is None):
                        valid_moves[-1].append((total,new_pos))

                    new_pos = tuple(map(sum,zip(new_pos,direction)))
                direction = tuple(map(lambda x: -x,direction))

            if (line_count < 3):
                valid_moves.pop()

        return [j for sub in valid_moves for j in sub]

    def get_computer_move(self):
        computer_valid_moves = None
        for move in self.get_possible_moves(self.player1_move):
            valid_moves = self.check_directions(move, self.player1_move)
            for valid_move in valid_moves:
                if (valid_move[0] >= self.size-1): #If we can win do it
                    #print("Winning move")
                    return valid_move[1]
            if (len(valid_moves) > 0):
                computer_valid_moves = valid_moves

        for move in self.get_possible_moves(not self.player1_move):
            valid_moves = self.check_directions(move, not self.player1_move)
            for valid_move in valid_moves:
                if (valid_move[0] >= self.size-1): #If the player can win block it
                    #print("Player block")
                    return valid_move[1]

        #If we can't win and the player can't win then make our best move
        if (computer_valid_moves is not None):
            #print("Valid")
            move = random.choice(computer_valid_moves)
            return move[1]
        
        #print("Random")
        #If we have gone through all the moves then make a random move
        valid_moves = self.get_possible_moves(None)
        return random.choice(valid_moves)

if __name__ == '__main__':
    message = "Do you want to be Crosses or Noughts [X/O]: "
    human_is_cross = get_input(message,lambda x: x in ['x','o']) == 'x'

    message = "Human starts or computer starts? [H/C]: "
    human_move = get_input(message,lambda x: x in ['h','c']) == 'h'

    game = Game(player1_first=human_move, player1_is_cross=human_is_cross)
    while True:
        if (game.player1_move):
            game.print_boards()
            move_raw = get_input("Enter move seperated by spaces (board x y) ", game.check_valid_move_string)
            move = list(map(int,move_raw.split()))
            board,x,y = move

            result = game.play(move)
        else:
            move = game.get_computer_move()
            result = game.play(move)

        if (result == 0):
            game.print_boards()
            print("It's a draw!")
            break

        if (result == -1 or result == 1):
            game.print_boards()
            print("Player wins!" if result==1 else "Computer wins!")
            break

