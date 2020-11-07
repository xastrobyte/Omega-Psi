from cogs.game.minigames.base_game.board import Board
from chess import WHITE, BLACK

def alpha_beta(board, is_player_turn, depth = 0, alpha = Board.LOSS, beta = Board.WIN, max_depth = 4):
    """An alpha-beta pruning algorithm for an AI to decide which move is best
    for them

    :param board: A Board object to use to find the best move
    :param is_player_turn: Whether or not this instance of the function is the players turn
    :param depth: The current depth of this instance
    :param alpha: The current alpha value
    :param beta: The current beta value
    :param max_depth: The maximum depth in the tree to search through (Default: 4)
    """

    # Copy the specified board
    copy_board = board.copy()
    copy_board.turn = BLACK if is_player_turn else WHITE
    legal_moves = [
        str(move)
        for move in copy_board.legal_moves
    ]

    # Keep track of the best move and the best score
    best_score = Board.LOSS if not is_player_turn else Board.WIN
    if len(legal_moves) > 0:
        best_move = legal_moves[0]
    else:
        return Board.WIN if not is_player_turn else Board.LOSS, None

    if board.is_game_over() or depth == max_depth:
        return best_score, best_move
    
    # Iterate through all the legal moves in the board
    for move in legal_moves:
        copy_board.push_uci(move)

        # Maximize the player's turn for the AI to try to avoid this move
        if not is_player_turn:
            score = alpha_beta(copy_board, True, depth + 1, alpha, beta, max_depth = max_depth)[0]
            if best_score < score:
                best_score = score - depth * 10
                best_move = move

                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
    
        # Minimize the AI's turn for the AI to try to make this move
        else:
            score = alpha_beta(copy_board, False, depth + 1, alpha, beta, max_depth = max_depth)[0]
            if best_score > score:
                best_score = score + depth * 10
                best_move = move

                beta = min(beta, best_score)
                if beta <= alpha:
                    break
        copy_board.pop()  # Pop the last move so we can move onto the next move
        
    return best_score, best_move