"""
Simple program to show moving a sprite with the keyboard.

This program uses the Arcade library found at http://arcade.academy

Artwork from https://kenney.nl/assets/space-shooter-redux

"""
import time

import arcade
import math
import random

SPRITE_SCALING = 0.5

# Set the size of the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Variables controlling the player

PLAYER_START_LIVES = 3
PLAYER_ROTATE_SPEED = 5
PLAYER_SPEED_X = 5
PLAYER_START_X = SCREEN_WIDTH / 2
PLAYER_START_Y = SCREEN_HEIGHT / 2
PLAYER_SPEED = 3
PLAYER_SHOT_SPEED = 4
PLAYER_THRUST = 0.5
PLAYER_SHOT_RANGE = SCREEN_WIDTH // 2
INVINCIBILITY_SECONDS = 5

FIRE_KEY = arcade.key.SPACE

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

    def __init__(self, center_x, center_y, scale, lives, is_imortal):
        """
        Setup new Player object
        """
        # Graphics to use for Player
        super().__init__("images/playerShip1_red.png")

        self.speed = 1
        self.angle = 0
        self.lives = lives
        self.scale = scale
        self.change_x = self.speed * math.cos(self.angle)
        self.change_y = self.speed * math.cos(self.angle)
        self.center_x = center_x
        self.center_y = center_y
        self.is_imortal = is_imortal
        self.die_cooldown = 30
        self.alpha = 255
        self.respawning = False

    def reset(self):
        """
        What happens to the player when it loses a life.
        """
        # It 100% transparent
        self.respawning = True
        self.alpha = 0
        self.die_cooldown = 90

    def update(self):
        """
        Move the sprite and wrap
        """
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.respawning:
            self.die_cooldown -= 1
            if self.die_cooldown < 1:
                self.center_x = PLAYER_START_X
                self.center_y = PLAYER_START_Y
                # 100% visible again
                self.alpha = 255
                self.respawning = False
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


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__(width, height)

        # Variable that will hold a list of shots fired by the player
        self.player_shot_list = None

        # Asteroid SpriteList
        self.asteroid_list = None

        # Set up the player info
        self.player_sprite = None
        self.player_score = None
        self.player_lives_lose = 0
        self.player_speed = 0
        self.opposite_angle = 0
        self.max_speed = PLAYER_SPEED
        self.reset_cooldown = 5.0

        # set up ufo info
        self.ufo_list = None
        self.ufo_shot_list = None

        # Track the current state of what key is pressed
        self.space_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

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

    def setup(self):
        """ Set up the game and initialize the variables. """

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
            scale=SPRITE_SCALING,
            lives=PLAYER_START_LIVES,
            is_imortal=INVINCIBILITY_SECONDS
        )

        # Spawn Asteroids
        for r in range(ASTEROIDS_PR_LEVEL):
            self.asteroid_list.append(Asteroid())

        # setup spawn_ufo to run regularly
        arcade.schedule(self.spawn_ufo, UFO_SPAWN_RATE)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw asteroids
        self.asteroid_list.draw()

        # Draw the player shot
        self.player_shot_list.draw()

        # Draw the player sprite
        self.player_sprite.draw()

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
            SCREEN_HEIGHT - 45,  # Y positon
            arcade.color.WHITE  # Color of text
        )

    def on_update(self, delta_time):
        """
        Movement and game logic
        """

        # Calculate player speed based on the keys pressed
        self.player_sprite.change_x = 0

        # Move player with keyboard
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.angle += PLAYER_ROTATE_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.angle += -PLAYER_ROTATE_SPEED

        if self.player_sprite.is_imortal > 0:
            self.player_sprite.is_imortal -= delta_time

        # rotate player with joystick if present
        if self.joystick:
            self.player_sprite.angle += round(self.joystick.x) * -PLAYER_ROTATE_SPEED

        # check for collisions
        # player shot
        for shot in self.player_shot_list:

            for ufo_hit in arcade.check_for_collision_with_list(shot, self.ufo_list):
                shot.kill()
                ufo_hit.destroy()
                self.player_score += UFO_POINTS_REWARD

        # Checks if the Player touching any astroid
        if any(self.player_sprite.collides_with_list(self.asteroid_list)):
            if self.player_sprite.is_imortal > 1:
                pass
            else:
                if not self.player_sprite.lives == 0:
                    self.player_lives_lose = 1
                    self.player_sprite.lives -= self.player_lives_lose
                    self.player_sprite.is_imortal = 5
                else:
                    # GameOver
                    print("Game Over")
                    arcade.close_window()
                Player.reset(self.player_sprite)

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

        if self.up_pressed:
            if not self.player_sprite.speed > self.max_speed:
                self.player_sprite.speed += PLAYER_THRUST

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

        if key == FIRE_KEY:
            new_shot = PlayerShot(
                self.player_sprite.center_x,
                self.player_sprite.center_y
            )

            self.player_shot_list.append(new_shot)

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

    def on_joybutton_press(self, joystick, button_no):
        print("Button pressed:", button_no)
        # Press the fire key
        self.on_key_press(FIRE_KEY, [])

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

    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
