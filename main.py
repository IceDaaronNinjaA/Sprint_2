"""A small Zelda-1-inspired overworld prototype made with Arcade.

The world is an irregular group of screens. Each screen has its own layout, and
some screen exits are blocked so the player has to follow a connected maze.
"""

import random
from pathlib import Path

import arcade


# Game-wide settings.
SCREEN_WIDTH = 768       # 12 tiles wide at 64 pixels per tile
SCREEN_HEIGHT = 576      # 9 tiles tall at 64 pixels per tile
SCREEN_TITLE = "The Nine Fields"
TILE_SIZE = 64
EXTRA_CONNECTION_CHANCE = 0.28
END_SCREEN_SECONDS = 4.0
MIN_SCREENS = 20
MAX_SCREENS = 25

# Sprite.change_x/change_y are pixels per update, not pixels per second. A
# small value makes movement visible instead of making the player jump.
PLAYER_SPEED = 3
PLAYER_SCALE = 0.45

# Temporary testing aid. Set this to False later to remove the screen label.
SHOW_DEBUG_LABELS = True
BUTTON_WIDTH = 260
BUTTON_HEIGHT = 58
START_BUTTON_Y = 300
EXIT_BUTTON_Y = 215
MENU_BUTTON_Y = 220

# Arcade's built-in top-down tiles line up on a 64-by-64 grid and are
# automatically included by the project's PyInstaller hook.
GRASS_TEXTURE = ":resources:images/topdown_tanks/tileGrass1.png"
GRASS_2_TEXTURE = ":resources:images/topdown_tanks/tileGrass2.png"
ROAD_EAST_TEXTURE = ":resources:images/topdown_tanks/tileGrass_roadEast.png"
ROAD_NORTH_TEXTURE = ":resources:images/topdown_tanks/tileGrass_roadNorth.png"
ROAD_CROSSING_TEXTURE = ":resources:images/topdown_tanks/tileGrass_roadCrossing.png"
TREE_TEXTURE = ":resources:images/topdown_tanks/treeGreen_large.png"
SMALL_TREE_TEXTURE = ":resources:images/topdown_tanks/treeGreen_small.png"
ROCK_TEXTURE = ":resources:images/tiles/rock.png"
BUSH_TEXTURE = ":resources:images/tiles/bush.png"
WALL_TEXTURE = ":resources:images/tiles/boxCrate_double.png"
COIN_TEXTURE = ":resources:images/items/coinGold.png"
PLAYER_TEXTURE = ":resources:images/animated_characters/robot/robot_idle.png"

# These are layout templates. The irregular world reuses and shuffles these
# templates so every screen still has scenery without requiring 20-25 hand-made
# layouts. Positions are tile coordinates, not pixel coordinates.
SCREEN_CONFIGS = {
    (0, 0): {
        "ground": GRASS_TEXTURE,
        "obstacles": [(1, 1, TREE_TEXTURE, 1.0), (9, 1, ROCK_TEXTURE, 0.5),
                       (2, 7, BUSH_TEXTURE, 0.5)],
        "walls": [(2, 6), (3, 6), (4, 6), (8, 2), (8, 3), (8, 4)],
    },
    (1, 0): {
        "ground": GRASS_2_TEXTURE,
        "obstacles": [(1, 2, ROCK_TEXTURE, 0.5), (10, 2, TREE_TEXTURE, 1.0),
                       (2, 7, SMALL_TREE_TEXTURE, 1.0)],
        "walls": [(2, 2), (3, 2), (4, 2), (8, 6), (9, 6), (10, 6)],
    },
    (2, 0): {
        "ground": GRASS_TEXTURE,
        "obstacles": [(1, 7, BUSH_TEXTURE, 0.5), (10, 1, ROCK_TEXTURE, 0.5),
                       (9, 7, TREE_TEXTURE, 1.0)],
        "walls": [(2, 6), (2, 7), (2, 8), (8, 1), (8, 2), (8, 3)],
    },
    (0, 1): {
        "ground": GRASS_2_TEXTURE,
        "obstacles": [(1, 1, SMALL_TREE_TEXTURE, 1.0), (10, 1, ROCK_TEXTURE, 0.5),
                       (2, 7, TREE_TEXTURE, 1.0), (9, 7, BUSH_TEXTURE, 0.5)],
        "walls": [(2, 2), (3, 2), (4, 2), (8, 6), (9, 6)],
    },
    (1, 1): {
        "ground": GRASS_TEXTURE,
        "obstacles": [(1, 1, TREE_TEXTURE, 1.0), (10, 1, ROCK_TEXTURE, 0.5),
                       (1, 7, ROCK_TEXTURE, 0.5), (10, 7, TREE_TEXTURE, 1.0)],
        # These barriers cross parts of the roads but leave openings so the
        # player can go around them using the other lane.
        "walls": [(2, 4), (3, 4), (4, 4), (8, 4), (9, 4),
                  (6, 1), (6, 2), (6, 6), (6, 7)],
    },
    (2, 1): {
        "ground": GRASS_2_TEXTURE,
        "obstacles": [(1, 2, ROCK_TEXTURE, 0.5), (9, 2, BUSH_TEXTURE, 0.5),
                       (2, 7, TREE_TEXTURE, 1.0), (10, 7, SMALL_TREE_TEXTURE, 1.0)],
        "walls": [(2, 6), (3, 6), (4, 6), (8, 2), (8, 3), (8, 4)],
    },
    (0, 2): {
        "ground": GRASS_TEXTURE,
        "obstacles": [(1, 1, BUSH_TEXTURE, 0.5), (10, 1, TREE_TEXTURE, 1.0),
                       (2, 7, ROCK_TEXTURE, 0.5)],
        "walls": [(2, 2), (3, 2), (4, 2), (8, 6), (9, 6), (10, 6)],
    },
    (1, 2): {
        "ground": GRASS_2_TEXTURE,
        "obstacles": [(1, 7, ROCK_TEXTURE, 0.5), (10, 7, BUSH_TEXTURE, 0.5),
                       (2, 1, TREE_TEXTURE, 1.0), (9, 1, SMALL_TREE_TEXTURE, 1.0)],
        "walls": [(2, 6), (2, 7), (2, 8), (8, 1), (8, 2), (8, 3)],
    },
    (2, 2): {
        "ground": GRASS_TEXTURE,
        "obstacles": [(1, 1, TREE_TEXTURE, 1.0), (10, 1, BUSH_TEXTURE, 0.5),
                       (1, 7, ROCK_TEXTURE, 0.5), (10, 7, TREE_TEXTURE, 1.0)],
        "walls": [(2, 2), (3, 2), (4, 2), (8, 6), (9, 6), (10, 6)],
    },
}


class GameWindow(arcade.Window):
    """The game window and the current screen in the irregular world."""

    def __init__(self):
        """Create the window and prepare the menu and player objects."""
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.background_color = arcade.color.DARK_SPRING_GREEN

        # The world is generated only after the player clicks START GAME.
        self.game_state = "menu"
        self.map_cells = frozenset()
        self.screen_positions = []
        self.map_screen_count = 0
        self.screen_layouts = {}
        self.open_connections = set()
        self.start_screen = None
        self.goal_screen = None
        self.screen_column = 0
        self.screen_row = 0
        self.visited_screens = set()
        self.game_won = False
        self.end_screen_timer = 0.0

        self.player = arcade.Sprite(PLAYER_TEXTURE, scale=PLAYER_SCALE)
        self.player.center_x = SCREEN_WIDTH / 2
        self.player.center_y = SCREEN_HEIGHT / 2
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        self.ground_list = arcade.SpriteList()
        self.obstacle_list = arcade.SpriteList(use_spatial_hash=True)
        self.path_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.coin = None
        self.physics_engine = None

    def start_game(self):
        """Start a fresh run and randomize the map after a menu click."""
        self.map_cells = self.create_random_shape()
        self.screen_positions = sorted(
            self.map_cells, key=lambda item: (item[1], item[0])
        )
        self.map_screen_count = len(self.screen_positions)
        self.screen_layouts = self.create_random_screen_layouts()
        self.open_connections, self.start_screen, self.goal_screen = (
            self.create_random_maze()
        )
        self.screen_column, self.screen_row = self.start_screen
        self.visited_screens = {self.start_screen}
        self.game_won = False
        self.end_screen_timer = 0.0
        self.game_state = "playing"
        self.write_current_map()
        self.player.center_x = SCREEN_WIDTH / 2
        self.player.center_y = SCREEN_HEIGHT / 2
        self.player.change_x = 0
        self.player.change_y = 0
        self.build_screen()

    def return_to_menu(self):
        """Return to the menu so the player can start another random run."""
        self.game_state = "menu"
        self.game_won = False
        self.player.change_x = 0
        self.player.change_y = 0

    @property
    def current_screen(self):
        """Return the layout data for the screen the player is visiting."""
        return self.screen_layouts[(self.screen_column, self.screen_row)]

    def create_random_screen_layouts(self):
        """Shuffle scenery templates and assign one to every screen.

        There are fewer templates than screens on purpose. Reusing templates
        keeps the code manageable while shuffling them makes each run look
        different.
        """
        layouts = list(SCREEN_CONFIGS.values())
        layouts = [
            layouts[index % len(layouts)]
            for index in range(len(self.screen_positions))
        ]
        random.shuffle(layouts)
        return dict(zip(self.screen_positions, layouts))

    def create_random_shape(self):
        """Grow a connected irregular shape containing 20 to 25 screens.

        The first cell is the seed. Each new cell is added next to an existing
        cell, so the shape itself can never split into disconnected pieces.
        """
        target_size = random.randint(MIN_SCREENS, MAX_SCREENS)
        cells = {(0, 0)}
        while len(cells) < target_size:
            # Frontier means every empty cell that touches the shape.
            frontier = set()
            for column, row in cells:
                frontier.update({
                    (column - 1, row),
                    (column + 1, row),
                    (column, row - 1),
                    (column, row + 1),
                })
            frontier -= cells
            cells.add(random.choice(tuple(frontier)))
        min_column = min(column for column, row in cells)
        min_row = min(row for column, row in cells)
        return frozenset(
            (column - min_column, row - min_row) for column, row in cells
        )

    def create_random_maze(self):
        """Create a random connected maze and choose two dead-end screens.

        A randomized depth-first search creates a spanning tree first, which
        guarantees that every screen is reachable. Extra nearby connections
        are then added to create loops and more branching paths. Two protected
        leaves stay as the start and coin dead ends.
        """
        maze_edges = set()
        visited = {random.choice(self.screen_positions)}
        search_stack = list(visited)

        while search_stack:
            # Depth-first search walks forward until it reaches a dead end,
            # then backs up and chooses another unexplored branch.
            current = search_stack[-1]
            column, row = current
            candidates = [
                (column + 1, row),
                (column - 1, row),
                (column, row + 1),
                (column, row - 1),
            ]
            candidates = [
                position
                for position in candidates
                if position in self.map_cells and position not in visited
            ]
            if not candidates:
                search_stack.pop()
                continue

            next_screen = random.choice(candidates)
            maze_edges.add(frozenset({current, next_screen}))
            visited.add(next_screen)
            search_stack.append(next_screen)

        degrees = {position: 0 for position in self.screen_positions}
        for edge in maze_edges:
            for position in edge:
                degrees[position] += 1
        dead_ends = [position for position, degree in degrees.items() if degree == 1]
        start_screen, goal_screen = random.sample(dead_ends, 2)

        # Add loops without touching the two protected dead ends. These extra
        # edges are what make the map feel less like one straight solution.
        possible_edges = []
        for position in self.screen_positions:
            column, row = position
            for neighbor in ((column + 1, row), (column, row + 1)):
                if neighbor in self.map_cells:
                    edge = frozenset({position, neighbor})
                    if edge not in maze_edges:
                        possible_edges.append(edge)
        random.shuffle(possible_edges)
        for edge in possible_edges:
            if start_screen in edge or goal_screen in edge:
                continue
            if random.random() < EXTRA_CONNECTION_CHANCE:
                maze_edges.add(edge)

        return maze_edges, start_screen, goal_screen

    def display_position(self, position):
        """Convert zero-based code coordinates to one-based map coordinates."""
        return f"{position[0] + 1},{position[1] + 1}"

    def neighbors_for(self, position):
        """Return valid neighboring positions for any irregular map cell.

        A missing neighbor means that side is an outside edge of the shape.
        A present neighbor may still be blocked if its edge is not in
        self.open_connections.
        """
        column, row = position
        candidates = {
            "left": (column - 1, row),
            "right": (column + 1, row),
            "down": (column, row - 1),
            "up": (column, row + 1),
        }
        return {
            direction: neighbor
            for direction, neighbor in candidates.items()
            if neighbor in self.map_cells
        }

    def write_current_map(self):
        """Write this run's actual randomized connections to MAP.txt.

        This is useful while learning and debugging. If a packaged build is
        installed somewhere read-only, the write is skipped and the game keeps
        running normally.
        """
        lines = [
            "THE NINE FIELDS - CURRENT RANDOM MAP",
            "====================================",
            "",
            "This file is regenerated every time the game starts.",
            "Screen coordinates start at 1 for easier reading.",
            f"Total screens: {self.map_screen_count}",
            f"Start dead end: {self.display_position(self.start_screen)}",
            f"Coin dead end: {self.display_position(self.goal_screen)}",
            "",
            "OPEN CONNECTIONS",
            "-----------------",
        ]
        for position in self.screen_positions:
            exits = []
            for direction, neighbor in self.neighbors_for(position).items():
                if self.edge_is_open(position, neighbor):
                    exits.append(f"{direction} to {self.display_position(neighbor)}")
            lines.append(
                f"SCREEN {self.display_position(position)}: "
                + ("; ".join(exits) if exits else "dead end")
            )
        lines.extend([
            "",
            "Any neighboring screen not listed above is blocked by a wall.",
            "The minimap grows as screens are visited.",
        ])
        try:
            Path(__file__).with_name("MAP.txt").write_text(
                "\n".join(lines) + "\n", encoding="utf-8"
            )
        except OSError:
            # A packaged application may be running from a read-only folder.
            # The game still works; only the optional text export is skipped.
            pass

    def build_screen(self):
        """Create this screen's complete drawing and collision lists.

        The old lists are replaced because a screen transition should not
        leave trees or walls from the previous screen behind.
        """
        self.ground_list = arcade.SpriteList()
        self.path_list = arcade.SpriteList()
        self.obstacle_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_list = arcade.SpriteList()
        self.coin = None
        config = self.current_screen

        # Fill the screen with the current screen's grass variant.
        for row in range(SCREEN_HEIGHT // TILE_SIZE):
            for column in range(SCREEN_WIDTH // TILE_SIZE):
                tile = arcade.Sprite(config["ground"])
                tile.center_x = column * TILE_SIZE + TILE_SIZE / 2
                tile.center_y = row * TILE_SIZE + TILE_SIZE / 2
                self.ground_list.append(tile)

        # The center roads line up with every neighboring screen.
        middle_column = (SCREEN_WIDTH // TILE_SIZE) // 2
        middle_row = (SCREEN_HEIGHT // TILE_SIZE) // 2
        for column in range(SCREEN_WIDTH // TILE_SIZE):
            self.add_path_tile(ROAD_EAST_TEXTURE, column, middle_row)
        for row in range(SCREEN_HEIGHT // TILE_SIZE):
            self.add_path_tile(ROAD_NORTH_TEXTURE, middle_column, row)
        self.add_path_tile(ROAD_CROSSING_TEXTURE, middle_column, middle_row)

        # Add the screen-specific interior maze walls.
        for column, row in config["walls"]:
            self.add_obstacle(WALL_TEXTURE, column, row, 0.5)

        # Add this screen's trees, rocks, and bushes.
        for column, row, texture, scale in config["obstacles"]:
            self.add_obstacle(texture, column, row, scale)

        # The goal is a collectible rather than an automatic screen change.
        # The player must walk onto the coin to finish the maze.
        if (self.screen_column, self.screen_row) == self.goal_screen:
            self.coin = arcade.Sprite(COIN_TEXTURE, scale=0.65)
            self.coin.center_x = SCREEN_WIDTH / 2
            self.coin.center_y = SCREEN_HEIGHT / 2
            self.coin_list.append(self.coin)

        # Show a solid wall along every closed side. This includes both maze
        # gates and the outside border of the irregular test world.
        current = (self.screen_column, self.screen_row)
        for direction in ("left", "right", "down", "up"):
            neighbor = self.neighbors().get(direction)
            if neighbor is None or not self.edge_is_open(current, neighbor):
                self.add_edge_wall(direction)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.obstacle_list
        )

    def add_path_tile(self, texture, column, row):
        """Add one path tile at a grid location."""
        tile = arcade.Sprite(texture)
        tile.center_x = column * TILE_SIZE + TILE_SIZE / 2
        tile.center_y = row * TILE_SIZE + TILE_SIZE / 2
        self.path_list.append(tile)

    def add_obstacle(self, texture, column, row, scale):
        """Create a collidable sprite at a grid location."""
        obstacle = arcade.Sprite(texture, scale=scale)
        obstacle.center_x = column * TILE_SIZE + TILE_SIZE / 2
        obstacle.center_y = row * TILE_SIZE + TILE_SIZE / 2
        self.obstacle_list.append(obstacle)

    def neighbors(self):
        """Return neighboring screens for the current irregular map cell."""
        return self.neighbors_for((self.screen_column, self.screen_row))

    def edge_is_open(self, current, neighbor):
        """Return whether the two screens have a usable connection."""
        return frozenset({current, neighbor}) in self.open_connections

    def add_edge_wall(self, direction):
        """Put a full wall of objects along a closed screen edge."""
        if direction == "left":
            for row in range(SCREEN_HEIGHT // TILE_SIZE):
                self.add_obstacle(WALL_TEXTURE, 0, row, 0.5)
        elif direction == "right":
            for row in range(SCREEN_HEIGHT // TILE_SIZE):
                self.add_obstacle(
                    WALL_TEXTURE, SCREEN_WIDTH // TILE_SIZE - 1, row, 0.5
                )
        elif direction == "down":
            for column in range(SCREEN_WIDTH // TILE_SIZE):
                self.add_obstacle(WALL_TEXTURE, column, 0, 0.5)
        elif direction == "up":
            for column in range(SCREEN_WIDTH // TILE_SIZE):
                self.add_obstacle(
                    WALL_TEXTURE, column, SCREEN_HEIGHT // TILE_SIZE - 1, 0.5
                )

    def on_draw(self):
        """Draw the current screen from back to front."""
        self.clear()

        if self.game_state == "menu":
            self.draw_menu()
            return

        # Once the maze goal is reached, replace the map with a simple end
        # screen. The player can return to the menu for another random run.
        if self.game_won:
            arcade.draw_text(
                "THE END",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 35,
                arcade.color.WHITE,
                38,
                anchor_x="center",
            )
            arcade.draw_text(
                "You collected the golden coin!",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 20,
                arcade.color.WHITE,
                18,
                anchor_x="center",
            )
            self.draw_button("RETURN TO MENU", MENU_BUTTON_Y)
            return

        self.ground_list.draw()
        self.path_list.draw()
        self.coin_list.draw()
        self.obstacle_list.draw()
        self.player_list.draw()
        self.draw_minimap()

        # Keep only the screen coordinate visible while testing navigation.
        # The directional OPEN/BLOCKED labels were intentionally removed so
        # the game world stays visually clean.
        if SHOW_DEBUG_LABELS:
            arcade.draw_text(
                f"Screen {self.screen_column + 1}, {self.screen_row + 1} / {self.map_screen_count}",
                12,
                SCREEN_HEIGHT - 28,
                arcade.color.WHITE,
                16,
            )

    def draw_button(self, label, center_y):
        """Draw one menu button centered at the requested y coordinate."""
        left = (SCREEN_WIDTH - BUTTON_WIDTH) / 2
        bottom = center_y - BUTTON_HEIGHT / 2
        arcade.draw_lbwh_rectangle_filled(
            left, bottom, BUTTON_WIDTH, BUTTON_HEIGHT, arcade.color.DARK_BLUE
        )
        arcade.draw_lbwh_rectangle_outline(
            left, bottom, BUTTON_WIDTH, BUTTON_HEIGHT, arcade.color.WHITE, 3
        )
        arcade.draw_text(
            label,
            SCREEN_WIDTH / 2,
            center_y - 10,
            arcade.color.WHITE,
            18,
            anchor_x="center",
        )

    def draw_menu(self):
        """Draw the mouse-controlled start menu."""
        arcade.draw_text(
            "THE NINE FIELDS",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 150,
            arcade.color.WHITE,
            34,
            anchor_x="center",
        )
        arcade.draw_text(
            "A new maze is created every time you play",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 195,
            arcade.color.WHITE,
            16,
            anchor_x="center",
        )
        self.draw_button("START GAME", START_BUTTON_Y)
        self.draw_button("EXIT GAME", EXIT_BUTTON_Y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle menu buttons clicked with the mouse."""
        left = (SCREEN_WIDTH - BUTTON_WIDTH) / 2
        right = left + BUTTON_WIDTH

        def clicked(center_y):
            bottom = center_y - BUTTON_HEIGHT / 2
            return left <= x <= right and bottom <= y <= bottom + BUTTON_HEIGHT

        if self.game_state == "menu":
            if clicked(START_BUTTON_Y):
                self.start_game()
            elif clicked(EXIT_BUTTON_Y):
                arcade.close_window()
        elif self.game_won and clicked(MENU_BUTTON_Y):
            self.return_to_menu()

    def draw_minimap(self):
        """Draw a small map that grows as the player visits screens."""
        cell_size = 14
        min_column = min(position[0] for position in self.map_cells)
        min_row = min(position[1] for position in self.map_cells)
        max_column = max(position[0] for position in self.map_cells)
        max_row = max(position[1] for position in self.map_cells)
        map_width = (max_column - min_column + 1) * cell_size
        map_height = (max_row - min_row + 1) * cell_size
        origin_x = SCREEN_WIDTH - map_width - 18
        origin_y = SCREEN_HEIGHT - map_height - 18

        arcade.draw_lbwh_rectangle_filled(
            origin_x - 6,
            origin_y - 6,
            map_width + 12,
            map_height + 12,
            arcade.color.BLACK,
        )

        def center(position):
            return (
                origin_x + (position[0] - min_column) * cell_size + cell_size / 2,
                origin_y + (position[1] - min_row) * cell_size + cell_size / 2,
            )

        # Only draw connections between screens the player has discovered.
        for edge in self.open_connections:
            first, second = tuple(edge)
            if first in self.visited_screens and second in self.visited_screens:
                x1, y1 = center(first)
                x2, y2 = center(second)
                arcade.draw_line(x1, y1, x2, y2, arcade.color.DARK_GRAY, 3)

        for position in self.visited_screens:
            x, y = center(position)
            color = (
                arcade.color.YELLOW
                if position == (self.screen_column, self.screen_row)
                else arcade.color.GREEN
            )
            arcade.draw_lbwh_rectangle_filled(
                x - (cell_size - 3) / 2,
                y - (cell_size - 3) / 2,
                cell_size - 3,
                cell_size - 3,
                color,
            )

    def on_key_press(self, key, modifiers):
        """Start movement when an arrow key or WASD key is pressed."""
        if key in (arcade.key.UP, arcade.key.W):
            self.player.change_y = PLAYER_SPEED
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.player.change_y = -PLAYER_SPEED
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.player.change_x = -PLAYER_SPEED
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.player.change_x = PLAYER_SPEED

    def on_key_release(self, key, modifiers):
        """Stop movement when a direction key is released."""
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.W, arcade.key.S):
            self.player.change_y = 0
        elif key in (arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D):
            self.player.change_x = 0

    def on_update(self, delta_time):
        """Move the player, handle walls, and change screens at open gates.

        Arcade calls this once per frame. It is also where coin pickup,
        discovered-screen tracking, and the timed ending are handled.
        """
        if self.game_state == "menu" or self.game_won:
            return

        self.physics_engine.update()

        current = (self.screen_column, self.screen_row)
        neighbors = self.neighbors()

        # A player can only transition through a gate that is part of the
        # connected maze. Closed gates are also drawn as collidable walls.
        if self.player.left < 0:
            if "left" in neighbors and self.edge_is_open(current, neighbors["left"]):
                self.screen_column -= 1
                self.player.right = SCREEN_WIDTH - 2
                self.build_screen()
            else:
                self.player.left = 0
        elif self.player.right > SCREEN_WIDTH:
            if "right" in neighbors and self.edge_is_open(current, neighbors["right"]):
                self.screen_column += 1
                self.player.left = 2
                self.build_screen()
            else:
                self.player.right = SCREEN_WIDTH

        current = (self.screen_column, self.screen_row)
        neighbors = self.neighbors()
        if self.player.bottom < 0:
            if "down" in neighbors and self.edge_is_open(current, neighbors["down"]):
                self.screen_row -= 1
                self.player.top = SCREEN_HEIGHT - 2
                self.build_screen()
            else:
                self.player.bottom = 0
        elif self.player.top > SCREEN_HEIGHT:
            if "up" in neighbors and self.edge_is_open(current, neighbors["up"]):
                self.screen_row += 1
                self.player.bottom = 2
                self.build_screen()
            else:
                self.player.top = SCREEN_HEIGHT

        # Record the current screen after any transition so the minimap grows.
        self.visited_screens.add((self.screen_column, self.screen_row))

        # The maze ends when the player collects the coin in the randomly
        # selected goal dead end. Give the end screen time to be seen.
        if self.coin is not None and arcade.check_for_collision(self.player, self.coin):
            self.game_won = True
            self.game_state = "won"
            self.end_screen_timer = END_SCREEN_SECONDS
            self.coin.remove_from_sprite_lists()
            self.coin = None
            self.player.change_x = 0
            self.player.change_y = 0


def main():
    """Create the window and start Arcade's event loop."""
    GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()
