def get_input(message,valid):
    print(message,end='')
    s = input().lower()
    while True:
        if (valid(s)):
            return s
        print("\nInvalid input")
        print(message,end='')
        s = input().lower()

class Game:
    def __init__(self,player1_first=True,player1_is_cross=True):
        self.player1_is_cross = player1_is_cross
        self.player1_move = player1_first

        self.size = 3
        self.boards = [[[None]*self.size for _ in range(self.size)] for _ in range(self.size)]

        self.move_counter = 0

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
        x,y = move[1],move[2]
        board = self.boards[move[0]]
        board_transposed = list(zip(*board))
        
        #Normal board
        column_win = all([cell==check for cell in board[y]])
        if (column_win):
            return True
        row_win = all([cell==check for cell in board_transposed[x]])
        if (row_win):
            return True
        
        #TODO: Diagonals will need to be adapted with size ever changes
        diagonal1_win = all([board[i][i]==check for i in range(self.size)])
        if (diagonal1_win):
            return True
        diagonal2_win = all([board[-i-1][i]==check for i in range(self.size)])
        if (diagonal2_win):
            return True
        
        #3D Board 
        up_win = all([self.boards[i][y][x]==check for i in range(self.size)])
        if (up_win):
            return True
        
        #3D Diagonals
        down_win = all([self.boards[i][i][x]==check for i in range(self.size)])
        if (down_win):
            return True
        right_win = all([self.boards[i][y][i]==check for i in range(self.size)])
        if (right_win):
            return True
        
        down_right_win = all([self.boards[i][i][i]==check for i in range(self.size)])
        if (down_right_win):
            return True
        down_left_win = all([self.boards[i][i][-i-1]==check for i in range(self.size)])
        if (down_left_win):
            return True

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

if __name__ == '__main__':
    message = "Do you want to be Crosses or Noughts [X/O]: "
    human_is_cross = get_input(message,lambda x: x in ['x','o']) == 'x'

    message = "Human starts or computer starts? [H/C]: "
    human_move = get_input(message,lambda x: x in ['h','c']) == 'h'

    game = Game(player1_first=human_move, player1_is_cross=human_is_cross)
    while True:
        game.print_boards()
        if (game.player1_move):
            move_raw = get_input("Enter move seperated by spaces (board x y) ", game.check_valid_move_string)
            move = list(map(int,move_raw.split()))
            board,x,y = move

            result = game.play(move)
        else:
            move_raw = get_input("IM ROBOT", game.check_valid_move_string)
            move = list(map(int,move_raw.split()))

            result = game.play(move)

        if (result == 0):
            game.print_boards()
            print("It's a draw!")
            break

        if (result == -1 or result == 1):
            game.print_boards()
            print("Player wins!" if result==1 else "Computer wins!")
            break

