import random
import math
from enum import IntEnum

import isolation
from sample_players import DataPlayer

S, N, W, E = -isolation.isolation._WIDTH - 2, isolation.isolation._WIDTH + 2, 1, -1    

class Range(IntEnum):
    """Similar to Action class but includes the area radius of 2 around the state
    """
    NNE = N+N+E  
    ENE = E+N+E  
    ESE = E+S+E  
    SSE = S+S+E  
    SSW = S+S+W  
    WSW = W+S+W  
    WNW = W+N+W  
    NNW = N+N+W  
    N = N
    NN = N+N
    S = S
    SS = S+S
    E = E
    EE = E+E
    W = W
    WW = W+W
    NE = N+E
    NENE = N+E+N+E
    SE = S+E
    SESE = S+E+S+E
    SW = S+W
    SWSW = S+W+S+W
    NW = N+W
    NWNW = N+W+N+W 

_RangeSet = set(Range)  

class CustomPlayer(DataPlayer):

    def __init__(self, player_id):
        super().__init__(player_id)
        self.t = 1
        self.alpha = 0.012
        self.t_Middle = 0.3
        self.t_Final = 0.8

    """ Implement your own agent to play knight's Isolation
    The get_action() method is the only required method for this project.
    You can modify the interface for get_action by adding named parameters
    with default values, but the function MUST remain compatible with the
    default interface.
    **********************************************************************
    NOTES:
    - The test cases will NOT be run on a machine with GPU access, nor be
      suitable for using any other machine learning techniques.
    - You can pass state forward to your agent on the next turn by assigning
      any pickleable object to the self.context attribute.
    **********************************************************************
    """
    def get_action(self, state):
        """ Employ an adversarial search technique to choose an action
        available in the current state calls self.queue.put(ACTION) at least
        This method must call self.queue.put(ACTION) at least once, and may
        call it as many times as you want; the caller will be responsible
        for cutting off the function after the search time limit has expired.
        See RandomPlayer and GreedyPlayer in sample_players for more examples.
        **********************************************************************
        NOTE: 
        - The caller is responsible for cutting off search, so calling
          get_action() from your own code will create an infinite loop!
          Refer to (and use!) the Isolation.play() function to run games.
        **********************************************************************
        """
        # TODO: Replace the example implementation below with your own search
        #       method by combining techniques from lecture
        #
        # EXAMPLE: choose a random move without any search--this function MUST
        #          call self.queue.put(ACTION) at least once before time expires
        #          (the timer is automatically managed for you)
        if state.ply_count < 1:
            self.queue.put(random.choice(state.actions()))
        else:
            self.queue.put(self.ab_decision(state, depth=3, alpha=-math.inf, beta=math.inf))
        self.t = self.t - self.t * self.alpha
        self.context = [self.t]
   
    
    def ab_decision(self, state, depth, alpha, beta):

        def min_value(state, depth, alpha, beta):
            if state.terminal_test():
                return state.utility(self.player_id)
            if depth <= 0: 
                return self.score(state)
            value = float("inf")
            for a in state.actions():
                value = min(value, max_value(state.result(a), depth - 1, alpha, beta))
                if value <= alpha:
                    return value
                beta = min(beta, value)
            return value

        def max_value(state, depth, alpha, beta):
            if state.terminal_test():
                return state.utility(self.player_id)
            if depth <= 0: 
                return self.score(state)
            value = -float("inf")
            for a in state.actions():
                value = max(value, min_value(state.result(a), depth - 1, alpha, beta))
                if value >= beta:
                    return value
                alpha = max(alpha, value)
            return value

        return max(state.actions(), key=lambda x: min_value(state.result(x), depth - 1, alpha, beta))

    def score(self, state):
      return self.heuristic(state)

    def heuristic(self, state):
        own_loc = state.locs[self.player_id]
        opp_loc = state.locs[1 - self.player_id]
        own_liberties = state.liberties(own_loc)
        opp_liberties = state.liberties(opp_loc)  
        own_dencity, opp_dencity = self.dencities(state)

        features = [len(own_liberties), len(opp_liberties), 
                    len(own_dencity), len(opp_dencity),
                    self.only_opp_liberty_is_ours(own_loc, opp_liberties),
                    self.opp_liberty_is_ours(own_loc, opp_liberties)]
        weights = self.feature_weights()

        score = sum([w*f for w,f in zip(weights, features)])
        return score

    def opp_liberty_is_ours(self, own_loc, opp_liberties):
        if own_loc in opp_liberties:
            return 1
        return 0

    def only_opp_liberty_is_ours(self, own_loc, opp_liberties):
        if len(opp_liberties) == 1 and own_loc in opp_liberties:    
            return 1
        return 0

    def dencities(self, state):
        """ Similar to liberties function, returns list of available cells
            in the current state range radius of 2
        """
        own_loc = state.locs[self.player_id]
        own_cells = range(isolation.isolation._SIZE) if own_loc is None else (own_loc + a for a in Range)
        opp_loc = state.locs[1 - self.player_id]
        opp_cells = range(isolation.isolation._SIZE) if opp_loc is None else (opp_loc + a for a in Range)
        return ([c for c in own_cells if c >= 0 and state.board & (1 << c)],
                [c for c in opp_cells if c >= 0 and state.board & (1 << c)])

    def feature_weights(self):
        if self.t > self.t_Middle:
            return [100, -100, 5, -5, 10000, 0]
        if self.t > self.t_Final:
            return [10, -10, 20, -10, 10000, 25]
        return [10, -10, 30, -10, 10000, 250]

