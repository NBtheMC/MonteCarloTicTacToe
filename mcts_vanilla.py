import random
import time

from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
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
    #UCT = wi/ni + c(sqrt(ln t/ni))
    #append all possible actions for current node
    for action in current.untried_actions:
        new_child = MCTSNode(current, action, board.legal_actions(board.next_state(state, action))) #need to get all actions
        current.child_nodes.append(new_child)
    # calculate UCT of nodes
    greatest_child = None
    greatest_UCT = 0
    for child in current.child_nodes:
        if child.visits is not 0:
            expand_leaf(child, board, state)
        current_UCT = child.wins/child.visits + explore_faction*(sqrt(log(current.visits)/child.visits))
        if current_UCT > greatest_UCT:
            greatest_child = child
            greatest_UCT = current_UCT
    #by this point have visited all nodes and have a greatest
    if greatest_child.visits == 0:
        return traverse_nodes(greatest_child, board, board.next_state(greatest_child.parent_action), identity)
    else:
        return greatest_child

def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """

    #check too see if nodes are filled
    current_state = state
    possible_actions = board.legal_actions(current_state)
    action_to_take = possible_actions[random.randint(0, len(possible_actions) - 1)]
    new_node = (node, action_to_take, [])
    node.child_nodes.append(new_node)
    return new_node

def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    current_state = state
    print(current_state)
    #play random move until an end state reached
    while not board.is_ended(current_state):
        possible_actions = board.legal_actions(current_state)
        action_to_take = possible_actions[random.randint(0, len(possible_actions)-1)]
        current_state = board.next_state(current_state, action_to_take)
    #current state at this point will be an ending state
    return current_state


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    current_node = node
    while current_node:
        current_node.wins += won
        current_node = current_node.parent
    pass


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    print(board.legal_actions(state))
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        #while time
        timer = time.time() + 1
        #while tree size
        tree_size = 1
        while tree_size < 1000:
            leaf = traverse_nodes(node, board, state, identity_of_bot)
            simulated = rollout(leaf)
            backpropagate(leaf, simulated)

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    return traverse_nodes(node, board, state, identity_of_bot).parent_action
