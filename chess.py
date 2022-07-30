import pygame
import engine
import chess_ai
import sys
from multiprocessing import Process, Queue

WIDTH = HEIGHT = 480
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}



def load_images():
    pieces = ["wp", "wr", "wn", "wb", "wq", "wk", "bp", "br", "bn", "bb", "bq", "bk"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load("images/{}.png".format(piece)), (SQUARE_SIZE, SQUARE_SIZE))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))
    gs = engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_log = gs.move_log
    animate_move = False
    made = False
    game_over = False

    load_images()
    running = True
    selected = ()
    clicks = []

    piecemoved = pygame.mixer.Sound("audio/piecemoved.wav")
    piececaptured = pygame.mixer.Sound("audio/piececaptured.wav")
    gameover = pygame.mixer.Sound("audio/gameover.wav")
    startup = pygame.mixer.Sound("audio/startup.wav")
    startup_sound_played = False
    gameover_sound_played = False
    w_player = True
    b_player = False

    ai_thinking = False
    move_undone = False
    move_finder_process = None

    while running:

        if startup_sound_played == False:
            startup.play()
            startup_sound_played = True

        if gameover_sound_played == False and game_over:
            gameover.play()
            gameover_sound_played = True

        human_playing = (gs.white_to_move and w_player) or (not gs.white_to_move and b_player)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    location = pygame.mouse.get_pos()
                    col = location[0]//SQUARE_SIZE
                    row = location[1]//SQUARE_SIZE
                    if selected == (row, col):
                        selected = ()
                        clicks = []
                    else:
                        selected = (row, col)
                        clicks.append(selected)

                    if len(clicks) == 2 and human_playing:
                        move = engine.Move(clicks[0], clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                if gs.board[clicks[1][0]][clicks[1][1]] == "--":
                                    piecemoved.play()
                                else:
                                    piececaptured.play()
                                gs.make_move(valid_moves[i])
                                made = True
                                animate_move = True
                                selected = ()
                                clicks = []
                        if not made:
                            clicks = [selected]
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    if len(move_log) != 0:
                        piecemoved.play()
                    gs.undo_move()
                    made = True
                    animate_move = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

            #AI
            if not game_over and not human_playing and not move_undone:
                if not ai_thinking:
                    ai_thinking = True
                    return_queue = Queue()
                    move_finder_process = Process(target=chess_ai.find_best_move, args = (gs, valid_moves, return_queue))
                    move_finder_process.start()
                if not move_finder_process.is_alive():
                    ai_move = return_queue.get()
                    if ai_move is None:
                        ai_move = chess_ai.find_random_move(valid_moves)
                    gs.make_move(ai_move)
                    made = True
                    animate_move = True
                    ai_thinking = False

            if made:
                if animate_move:
                    animate(gs.move_log[-1], screen, gs.board, clock)
                valid_moves = gs.get_valid_moves()
                made = False
                animate_move = False
                move_undone = False



        draw_game_state(screen, gs, valid_moves, selected, move_log)

        if gs.checkmate:
            game_over = True

        elif gs.stalemate:
            game_over = True

        clock.tick(MAX_FPS)
        pygame.display.flip()

def draw_game_state(screen, gs, valid_moves, selected, move_log):
    draw_board(screen)
    draw_moves(screen, gs, valid_moves, selected, move_log)
    draw_pieces(screen, gs.board)

def draw_board(screen):
    colors = [pygame.Color(186, 186, 186), pygame.Color(122, 122, 122)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            pygame.draw.rect(screen, color, pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_moves(screen, gs, valid_moves, selected, move_log):
    color2 = pygame.Color(186, 221, 255)
    color = pygame.Color(186, 221, 255)

    if selected != ():
        r, c = selected
        if gs.board[r][c][0] == ("w" if gs.white_to_move else "b"):
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(color)
            screen.blit(s, (c*SQUARE_SIZE, r * SQUARE_SIZE))
            s.fill(color)
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col*SQUARE_SIZE, move.end_row*SQUARE_SIZE))
    if move_log:
        move = move_log[-1]
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(80)
        s.fill(color2)
        screen.blit(s, (move.start_col*SQUARE_SIZE, move.start_row*SQUARE_SIZE))
        screen.blit(s, (move.end_col*SQUARE_SIZE, move.end_row*SQUARE_SIZE))



def animate(move, screen, board, clock):
    colors = [pygame.Color(186, 186, 186), pygame.Color(122, 122, 122)]
    delta_row = move.end_row - move.start_row
    delta_col = move.end_col - move.start_col
    fps = 4
    frame_count = (abs(delta_row) + abs(delta_col)) * fps
    for frame in range(frame_count + 1):
        r, c = (move.start_row + delta_row*frame/frame_count, move.start_col + delta_col*frame/frame_count)
        draw_board(screen)
        draw_pieces(screen,board)
        color = colors[(move.end_row + move.end_col) % 2]
        end = pygame.Rect(move.end_col*SQUARE_SIZE, move.end_row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen,color,end)
        if move.piece_captured != "--":
            screen.blit(IMAGES[move.piece_captured], end)
        screen.blit(IMAGES[move.piece_moved], pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
