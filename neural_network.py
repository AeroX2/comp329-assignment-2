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

def evaluate_game(mlp1, mlp2):
    mf = np.vectorize(lambda x: 0.5 if x is None else float(x))

    game = Game()
    result = None
    mistakes = 0

    while (result not in [-1,0,1]):
        #print(result)
        #game.print_boards()

        if (game.player1_move):
            translate = mf(np.array(game.boards).flatten())
            moves = mlp1.predict([translate])[0]
            moves = [z[1] for z in sorted([(x,i) for i,x in enumerate(moves)])]

            for move in moves:

                board = move // 9
                y = (move % 9) // 3
                x = move % 3
                move = (board,x,y)
                #print("Player1: Trying move", move)

                result = game.play(move)
                if (result != -2):
                    #print("Move made")
                    break
                mistakes += 1
        else:
            translate = mf(np.array(game.boards).flatten())
            moves = mlp2.predict([translate])[0]
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

    #print("Finished")
    #game.print_boards()
    if (result == 1):
        return (10-mistakes,)
    elif (result == -1):
        return (-10-mistakes,)
    elif (result == 0):
        return (-mistakes,)
    else:
        print("WTF")
    
def mapOverride(f,l):
    return [f(x,l,i) for i,x in enumerate(l)] 

def evaluation(current_individual, l, i):
    average = 0
    for ii,x in enumerate(l):
        if (ii == i):
            continue

        current_mlp = MLPClassifierOverride()
        current_mlp.init_weights(current_individual)
        current_mlp.fit([[0.0]*3*3*3,[0.0]*3*3*3], [[0.1]*3*3*3,[0.1]*3*3*3])

        previous_mlp = MLPClassifierOverride()
        previous_mlp.init_weights(x)
        previous_mlp.fit([[0.0]*3*3*3,[0.0]*3*3*3], [[0.1]*3*3*3,[0.1]*3*3*3])

        average += evaluate_game(current_mlp, previous_mlp)[0]
    return (average/(len(l)-1),)

def selectOverride(pop, l):
    return tools.selBest(pop,k=3)+tools.selTournament(pop,l-3,tournsize=3)

toolbox = base.Toolbox()

#w=np.random.randn(layer_size[l],layer_size[l-1])*np.sqrt(2/layer_size[l-1])

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

n = (3*3*3 * 100) + 100 + (100 * 3*3*3) + 3*3*3 # Input size + Hidden layer size + biases
toolbox.register("attr_float", random.random)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_float, n=n)

toolbox.register("population", tools.initRepeat, list, 
                 toolbox.individual)
toolbox.register("map", mapOverride)
toolbox.register("evaluate", evaluation)

toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", selectOverride) 

print("Here goes nothing")

import operator
fit_stats = tools.Statistics(key=operator.attrgetter("fitness.values"))
fit_stats.register('mean', np.mean)
fit_stats.register('min', np.min)
fit_stats.register('max', np.max)

ngen = 200
pop = toolbox.population(n=50)
result, log = algorithms.eaSimple(pop, toolbox,
                             cxpb=0.8, mutpb=0.1,
                             ngen=ngen, verbose=True,
                             stats=fit_stats)
best = tools.selBest(result,k=1)[0]
np.save('best_blob3_%d' % ngen, best)

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
    game.print_boards()
    if (game.player1_move):
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
        if (human_move):
            print("Player wins!" if result==1 else "Computer wins!")
        else:
            print("Computer wins!" if result==1 else "Player wins!")
        break
