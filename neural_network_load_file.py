import os
import random
import numpy as np
from tictactoe import Game,get_input
from deap import algorithms, base, creator, tools
from sklearn.neural_network import MLPRegressor

class MLPClassifierOverride(MLPRegressor):
    def init_weights(self, individual):
        self.count = 0
        self.individual = individual

    # Nah
    def _fit_stochastic(self, X, y, activations, deltas, coef_grads,
                    intercept_grads, layer_units, incremental):
        pass
    
    # Overriding _init_coef method
    def _init_coef(self, fan_in, fan_out):
        if self.activation == 'logistic':
            init_bound = np.sqrt(2. / (fan_in + fan_out))
        elif self.activation in ('identity', 'tanh', 'relu'):
            init_bound = np.sqrt(6. / (fan_in + fan_out))
        else:
            raise ValueError("Unknown activation function %s" %
                             self.activation)

        start = self.count
        end = start + fan_in*fan_out
        coef_init = np.reshape(self.individual[start:end], (fan_in, fan_out))

        start = end
        end = start + fan_out
        intercept_init = self.individual[start:end]

        self.count += fan_in*fan_out
        self.count += fan_out

        #coef_init = self.coefs
        #intercept_init = self.intercepts

        #coef_init = self._random_state.uniform(-init_bound, init_bound,
        #                                       (fan_in, fan_out))
        #intercept_init = self._random_state.uniform(-init_bound, init_bound,
        #                                            fan_out)

        return coef_init, intercept_init

while True:
    print("Input filename: ", end='')
    file_name = input()
    if (os.path.exists(file_name+".npy")):
        break
    print("Invalid file")
best = np.load(file_name+".npy")

mf = np.vectorize(lambda x: 0.5 if x is None else float(x))
mlp = MLPClassifierOverride()
mlp.init_weights(best)
mlp.fit([[0.0]*3*3*3,[0.0]*3*3*3], [[0.1]*3*3*3,[0.1]*3*3*3])

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
        translate = mf(np.array(game.boards).flatten())
        moves = mlp.predict([translate])[0]
        moves = [z[1] for z in sorted([(x,i) for i,x in enumerate(moves)])]

        #print("Wat",moves)
        for move in moves:
            board = move // 9
            y = (move % 9) // 3
            x = move % 3
            move = (board,x,y)
            #print("Player2: Trying move", move)

            result = game.play(move)
            if (result != -2):
                #print("Move made")
                break
            print("Mistake made")

    if (result == 0):
        game.print_boards()
        print("It's a draw!")
        break

    if (result == -1 or result == 1):
        game.print_boards()
        print("Player wins!" if result==1 else "Computer wins!")
        break
