"""
Simple program to show moving a sprite with the keyboard.

This program uses the Arcade library found at http://arcade.academy

Artwork from https://kenney.nl/assets/space-shooter-redux

"""

import arcade
import math
import random
from enum import Enum, auto


SPRITE_SCALING = 0.5

# Set the size of the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Variables controlling the player

PLAYER_LIVES = 3
PLAYER_ROTATE_SPEED = 5
PLAYER_THRUST = 0.05  # speed gained from thrusting
PLAYER_GRAPHICS_CORRECTION = math.pi / 2  # the player graphic is turned 45 degrees too much compared to actual angle
PLAYER_START_X = SCREEN_WIDTH // 2
PLAYER_START_Y = 50
PLAYER_LIVES = 3
PLAYER_SPEED = 3
PLAYER_SHOT_SPEED = 4
PLAYER_SHOT_RANGE = SCREEN_WIDTH // 2

PLAYER_THRUST_KEY = arcade.key.UP
PLAYER_FIRE_KEY = arcade.key.SPACE

# Asteroids variables
ASTEROIDS_PR_LEVEL = 5
ASTEROIDS_SPEED = 1.

# UFO constants
UFO_SPEED = 2  # both for x and y note: has to be int
UFO_DIR_CHANGE_RATE = 3
UFO_SPAWN_RATE = 10  # seconds
UFO_POINTS_REWARD = 300
UFO_SHOT_SPEED = 2
UFO_FIRE_RATE = 1.5
UFO_SIZE_SMALL = 0.9
UFO_SIZE_BIG = 1.5

# intro screen constants
PLAY_BUTTON_X = SCREEN_WIDTH // 2
PLAY_BUTTON_Y = SCREEN_HEIGHT // 2

TITLE_X = SCREEN_WIDTH // 2
TITLE_Y = SCREEN_HEIGHT * 0.75


def wrap(sprite: arcade.Sprite):
    """
    if sprite is off-screen move it to the other side of the screen
    """

    if sprite.right < 0:
        sprite.center_x += SCREEN_WIDTH
    elif sprite.left > SCREEN_WIDTH:
        sprite.center_x -= SCREEN_WIDTH

    if sprite.top < 0:
        sprite.center_y += SCREEN_HEIGHT
    elif sprite.bottom > SCREEN_HEIGHT:
        sprite.center_y -= SCREEN_HEIGHT



def wrap(sprite: arcade.Sprite):
    """
    if sprite is off-screen move it to the other side of the screen
    """

    if sprite.right < 0:
        sprite.center_x += SCREEN_WIDTH
    elif sprite.left > SCREEN_WIDTH:
        sprite.center_x -= SCREEN_WIDTH

    if sprite.top < 0:
        sprite.center_y += SCREEN_HEIGHT
    elif sprite.bottom > SCREEN_HEIGHT:
        sprite.center_y -= SCREEN_HEIGHT


class Player(arcade.Sprite):
    """
    The player
    """

    def __init__(self, center_x, center_y, lives, scale):
        """
        Setup new Player object
        """
        # Graphics to use for Player
        super().__init__("images/playerShip1_red.png")

        self.angle = 0
        self.lives = lives
        self.scale = scale
        self.center_x = center_x
        self.center_y = center_y

    def thrust(self):
        """
        increase speed in the direction pointing
        """

        self.change_x += math.cos(self.radians + PLAYER_GRAPHICS_CORRECTION) * PLAYER_THRUST
        self.change_y += math.sin(self.radians + PLAYER_GRAPHICS_CORRECTION) * PLAYER_THRUST

    def update(self):
        """
        Move the sprite and wrap
        """

        self.center_x += self.change_x
        self.center_y += self.change_y

        # wrap
        wrap(self)


class Asteroid(arcade.Sprite):
    
    def __init__(self):
        
        # Initialize the asteroid
        
        # Graphics
        super().__init__(
            filename="images/Meteors/meteorGrey_big1.png", 
            scale=SPRITE_SCALING
        )

        self.angle = arcade.rand_angle_360_deg()
        self.center_x = random.randint(0, SCREEN_WIDTH)
        self.center_y = random.randint(0, SCREEN_HEIGHT)
        self.change_x = math.sin(self.radians) * ASTEROIDS_SPEED
        self.change_y = math.cos(self.radians) * ASTEROIDS_SPEED
        
    def update(self):
         
        # Update position
        self.center_x += self.change_x
        self.center_y += self.change_y

        # wrap
        wrap(self)


class PlayerShot(arcade.Sprite):
    """
    A shot fired by the Player
    """

    def __init__(self, center_x=0, center_y=0):
        """
        Setup new PlayerShot object
        """

        # Set the graphics to use for the sprite
        super().__init__("images/Lasers/laserBlue01.png", SPRITE_SCALING)

        self.center_x = center_x
        self.center_y = center_y
        self.change_y = PLAYER_SHOT_SPEED
        self.distance_traveled = 0
        self.speed = PLAYER_SHOT_SPEED

    def update(self):
        """
        Move the sprite
        """

        # Update position
        self.center_x += self.change_x
        self.center_y += self.change_y

        # wrap
        wrap(self)

        # Has a range of how long the shot can last for
        self.distance_traveled += self.speed

        # When distance made kill it
        if self.distance_traveled > PLAYER_SHOT_RANGE:
            self.kill()


class UFOShot(arcade.Sprite):
    """shot fired by the ufo"""

    def __int__(self, **kwargs):
        super().__init__(**kwargs)

    def update(self):
        """update position/kill if out of bounds"""

        self.center_x += self.change_x
        self.center_y += self.change_y

        self.angle = ((self.change_x / self.change_y) * -90)  # set ange based on our direction

        # kill if out of bounds
        if self.center_x > SCREEN_WIDTH or self.center_x < 0 and self.center_y > SCREEN_HEIGHT or self.center_y < 0:
            self.kill()


class BonusUFO(arcade.Sprite):
    """occasionally moves across the screen. Grants the player points if shot"""

    def __int__(self, shot_list, **kwargs):

        kwargs['filename'] = "images/ufoBlue.png"

        # UFO's are big or small
        kwargs['scale'] = SPRITE_SCALING * random.choice([UFO_SIZE_SMALL, UFO_SIZE_BIG])

        # set random position off-screen
        kwargs['center_x'] = random.choice([0, SCREEN_WIDTH])
        kwargs['center_y'] = random.choice([0, SCREEN_HEIGHT])

        # send arguments upstairs
        super().__init__(**kwargs)

        self.shot_list = shot_list

        # set random direction. always point towards center, with noise
        self.change_x = random.randrange(1, UFO_SPEED)
        if self.center_x > SCREEN_WIDTH / 2:
            self.change_x *= -1

        self.change_y = UFO_SPEED - self.change_x
        if self.center_y > SCREEN_HEIGHT / 2:
            self.change_y *= -1

        # setup direction changing
        arcade.schedule(self.change_dir, UFO_DIR_CHANGE_RATE)

        # setup shooting
        arcade.schedule(self.shoot, UFO_FIRE_RATE)

    def change_dir(self, delta_time):
        """
        set a new direction
        """

        r = random.randrange(-UFO_SPEED, UFO_SPEED)
        self.change_x -= r
        self.change_y += r

    def shoot(self, delta_time):
        """
        fire a new shot
        """

        new_ufo_shot = UFOShot()  # sprites created with arcade.schedule don't __init__ it has to be manually called
        new_ufo_shot.__init__(
            filename="images/Lasers/laserGreen07.png",
            scale=SPRITE_SCALING,
            center_x=self.center_x,
            center_y=self.center_y
            )

        new_ufo_shot.change_x = random.randrange(-UFO_SHOT_SPEED, UFO_SHOT_SPEED)
        new_ufo_shot.change_y = new_ufo_shot.change_x - UFO_SHOT_SPEED
        self.shot_list.append(new_ufo_shot)

    def update(self):
        """update position, and kill if out of bounds"""

        # keep spinning. just for graphics purposes
        self.angle += self.change_x + self.change_y  # the faster it moves, the faster it spins.

        self.center_x += self.change_x
        self.center_y += self.change_y

        # kill if out of bounds
        if self.center_x > SCREEN_WIDTH or self.center_x < 0 or self.center_y > SCREEN_HEIGHT or self.center_y < 0:
            self.destroy()

    def destroy(self):
        """
        kill the sprite and unschedule all functions
        """

        arcade.unschedule(self.shoot)
        arcade.unschedule(self.change_dir)
        self.kill()


class GameState(Enum):
    """
    the state of the game: INTRO, IN_GAME or GAME_OVER
    """

    INTRO = auto()
    IN_GAME = auto()
    GAME_OVER = auto()


class InGameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__()

        # game state variable.
        self.game_state = None

        # Variable that will hold a list of shots fired by the player
        self.player_shot_list = None

        # Asteroid SpriteList
        self.asteroid_list = None

        # Set up the player info
        self.player_sprite: Player = None
        self.player_score = None
        self.player_lives = None
        self.player_speed = 0
        self.opposite_angle = 0
        self.max_speed = PLAYER_SPEED

        # set up ufo info
        self.ufo_list = None
        self.ufo_shot_list = None

        # UI
        self.play_button = None
        self.title_graphics = None

        # Track the current state of what key is pressed
        self.space_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.thrust_pressed = False

        # Get list of joysticks
        joysticks = arcade.get_joysticks()

        if joysticks:
            print("Found {} joystick(s)".format(len(joysticks)))

            # Use 1st joystick found
            self.joystick = joysticks[0]

            # Communicate with joystick
            self.joystick.open()

            # Map joysticks functions to local functions
            self.joystick.on_joybutton_press = self.on_joybutton_press
            self.joystick.on_joybutton_release = self.on_joybutton_release
            self.joystick.on_joyaxis_motion = self.on_joyaxis_motion
            self.joystick.on_joyhat_motion = self.on_joyhat_motion

        else:
            print("No joysticks found")
            self.joystick = None

            # self.joystick.
        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def spawn_ufo(self, delta_time):
        """
        spawns an ufo object into self.ufo_list.
        has to take delta_time because it needs to be called by arcade.schedule
        """

        new_ufo_obj = BonusUFO()
        new_ufo_obj.__int__(self.ufo_shot_list)  # it needs the list so it can send shots to MyGame
        self.ufo_list.append(new_ufo_obj)

    def on_show_view(self):
        """ Set up the game and initialize the variables. """

        self.game_state = GameState.INTRO

        # No points when the game starts
        self.player_score = 0

        # Sprite lists
        self.player_shot_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()

        self.ufo_list = arcade.SpriteList()
        self.ufo_shot_list = arcade.SpriteList()

        # Create a Player object
        self.player_sprite = Player(
            center_x=PLAYER_START_X,
            center_y=PLAYER_START_Y,
            lives=PLAYER_LIVES,
            scale=SPRITE_SCALING
        )
        
        # Spawn Asteroids
        for r in range(ASTEROIDS_PR_LEVEL):
            self.asteroid_list.append(Asteroid())

        # setup spawn_ufo to run regularly
        arcade.schedule(self.spawn_ufo, UFO_SPAWN_RATE)

        # create UI objs
        self.title_graphics = arcade.load_texture("images/UI/asteroidsTitle.png")
        self.play_button = arcade.load_texture("images/UI/asteroidsStartButton.png")

    def on_draw(self):
        """
        Render the screen.
        """

        # always

        # This command has to happen before we start drawing
        arcade.start_render()

        # only in intro
        if self.game_state == GameState.INTRO:

            self.title_graphics.draw_scaled(
                center_x=TITLE_X,
                center_y=TITLE_Y
            )

            self.play_button.draw_scaled(
                center_x=PLAY_BUTTON_X,
                center_y=PLAY_BUTTON_Y,
            )

        # only in-game
        elif self.game_state == GameState.IN_GAME:

            # Draw the player shot
            self.player_shot_list.draw()

            # Draw the player sprite
            self.player_sprite.draw()

            # Draw asteroids
            self.asteroid_list.draw()

            # draw ufo(s)
            self.ufo_list.draw()

            # and their shots
            self.ufo_shot_list.draw()

            # Draw players score on screen
            arcade.draw_text(
                "SCORE: {}".format(self.player_score),  # Text to show
                10,  # X position
                SCREEN_HEIGHT - 20,  # Y_position
                arcade.color.WHITE  # Color of text
            )
            arcade.draw_text(
                "LIVES: {}".format(self.player_sprite.lives),  # Text to show
                10,  # X position
                SCREEN_HEIGHT - 45, # Y positon
                arcade.color.WHITE  # Color of text
            )

        # only post-game
        elif self.game_state == GameState.GAME_OVER:
            pass

    def on_update(self, delta_time):
        """
        Movement and game logic
        """

        if self.game_state == GameState.IN_GAME:
            # Calculate player speed based on the keys pressed
            # Move player with keyboard
            if self.left_pressed and not self.right_pressed:
                self.player_sprite.angle+= PLAYER_ROTATE_SPEED
            elif self.right_pressed and not self.left_pressed:
                self.player_sprite.angle+= -PLAYER_ROTATE_SPEED

            # rotate player with joystick if present
            if self.joystick:
                self.player_sprite.angle += round(self.joystick.x) * -PLAYER_ROTATE_SPEED

            # checks if ufo shot collides with player
            if any(self.player_sprite.collides_with_list(self.ufo_shot_list)):
                self.player_sprite.lives -= 1

            #player shot
            for shot in self.player_shot_list:

                for ufo_hit in arcade.check_for_collision_with_list(shot, self.ufo_list):
                    shot.kill()
                    ufo_hit.destroy()
                    self.player_score += UFO_POINTS_REWARD
                
            # Check for PlayerShot - Asteroid collisions
            for s in self.player_shot_list:
                for a in arcade.check_for_collision_with_list(s, self.asteroid_list):
                    s.kill()
                    a.kill()

            # check if the player is dead
            if self.player_sprite.lives <= 0:
                self.game_state = GameState.GAME_OVER

            # check for thrust
            if self.thrust_pressed:
                self.player_sprite.thrust()

            # Update player sprite
            self.player_sprite.update()

            # Update the player shots
            self.player_shot_list.update()

            # Update Asteroids
            self.asteroid_list.update()

            # update UFOs
            self.ufo_list.update()

            # update UFO shot_lists
            self.ufo_shot_list.update()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """
        called whenever the mouse is clicked on the screen
        """

        if self.game_state == GameState.INTRO:

            if arcade.get_distance(x, y, PLAY_BUTTON_X, PLAY_BUTTON_Y) < self.play_button.width // 4:
                self.game_state = GameState.IN_GAME

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """

        # Track state of arrow keys
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.SPACE:
            self.space_pressed = True
        if key == PLAYER_THRUST_KEY:
            self.thrust_pressed = True

        if key == PLAYER_FIRE_KEY:
            new_shot = PlayerShot(
                self.player_sprite.center_x,
                self.player_sprite.center_y
            )

            self.player_shot_list.append(new_shot)

        if key == PLAYER_THRUST_KEY:
            self.player_sprite.thrust()

    def on_key_release(self, key, modifiers):
        """
        Called whenever a key is released.
        """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.SPACE:
            self.space_pressed = False
        if key == PLAYER_THRUST_KEY:
            self.thrust_pressed = False

    def on_joybutton_press(self, joystick, button_no):
        print("Button pressed:", button_no)
        # Press the fire key
        self.on_key_press(PLAYER_FIRE_KEY, [])

    def on_joybutton_release(self, joystick, button_no):
        print("Button released:", button_no)

    def on_joyaxis_motion(self, joystick, axis, value):
        print("Joystick axis {}, value {}".format(axis, value))

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        print("Joystick hat ({}, {})".format(hat_x, hat_y))


def main():
    """
    Main method
    """

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT)
    in_game_view = InGameView()
    window.show_view(in_game_view)
    arcade.run()


if __name__ == "__main__":
    main()
