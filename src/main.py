import os
import sys
import pygame
import chess
import chess.engine


# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()

WIDTH = 1000
HEIGHT = 800

BOARD_SIZE = 800
PANEL_WIDTH = 200
SQUARE_SIZE = BOARD_SIZE // 8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Chess")

clock = pygame.time.Clock()


# ============================================================
# COLORS
# ============================================================

LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)

BACKGROUND = (30, 30, 35)
PANEL_COLOR = (38, 38, 45)

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)

GREEN = (80, 200, 120)
RED = (220, 70, 70)
BLUE = (70, 140, 220)
YELLOW = (235, 210, 70)
GRAY = (150, 150, 150)

SELECT_COLOR = (80, 150, 255)
MOVE_COLOR = (90, 190, 100)
LAST_MOVE_COLOR = (235, 210, 70)
CHECK_COLOR = (220, 70, 70)


# ============================================================
# FONTS
# ============================================================

FONT_SMALL = pygame.font.SysFont("arial", 16)
FONT_MEDIUM = pygame.font.SysFont("arial", 20)
FONT_LARGE = pygame.font.SysFont("arial", 30, bold=True)
FONT_TITLE = pygame.font.SysFont("arial", 48, bold=True)

PIECE_FONT = pygame.font.SysFont("segoeuisymbol", 72)


# ============================================================
# STOCKFISH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

STOCKFISH_PATH = os.path.join(
    PROJECT_ROOT,
    "stockfish",
    "stockfish.exe"
)

engine = None


def initialize_stockfish():
    global engine

    if not os.path.exists(STOCKFISH_PATH):
        print("Stockfish not found:")
        print(STOCKFISH_PATH)
        return False

    try:
        engine = chess.engine.SimpleEngine.popen_uci(
            STOCKFISH_PATH
        )

        print("Stockfish connected successfully.")
        return True

    except Exception as e:
        print("Stockfish initialization error:", e)
        engine = None
        return False


STOCKFISH_AVAILABLE = initialize_stockfish()


# ============================================================
# CHESS PIECES
# ============================================================

PIECE_SYMBOLS = {
    "P": "♙",
    "N": "♘",
    "B": "♗",
    "R": "♖",
    "Q": "♕",
    "K": "♔",
    "p": "♟",
    "n": "♞",
    "b": "♝",
    "r": "♜",
    "q": "♛",
    "k": "♚",
}


# ============================================================
# BUTTON
# ============================================================

class Button:

    def __init__(self, rect, text, color=BLUE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color

    def draw(self, surface):

        mouse_pos = pygame.mouse.get_pos()

        current_color = self.color

        if self.rect.collidepoint(mouse_pos):
            current_color = tuple(
                min(255, c + 30)
                for c in self.color
            )

        pygame.draw.rect(
            surface,
            current_color,
            self.rect,
            border_radius=8
        )

        pygame.draw.rect(
            surface,
            WHITE,
            self.rect,
            2,
            border_radius=8
        )

        text_surface = FONT_MEDIUM.render(
            self.text,
            True,
            WHITE
        )

        text_rect = text_surface.get_rect(
            center=self.rect.center
        )

        surface.blit(
            text_surface,
            text_rect
        )

    def clicked(self, event):

        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ============================================================
# MAIN MENU
# ============================================================

def main_menu():

    play_button = Button(
        (350, 330, 300, 60),
        "PLAY",
        GREEN
    )

    quit_button = Button(
        (350, 420, 300, 60),
        "QUIT",
        RED
    )

    while True:

        screen.fill(BACKGROUND)

        title = FONT_TITLE.render(
            "AI CHESS",
            True,
            WHITE
        )

        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 180)
            )
        )

        subtitle = FONT_MEDIUM.render(
            "Human vs Stockfish",
            True,
            GRAY
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(WIDTH // 2, 240)
            )
        )

        play_button.draw(screen)
        quit_button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "quit"

            if play_button.clicked(event):
                return "difficulty"

            if quit_button.clicked(event):
                return "quit"

        clock.tick(60)


# ============================================================
# DIFFICULTY MENU
# ============================================================

def difficulty_menu():

    easy_button = Button(
        (350, 250, 300, 55),
        "EASY",
        GREEN
    )

    medium_button = Button(
        (350, 330, 300, 55),
        "MEDIUM",
        BLUE
    )

    hard_button = Button(
        (350, 410, 300, 55),
        "HARD",
        RED
    )

    back_button = Button(
        (350, 500, 300, 55),
        "BACK",
        GRAY
    )

    while True:

        screen.fill(BACKGROUND)

        title = FONT_LARGE.render(
            "SELECT DIFFICULTY",
            True,
            WHITE
        )

        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 150)
            )
        )

        easy_button.draw(screen)
        medium_button.draw(screen)
        hard_button.draw(screen)
        back_button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "quit"

            if easy_button.clicked(event):
                return "easy"

            if medium_button.clicked(event):
                return "medium"

            if hard_button.clicked(event):
                return "hard"

            if back_button.clicked(event):
                return "back"

        clock.tick(60)


# ============================================================
# DIFFICULTY SETTINGS
# ============================================================

DIFFICULTY_SETTINGS = {

    "easy": {
        "name": "EASY",
        "depth": 6
    },

    "medium": {
        "name": "MEDIUM",
        "depth": 10
    },

    "hard": {
        "name": "HARD",
        "depth": 14
    }
}


def difficulty_name(difficulty):
    return DIFFICULTY_SETTINGS[difficulty]["name"]


# ============================================================
# BOARD COORDINATES
# ============================================================

def square_to_screen(square):

    file = chess.square_file(square)
    rank = chess.square_rank(square)

    x = file * SQUARE_SIZE
    y = (7 - rank) * SQUARE_SIZE

    return x, y


def get_square_from_mouse(pos):

    x, y = pos

    if x >= BOARD_SIZE or y >= BOARD_SIZE:
        return None

    file = x // SQUARE_SIZE
    rank = 7 - (y // SQUARE_SIZE)

    return chess.square(file, rank)


# ============================================================
# DRAW BOARD
# ============================================================

def draw_board(
    board,
    selected_square=None,
    last_move=None
):

    # Draw squares
    for rank in range(8):

        for file in range(8):

            x = file * SQUARE_SIZE
            y = rank * SQUARE_SIZE

            if (rank + file) % 2 == 0:
                color = LIGHT_SQUARE
            else:
                color = DARK_SQUARE

            pygame.draw.rect(
                screen,
                color,
                (
                    x,
                    y,
                    SQUARE_SIZE,
                    SQUARE_SIZE
                )
            )

    # Last move
    if last_move:

        for square in [
            last_move.from_square,
            last_move.to_square
        ]:

            x, y = square_to_screen(square)

            overlay = pygame.Surface(
                (
                    SQUARE_SIZE,
                    SQUARE_SIZE
                ),
                pygame.SRCALPHA
            )

            overlay.fill(
                (*LAST_MOVE_COLOR, 110)
            )

            screen.blit(
                overlay,
                (x, y)
            )

    # Selected square
    if selected_square is not None:

        x, y = square_to_screen(
            selected_square
        )

        pygame.draw.rect(
            screen,
            SELECT_COLOR,
            (
                x,
                y,
                SQUARE_SIZE,
                SQUARE_SIZE
            ),
            5
        )

        # Legal moves
        for move in board.legal_moves:

            if move.from_square == selected_square:

                x, y = square_to_screen(
                    move.to_square
                )

                center = (
                    x + SQUARE_SIZE // 2,
                    y + SQUARE_SIZE // 2
                )

                pygame.draw.circle(
                    screen,
                    MOVE_COLOR,
                    center,
                    10
                )

    # Draw pieces
    for square in chess.SQUARES:

        piece = board.piece_at(square)

        if piece is None:
            continue

        x, y = square_to_screen(square)

        symbol = PIECE_SYMBOLS[
            piece.symbol()
        ]

        # Shadow
        shadow = PIECE_FONT.render(
            symbol,
            True,
            (70, 70, 70)
        )

        shadow_rect = shadow.get_rect(
            center=(
                x + SQUARE_SIZE // 2 + 2,
                y + SQUARE_SIZE // 2 + 3
            )
        )

        screen.blit(
            shadow,
            shadow_rect
        )

        # Piece
        if piece.color == chess.WHITE:
            piece_color = (250, 250, 250)
        else:
            piece_color = (30, 30, 30)

        piece_surface = PIECE_FONT.render(
            symbol,
            True,
            piece_color
        )

        piece_rect = piece_surface.get_rect(
            center=(
                x + SQUARE_SIZE // 2,
                y + SQUARE_SIZE // 2
            )
        )

        screen.blit(
            piece_surface,
            piece_rect
        )

    # Check indicator
    if board.is_check():

        king_square = board.king(
            board.turn
        )

        if king_square is not None:

            x, y = square_to_screen(
                king_square
            )

            pygame.draw.rect(
                screen,
                CHECK_COLOR,
                (
                    x + 5,
                    y + 5,
                    SQUARE_SIZE - 10,
                    SQUARE_SIZE - 10
                ),
                5
            )


# ============================================================
# PROMOTION MENU
# ============================================================

def promotion_menu():

    options = [
        ("Queen", chess.QUEEN),
        ("Rook", chess.ROOK),
        ("Bishop", chess.BISHOP),
        ("Knight", chess.KNIGHT)
    ]

    buttons = []

    start_y = 250

    for i, (name, piece_type) in enumerate(options):

        button = Button(
            (
                350,
                start_y + i * 70,
                300,
                55
            ),
            name,
            BLUE
        )

        buttons.append(
            (button, piece_type)
        )

    while True:

        screen.fill(BACKGROUND)

        title = FONT_LARGE.render(
            "CHOOSE PROMOTION",
            True,
            WHITE
        )

        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 170)
            )
        )

        for button, _ in buttons:
            button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for button, piece_type in buttons:

                if button.clicked(event):
                    return piece_type

        clock.tick(60)


# ============================================================
# CREATE HUMAN MOVE
# ============================================================

def create_human_move(
    board,
    from_square,
    to_square
):

    candidates = []

    for move in board.legal_moves:

        if (
            move.from_square == from_square
            and move.to_square == to_square
        ):

            candidates.append(move)

    if not candidates:
        return None

    promotion_moves = [
        move
        for move in candidates
        if move.promotion is not None
    ]

    if promotion_moves:

        piece_type = promotion_menu()

        for move in promotion_moves:

            if move.promotion == piece_type:
                return move

    return candidates[0]


# ============================================================
# STOCKFISH AI MOVE
# ============================================================

def get_ai_move(board, difficulty):

    global engine

    if engine is None:
        return None

    try:

        depth = DIFFICULTY_SETTINGS[
            difficulty
        ]["depth"]

        result = engine.play(
            board,
            chess.engine.Limit(
                depth=depth
            )
        )

        return result.move

    except Exception as e:

        print(
            "Stockfish move error:",
            e
        )

        return None


# ============================================================
# GAME STATUS
# ============================================================

def get_game_status(board):

    if board.is_checkmate():

        if board.turn == chess.WHITE:
            return "CHECKMATE - AI WINS"

        return "CHECKMATE - YOU WIN"

    if board.is_stalemate():
        return "STALEMATE - DRAW"

    if board.is_insufficient_material():
        return "DRAW - INSUFFICIENT MATERIAL"

    if board.is_seventyfive_moves():
        return "DRAW - 75 MOVE RULE"

    if board.is_fivefold_repetition():
        return "DRAW - REPETITION"

    if board.is_check():

        if board.turn == chess.WHITE:
            return "YOUR KING IS IN CHECK"

        return "AI KING IS IN CHECK"

    if board.turn == chess.WHITE:
        return "YOUR TURN"

    return "AI THINKING"


# ============================================================
# MOVE HISTORY
# ============================================================

def draw_move_history(history):

    title = FONT_MEDIUM.render(
        "MOVE HISTORY",
        True,
        WHITE
    )

    screen.blit(
        title,
        (820, 410)
    )

    if not history:

        empty = FONT_SMALL.render(
            "No moves yet",
            True,
            GRAY
        )

        screen.blit(
            empty,
            (820, 445)
        )

        return

    recent_moves = history[-6:]

    start_y = 445

    for i, move_text in enumerate(
        recent_moves
    ):

        index = (
            len(history)
            - len(recent_moves)
            + i
            + 1
        )

        text = FONT_SMALL.render(
            f"{index}. {move_text}",
            True,
            WHITE
        )

        screen.blit(
            text,
            (
                820,
                start_y + i * 28
            )
        )


# ============================================================
# SIDE PANEL
# ============================================================

def draw_side_panel(
    board,
    difficulty,
    history,
    undo_available
):

    pygame.draw.rect(
        screen,
        PANEL_COLOR,
        (
            BOARD_SIZE,
            0,
            PANEL_WIDTH,
            HEIGHT
        )
    )

    title = FONT_LARGE.render(
        "CHESS",
        True,
        WHITE
    )

    screen.blit(
        title,
        (830, 25)
    )

    player_text = FONT_SMALL.render(
        "PLAYER: WHITE",
        True,
        WHITE
    )

    screen.blit(
        player_text,
        (820, 85)
    )

    ai_text = FONT_SMALL.render(
        "AI: BLACK",
        True,
        WHITE
    )

    screen.blit(
        ai_text,
        (820, 115)
    )

    difficulty_text = FONT_SMALL.render(
        f"LEVEL: {difficulty_name(difficulty)}",
        True,
        YELLOW
    )

    screen.blit(
        difficulty_text,
        (820, 145)
    )

    status = get_game_status(board)

    status_color = GREEN

    if "CHECK" in status:
        status_color = RED

    if "DRAW" in status:
        status_color = YELLOW

    if "THINKING" in status:
        status_color = YELLOW

    status_text = FONT_SMALL.render(
        status,
        True,
        status_color
    )

    screen.blit(
        status_text,
        (820, 190)
    )

    pygame.draw.line(
        screen,
        GRAY,
        (815, 225),
        (985, 225),
        1
    )

    controls_title = FONT_SMALL.render(
        "CONTROLS",
        True,
        WHITE
    )

    screen.blit(
        controls_title,
        (820, 250)
    )

    controls = [
        "R  - Restart",
        "U  - Undo",
        "ESC - Menu"
    ]

    for i, text in enumerate(controls):

        surface = FONT_SMALL.render(
            text,
            True,
            GRAY
        )

        screen.blit(
            surface,
            (820, 280 + i * 25)
        )

    draw_move_history(history)

    undo_button = Button(
        (820, 650, 150, 45),
        "UNDO",
        BLUE if undo_available else GRAY
    )

    undo_button.draw(screen)

    return undo_button


# ============================================================
# GAME OVER SCREEN
# ============================================================

def game_over_screen(board):

    status = get_game_status(board)

    play_again = Button(
        (300, 430, 180, 55),
        "PLAY AGAIN",
        GREEN
    )

    menu_button = Button(
        (520, 430, 180, 55),
        "MENU",
        BLUE
    )

    while True:

        screen.fill(BACKGROUND)

        title = FONT_TITLE.render(
            "GAME OVER",
            True,
            WHITE
        )

        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 230)
            )
        )

        result = FONT_LARGE.render(
            status,
            True,
            YELLOW
        )

        screen.blit(
            result,
            result.get_rect(
                center=(WIDTH // 2, 320)
            )
        )

        play_again.draw(screen)
        menu_button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "quit"

            if play_again.clicked(event):
                return "again"

            if menu_button.clicked(event):
                return "menu"

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    return "menu"

                if event.key == pygame.K_r:
                    return "again"

        clock.tick(60)


# ============================================================
# PLAY GAME
# ============================================================

def play_game(difficulty):

    board = chess.Board()

    selected_square = None
    last_move = None

    move_history = []

    # Stores position before each complete player turn
    undo_stack = []

    ai_error = False

    while True:

        # ----------------------------------------------------
        # EVENTS
        # ----------------------------------------------------

        events = pygame.event.get()

        for event in events:

            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:

                # Restart
                if event.key == pygame.K_r:

                    board = chess.Board()

                    selected_square = None
                    last_move = None

                    move_history.clear()
                    undo_stack.clear()

                    ai_error = False

                # Undo
                elif event.key == pygame.K_u:

                    if undo_stack:

                        previous_state = (
                            undo_stack.pop()
                        )

                        board = (
                            previous_state["board"]
                        )

                        move_history = (
                            previous_state["history"]
                        )

                        last_move = (
                            previous_state["last_move"]
                        )

                        selected_square = None
                        ai_error = False

                # Menu
                elif event.key == pygame.K_ESCAPE:
                    return "menu"

        # ----------------------------------------------------
        # HUMAN MOVE
        # ----------------------------------------------------

        for event in events:

            if not (
                event.type
                == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                continue

            # Ignore clicks on side panel
            if event.pos[0] >= BOARD_SIZE:
                continue

            if board.turn != chess.WHITE:
                continue

            if board.is_game_over():
                continue

            square = get_square_from_mouse(
                event.pos
            )

            if square is None:
                continue

            # Select piece
            if selected_square is None:

                piece = board.piece_at(
                    square
                )

                if (
                    piece is not None
                    and piece.color == chess.WHITE
                ):

                    selected_square = square

                continue

            # Click same square
            if square == selected_square:

                selected_square = None
                continue

            # Try move
            move = create_human_move(
                board,
                selected_square,
                square
            )

            if move is not None:

                # Save position before complete turn
                undo_stack.append({
                    "board": board.copy(),
                    "history": move_history.copy(),
                    "last_move": last_move
                })

                san = board.san(move)

                board.push(move)

                move_history.append(san)

                last_move = move

                selected_square = None

        # ----------------------------------------------------
        # AI TURN
        # ----------------------------------------------------

        if (
            board.turn == chess.BLACK
            and not board.is_game_over()
            and not ai_error
        ):

            if STOCKFISH_AVAILABLE:

                pygame.event.pump()

                ai_move = get_ai_move(
                    board,
                    difficulty
                )

                if ai_move is not None:

                    san = board.san(
                        ai_move
                    )

                    board.push(
                        ai_move
                    )

                    move_history.append(
                        san
                    )

                    last_move = ai_move

                else:

                    ai_error = True

            else:

                ai_error = True

        # ----------------------------------------------------
        # DRAW
        # ----------------------------------------------------

        screen.fill(BACKGROUND)

        draw_board(
            board,
            selected_square,
            last_move
        )

        undo_button = draw_side_panel(
            board,
            difficulty,
            move_history,
            len(undo_stack) > 0
        )

        # ----------------------------------------------------
        # AI ERROR
        # ----------------------------------------------------

        if ai_error:

            overlay = pygame.Surface(
                (
                    BOARD_SIZE,
                    HEIGHT
                ),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 170)
            )

            screen.blit(
                overlay,
                (0, 0)
            )

            error_title = FONT_LARGE.render(
                "STOCKFISH ERROR",
                True,
                RED
            )

            screen.blit(
                error_title,
                error_title.get_rect(
                    center=(400, 300)
                )
            )

            error_text = FONT_SMALL.render(
                "Check the VS Code terminal",
                True,
                WHITE
            )

            screen.blit(
                error_text,
                error_text.get_rect(
                    center=(400, 345)
                )
            )

            error_text2 = FONT_SMALL.render(
                "Press R to restart",
                True,
                WHITE
            )

            screen.blit(
                error_text2,
                error_text2.get_rect(
                    center=(400, 380)
                )
            )

        pygame.display.flip()

        # ----------------------------------------------------
        # UNDO BUTTON
        # ----------------------------------------------------

        for event in events:

            if (
                event.type
                == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and undo_button.rect.collidepoint(
                    event.pos
                )
            ):

                if undo_stack:

                    previous_state = (
                        undo_stack.pop()
                    )

                    board = (
                        previous_state["board"]
                    )

                    move_history = (
                        previous_state["history"]
                    )

                    last_move = (
                        previous_state["last_move"]
                    )

                    selected_square = None
                    ai_error = False

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        if board.is_game_over():

            result = game_over_screen(
                board
            )

            if result == "quit":
                return "quit"

            if result == "menu":
                return "menu"

            if result == "again":
                return play_game(
                    difficulty
                )

        clock.tick(30)


# ============================================================
# MAIN
# ============================================================

def main():

    if not STOCKFISH_AVAILABLE:

        print()
        print("=" * 60)
        print("STOCKFISH WAS NOT FOUND")
        print("=" * 60)
        print()

        print("Expected Stockfish at:")
        print(STOCKFISH_PATH)

        print()

        print("Make sure stockfish.exe is inside:")
        print(
            "AI-Chess\\stockfish\\stockfish.exe"
        )

        print()

    while True:

        result = main_menu()

        if result == "quit":
            break

        while True:

            difficulty = difficulty_menu()

            if difficulty == "quit":

                pygame.quit()
                sys.exit()

            if difficulty == "back":
                break

            result = play_game(
                difficulty
            )

            if result == "quit":

                pygame.quit()
                sys.exit()

            if result == "menu":
                break

    pygame.quit()

    if engine is not None:

        try:
            engine.quit()
        except Exception:
            pass

    sys.exit()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()