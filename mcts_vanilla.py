import math
import random
import time

from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 100
explore_faction = 2.

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    current = node
    greatest_child = None
    greatest_UCT = -math.inf
    #Checking for nonvisited children
    # for c in current.child_nodes.values():
    #     if c.visits == 0: #if not visited want to rollout this one
    #         return c
    if current.untried_actions:
        return (current, state)
    if len(current.child_nodes) == 0:
        return (current, state)
    for child in current.child_nodes.values():
        if identity == board.current_player(state):
            current_UCT = child.wins/child.visits + explore_faction * (sqrt(log(current.visits) / child.visits))
        else:
            current_UCT = (1-(child.wins/child.visits)) + explore_faction * (sqrt(log(current.visits) / child.visits))
        
        if current_UCT > greatest_UCT:
            greatest_child = child
            greatest_UCT = current_UCT
    if not greatest_child:
        return (current, state)
    next_state = board.next_state(state, greatest_child.parent_action)
    return traverse_nodes(greatest_child, board, next_state, identity)
    

def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    if not node.untried_actions:
        return node, state
    random_action = choice(node.untried_actions)
    new_state = board.next_state(state, random_action)
    new_node = MCTSNode(node, random_action, board.legal_actions(new_state))
    node.child_nodes[random_action] = new_node
    node.untried_actions.remove(random_action)
    return new_node, new_state
    

def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    current_state = state #state
    while not board.is_ended(current_state):
        possible_actions = board.legal_actions(current_state)
        action_to_take = random.choice(possible_actions)
        current_state = board.next_state(current_state, action_to_take)
    return current_state


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    #Update win scores
    current_node = node
    while current_node:
        current_node.wins += won
        current_node.visits += 1
        current_node = current_node.parent
    pass

def best_action(node, board, state, identity):
    greatest_winrate = -math.inf
    current_winrate = 0
    greatest_child = None

    for child in node.child_nodes.values():
        # UCT = wi/ni + c(sqrt(ln t/ni))
        # if(child.visits == 0):
        #     return child.parent_action
        current_winrate = child.wins/child.visits
        if current_winrate > greatest_winrate:
            greatest_child = child
            greatest_winrate = current_winrate
    return greatest_child.parent_action


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    # Copy the game for sampling a playthrough
    sampled_game = state
    # Start at root
    node = root_node
    node_amount = num_nodes
    # if identity_of_bot == 1:
    #     node_amount = 200
    # Do MCTS - This is all you!
    #while tree size, eventually replace with timer
    tree_size = 1

    # timer = 0.1 + time.time()
    # while time.time() < timer:
    while tree_size < num_nodes:
        #print(tree_size)
        new_leaf, new_state = traverse_nodes(node, board, state, identity_of_bot) #add state for current layer
        #expand leaf here
        new_node, new_state = expand_leaf(new_leaf, board, new_state)
        #next_state = board.next_state(state, leaf.parent_action)
        simulated = rollout(board, new_state) #use state returned from expand leaf
        score_to_update = board.win_values(simulated)[identity_of_bot]
        backpropagate(new_node, score_to_update) #need to update wins correctly
        tree_size += 1
    #print(tree_size)
    action_to_take = best_action(node, board, state, identity_of_bot)
    return action_to_take