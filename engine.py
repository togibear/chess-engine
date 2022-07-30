class GameState():
    def __init__(self):
        self.board = [
        ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
        ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
        ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]]

        self.move_function = {"p": self.get_pawn_moves, "r": self.get_rook_moves,
                              "n": self.get_knight_moves, "b": self.get_bishop_moves,
                              "q": self.get_queen_moves, "k": self.get_king_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7,4)
        self.black_king_location = (0,4)
        self.in_check = False
        self.checkmate = False
        self.stalemate = False
        self.pins = []
        self.checks = []
        self.en_passant_possible = ()
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.w_kingside, self.current_castling_rights.b_kingside,
                                               self.current_castling_rights.w_queenside, self.current_castling_rights.b_queenside)]

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        if move.piece_moved == "wk":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bk":
            self.black_king_location = (move.end_row, move.end_col)

        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "q"

        if move.is_en_passant:
            self.board[move.start_row][move.end_col] = "--"

        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible = ((move.start_row + move.end_row)//2, move.start_col)
        else:
            self.en_passant_possible = ()

        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1]
                self.board[move.end_row][move.end_col+1] = "--"
            else:
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2]
                self.board[move.end_row][move.end_col-2] = "--"


        #updating castling rights
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.w_kingside, self.current_castling_rights.b_kingside,
                                               self.current_castling_rights.w_queenside, self.current_castling_rights.b_queenside))

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            if move.piece_moved == "wk":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bk":
                self.black_king_location = (move.start_row, move.start_col)

            if move.is_en_passant:
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.en_passant_possible = (move.end_row, move.end_col)

            if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
                self.en_passant_possible = ()

            #undo castling rights
            self.castle_rights_log.pop()
            new_rights = self.castle_rights_log[-1]
            self.current_castling_rights = CastleRights(new_rights.w_kingside, new_rights.b_kingside, new_rights.w_queenside, new_rights.b_queenside)

            #undo castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col-1] = "--"
                else:
                    self.board[move.end_row][move.end_col-2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col+1] = "--"

            self.checkmate = False
            self.stalemate = False

    def update_castle_rights(self, move):
        if move.piece_moved == "wk":
            self.current_castling_rights.w_kingside = False
            self.current_castling_rights.w_queenside = False
        elif move.piece_moved == "bk":
            self.current_castling_rights.b_kingside = False
            self.current_castling_rights.b_queenside = False
        elif move.piece_moved == "wr":
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castling_rights.w_queenside = False
                elif move.start_col == 7:
                    self.current_castling_rights.w_kingside = False
        elif move.piece_moved == "br":
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castling_rights.b_queenside = False
                elif move.start_col == 7:
                    self.current_castling_rights.b_kingside = False

        if move.piece_captured == "wr":
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castling_rights.w_queenside = False
                elif move.end_col == 7:
                    self.current_castling_rights.w_kingside = False
        if move.piece_captured == "br":
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castling_rights.b_queenside = False
                elif move.end_col == 7:
                    self.current_castling_rights.b_kingside = False



    def get_valid_moves(self):
        moves = []
        self.in_check, self.pins, self.checks = self.pins_and_checks()
        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1:
                moves = self.get_all_moves()
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_attacking = self.board[check_row][check_col]
                valid_squares = []
                if piece_attacking[1] == "n":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1,8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != "k":
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_row, king_col, moves)
        else:
            moves = self.get_all_moves()
            if self.white_to_move:
                self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)

        if len(moves) == 0:
            if self.incheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        return moves

    def incheck(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, row, col):
        self.white_to_move = not self.white_to_move  # switch to opponent's point of view
        opponents_moves = self.get_all_moves()
        self.white_to_move = not self.white_to_move
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:  # square is under attack
                return True
        return False

    def get_all_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                piece = self.board[r][c][1]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    self.move_function[piece](r, c, moves)
        return moves

    def pins_and_checks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "k":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "r") or (4 <= j <= 7 and enemy_type == "b") or (
                                i == 1 and enemy_type == "p" and (
                                (enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (
                                enemy_type == "q") or (i == 1 and enemy_type == "k"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "n":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks


    def get_pawn_moves(self, r, c, moves):
        pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            if self.board[r-1][c] == "--":
                if not pinned or pin_direction == (-1, 0):
                    moves.append(Move((r,c), (r-1,c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":
                        moves.append(Move((r,c), (r-2,c), self.board))

            if c-1 >= 0:
                if self.board[r-1][c-1][0] == "b":
                    if not pinned or pin_direction == (-1, -1):
                        moves.append(Move((r,c), (r-1,c-1), self.board))
                elif (r-1, c-1) == self.en_passant_possible:
                    if not pinned or pin_direction == (-1, -1):
                        moves.append(Move((r,c), (r-1,c-1), self.board, is_en_passant = True))

            if c+1 <= 7:
                if self.board[r-1][c+1][0] == "b":
                    if not pinned or pin_direction == (-1, 1):
                        moves.append(Move((r,c), (r-1,c+1), self.board))
                elif (r-1, c+1) == self.en_passant_possible:
                    if not pinned or pin_direction == (-1, 1):
                        moves.append(Move((r,c), (r-1,c+1), self.board, is_en_passant = True))


        else:
            if self.board[r+1][c] == "--":
                if not pinned or pin_direction == (1, 0):
                    moves.append(Move((r,c), (r+1,c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append(Move((r,c), (r+2,c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == "w":
                    if not pinned or pin_direction == (1, -1):
                        moves.append(Move((r,c), (r+1,c-1), self.board))
                elif (r+1, c-1) == self.en_passant_possible:
                    if not pinned or pin_direction == (1, -1):
                        moves.append(Move((r,c), (r+1,c-1), self.board, is_en_passant = True))

            if c+1 <= 7:
                if self.board[r+1][c+1][0] == "w":
                    if not pinned or pin_direction == (1, 1):
                        moves.append(Move((r,c), (r+1,c+1), self.board))
                elif (r+1, c+1) == self.en_passant_possible:
                    if not pinned or pin_direction == (1, 1):
                        moves.append(Move((r,c), (r+1,c+1), self.board, is_en_passant = True))




    def get_rook_moves(self, r, c, moves):
        pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "q":
                    self.pins.remove(self.pins[i])
                break


        directions = ((-1,0),(0,-1),(1,0),(0,1))
        opposing = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end = self.board[end_row][end_col]
                        if end == "--":
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                        elif end[0] == opposing:
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break



    def get_knight_moves(self, r, c, moves):
        pinned = False
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1]:
                pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        ally = "w" if self.white_to_move else "b"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not pinned:
                    end = self.board[end_row][end_col]
                    if end[0] != ally:
                        moves.append(Move((r,c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        pinned = False
        pin_direction = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,-1),(-1,1),(1,-1),(1,1))
        opposing = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end = self.board[end_row][end_col]
                        if end == "--":
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                        elif end[0] == opposing:
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end = self.board[end_row][end_col]
                if end[0] != ally:
                    if ally == "w":
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.pins_and_checks()
                    if not in_check:
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                    if ally == "w":
                        self.white_king_location = (r,c)
                    else:
                        self.black_king_location = (r,c)

    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return
        if (self.white_to_move and self.current_castling_rights.w_kingside) or (not self.white_to_move and self.current_castling_rights.b_kingside):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.white_to_move and self.current_castling_rights.w_queenside) or (not self.white_to_move and self.current_castling_rights.b_queenside):
            self.get_queenside_castle_moves(r, c, moves)

    def get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r,c), (r,c+2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r,c-2), self.board, is_castle_move=True))



class CastleRights():
    def __init__(self, w_kingside, b_kingside, w_queenside, b_queenside):
        self.w_kingside = w_kingside
        self.b_kingside = b_kingside
        self.w_queenside = w_queenside
        self.b_queenside = b_queenside


class Move():
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}


    def __init__(self, start, end, board, is_en_passant = False, is_castle_move = False):
        self.start_row = start[0]
        self.start_col = start[1]
        self.end_row = end[0]
        self.end_col = end[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.is_pawn_promotion = False
        if (self.piece_moved == "wp" and self.end_row == 0) or (self.piece_moved == "bp" and self.end_row == 7):
            self.is_pawn_promotion = True

        self.is_en_passant = is_en_passant
        if self.is_en_passant:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"

        self.is_castle_move = is_castle_move

        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def get_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
