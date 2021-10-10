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
    #print("Visits ", current.visits)
    if current.visits == 0: #if no children, then add a leaf
        #print("Child actions: ")
        for action in current.untried_actions:
            next_state = board.next_state(state, action)
            expanded_leaf = expand_leaf(current, board, next_state)
            expanded_leaf.parent_action = action
            expanded_leaf.untried_actions = board.legal_actions(next_state)
            node.child_nodes[action] = expanded_leaf
            #print("Action: ", action)
    if len(current.child_nodes) == 0:
        return current
    # calculate UCT of nodes
    greatest_child = None
    greatest_UCT = 0
    #Checking for nonvisited children
    for c in current.child_nodes.values():
        if c.visits == 0: #if not visited want to rollout this one
            #print("return")
            return c

    #Using UCT to figure out which child to continue with
    for child in current.child_nodes.values():
        # if child.visits != 0: #expand leaf node
        #     expand_leaf(child, board, state)
        # UCT = wi/ni + c(sqrt(ln t/ni))
        current_UCT = child.wins/child.visits + explore_faction*(sqrt(log(current.visits)/child.visits))
        if current_UCT > greatest_UCT:
            greatest_child = child
            greatest_UCT = current_UCT
    #by this point have visited all nodes and have a greatest
    # if greatest_child.visits > 0:
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

    # #check too see if nodes are filled
    # current_state = state
    # possible_actions = board.legal_actions(current_state)
    # #print("Possible:", possible_actions)
    # for action in possible_actions:
    #     new_node = MCTSNode(node, action, board.legal_actions(board.next_state(state, action)))
    #     node.child_nodes[action] = new_node
    # #print("Action:", action_to_take)
    new_node = MCTSNode(node, None, None)
    return new_node
    

def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    current_state = state #state
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
    #Update win scores
    current_node = node
    while current_node:
        current_node.wins += won
        current_node.visits += 1
        current_node = current_node.parent
    pass

def best_action(node, board, state, identity):
    greatest_UCT = 0
    current_UCT = 0
    greatest_child = None
    for child in node.child_nodes.values():
        # UCT = wi/ni + c(sqrt(ln t/ni))
        current_UCT = child.wins/child.visits + explore_faction*(sqrt(log(node.visits)/child.visits))
        if current_UCT > greatest_UCT:
            greatest_child = child
            greatest_UCT = current_UCT
    return greatest_child.parent_action


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    # print("identity_of_bot")
    # print(identity_of_bot)
    #print(board.legal_actions(state))
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    # Copy the game for sampling a playthrough
    sampled_game = state
    # Start at root
    node = root_node

    # Do MCTS - This is all you!
    timer = time.time() + 1
    #while tree size, eventually replace with timer
    total_score = 0
    tree_size = 1
    while tree_size < num_nodes:
        #print(tree_size)
        leaf = traverse_nodes(node, board, state, identity_of_bot)
        next_state = board.next_state(state, leaf.parent_action)
        simulated = rollout(board, next_state)
        score_to_update = board.win_values(simulated)[identity_of_bot]
        total_score += score_to_update
        backpropagate(leaf, score_to_update) #need to update wins correctly
        tree_size += 1
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    #print(total_score/tree_size)
    action_to_take = best_action(node, board, state, identity_of_bot)
    return action_to_take
