from random import choice
from cogs.game.minigames.base_game.board import Board

def alpha_beta(board, is_player_turn, depth = 0, alpha = Board.LOSS, beta = Board.WIN, max_depth = 4):
    """An alpha-beta pruning algorithm for an AI to decide which move is best
    for them

    Parameters
    ----------
        board : Board
            A Board object to use to find the best move
        is_player_turn : boolean
            Whether or not this instance of the function is the players turn
        depth : int
            The current depth of this instance
        alpha : int
            The current alpha value
        beta : int
            The current beta value
        
    Keyword Parameters
    ------------------
        max_depth : int
            The maximum depth in the tree to search through (Default is 4).
    """

    # Keep track of the best move and the best score
    best_move = -1, -1
    best_score = Board.LOSS if not is_player_turn else Board.WIN

    if board.is_full() or board.check_for_winner() != 0 or depth == max_depth:
        return best_score, best_move
    
    # Iterate through all the legal moves in the board
    for move in board.get_legal_moves():
        board.board[move[0]][move[1]] = is_player_turn

        # Maximize the player's turn for the AI to try to avoid this move
        if not is_player_turn:
            score = alpha_beta(board, True, depth + 1, alpha, beta, max_depth = max_depth)[0]
            if best_score < score:
                best_score = score - depth * 10
                best_move = move

                alpha = max(alpha, best_score)
                board.board[move[0]][move[1]] = None
                if beta <= alpha:
                    break
    
        # Minimize the AI's turn for the AI to try to make this move
        else:
            score = alpha_beta(board, False, depth + 1, alpha, beta, max_depth = max_depth)[0]
            if best_score > score:
                best_score = score + depth * 10
                best_move = move

                beta = min(beta, best_score)
                board.board[move[0]][move[1]] = None
                if beta <= alpha:
                    break
        
        # Reset the board space; We don't want to keep this temporary move
        #   in the board state outside of this function
        board.board[move[0]][move[1]] = None
        
    return best_score, best_move