#!/usr/bin/env python

"""
Simple program to show moving a sprite with the keyboard.
This program uses the Arcade library found at http://arcade.academy
Artwork from https://kenney.nl/assets/space-shooter-redux
"""

import arcade
import math
import random
import tomli

# load the config file as a dict
with open('my_game.toml', 'rb') as fp:
    CONFIG = tomli.load(fp)

# has to be defined here since they use libraries
SCREEN_COLOR = arcade.color.BLACK

# The thrust effects textures and scale
PARTICLE_TEXTURES = [
    arcade.make_soft_circle_texture(25, arcade.color.YELLOW_ORANGE),
    arcade.make_soft_circle_texture(25, arcade.color.SUNGLOW),
]
UFO_EXPLOSIONS_PARTICLE_TEXTURES = [
    arcade.make_soft_circle_texture(25, arcade.color.BLUE),
    arcade.make_soft_circle_texture(25, arcade.color.GREEN),
]


def wrap(sprite: arcade.Sprite):
    """
    if sprite is off-screen move it to the other side of the screen
    """

    if sprite.right < 0:
        sprite.center_x += CONFIG['SCREEN_WIDTH']
    elif sprite.left > CONFIG['SCREEN_WIDTH']:
        sprite.center_x -= CONFIG['SCREEN_WIDTH']

    if sprite.top < 0:
        sprite.center_y += CONFIG['SCREEN_HEIGHT']
    elif sprite.bottom > CONFIG['SCREEN_HEIGHT']:
        sprite.center_y -= CONFIG['SCREEN_HEIGHT']


class Player(arcade.Sprite):
    """
    The player
    """

    def __init__(self, center_x, center_y, lives, scale):
        """
        Setup new Player object
        """

        # Graphics to use for Player
        super().__init__("images/playerShip1_red.png", flipped_horizontally=True ,flipped_diagonally=True)
        self.invincibility_timer = 0
        self.angle = 0
        self.lives = lives
        self.scale = scale
        self.center_x = center_x
        self.center_y = center_y

    def thrust(self):
        """
        increase speed in the direction pointing
        """

        self.forward(CONFIG['PLAYER_THRUST'])
        # Keep track of Player Speed
        player_speed_vector_length = math.sqrt(self.change_x ** 2 + self.change_y ** 2)

        # Calculating the value used to lower the players speed while keeping the x - y ratio
        player_x_and_y_speed_ratio = CONFIG['PLAYER_SPEED_LIMIT'] / player_speed_vector_length

        # If player is too fast slow it down
        if player_speed_vector_length > CONFIG['PLAYER_SPEED_LIMIT']:
            self.change_x *= player_x_and_y_speed_ratio
            self.change_y *= player_x_and_y_speed_ratio

    def reset(self):
        """
        The code works as when you get hit by the asteroid you will disappear for 2 seconds.
        After that you are invincible for 3 seconds, and you can get hit again.
        """
        self.invincibility_timer = CONFIG['PLAYER_INVINCIBILITY_SECONDS']
        # The Player is Invisible
        self.alpha = 0

    @property
    def is_invincible(self):
        return self.invincibility_timer > 0

    def on_update(self, delta_time):
        """
        Move the sprite and wrap
        """

        self.center_x += self.change_x
        self.center_y += self.change_y

        # Time when you can't get hit by an asteroid
        if self.is_invincible:
            self.invincibility_timer -= delta_time
            # Time when you are not visible
            if self.invincibility_timer < 3:
                # Visible
                if self.alpha == 0:
                    self.alpha = 155
                    self.center_x = CONFIG['PLAYER_START_X']
                    self.center_y = CONFIG['PLAYER_START_Y']
                    self.change_y = 0
                    self.change_x = 0
        else:
            self.alpha = 255

        # wrap
        wrap(self)


class Asteroid(arcade.Sprite):

    def __init__(self, size=3, level=1, spawn_pos=None, angle=None):
        # Initialize the asteroid

        # Graphics
        super().__init__(
            filename='images/Meteors/meteorGrey_med1.png',
            scale=size * CONFIG['SPRITE_SCALING']
        )

        self.size = size
        self.level = level

        if angle == None:
            self.angle = random.randrange(0, 360)
        else:
            self.angle = angle

        # Spawning Astroids until the distance to the player is longer than ASTEROIDS_MINIMUM_SPAWN_DISTANCE_FROM_PLAYER
        if not spawn_pos is None:
            self.position = spawn_pos
        else:
            while True:
                self.center_x = random.randint(0, CONFIG['SCREEN_WIDTH'])
                self.center_y = random.randint(0, CONFIG['SCREEN_HEIGHT'])

                if arcade.get_distance(
                        self.center_x,
                        self.center_y,
                        CONFIG['PLAYER_START_X'],
                        CONFIG['PLAYER_START_Y']
                ) > CONFIG['ASTEROIDS_MINIMUM_SPAWN_DISTANCE_FROM_PLAYER']:
                    break
        self.angle += random.randint(-CONFIG['ASTEROIDS_SPREAD'], CONFIG['ASTEROIDS_SPREAD'])
        self.forward(CONFIG['ASTEROIDS_SPEED'])

        self.angle += random.randint(-CONFIG['ASTEROIDS_SPREAD'], CONFIG['ASTEROIDS_SPREAD'])
        self.forward(CONFIG['ASTEROIDS_SPEED'])
        self.level = level

        self.rotation_speed = random.randrange(0, 5)

        self.direction = self.angle  # placeholder for initial angle - angle changes during the game
        self.value = CONFIG['ASTEROID_SCORE_VALUES'][self.size - 1]

    def update(self):
        # Update position
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Rotate Asteroid
        self.angle += self.rotation_speed

        # wrap
        wrap(self)


class PlayerShot(arcade.Sprite):
    """
    A shot fired by the Player
    """

    sound_fire = arcade.load_sound("sounds/laserRetro_001.ogg")

    def __init__(self, center_x=0, center_y=0, angle=0):
        """
        Setup new PlayerShot object
        """

        # Set the graphics to use for the sprite
        super().__init__("images/Lasers/laserBlue01.png",
                         CONFIG['SPRITE_SCALING'],
                         flipped_horizontally=True ,
                         flipped_diagonally=True)

        self.center_x = center_x
        self.center_y = center_y
        self.angle = angle
        self.forward(CONFIG['PLAYER_SHOT_SPEED'])
        self.distance_traveled = 0
        self.speed = CONFIG['PLAYER_SHOT_SPEED']

        PlayerShot.sound_fire.play()

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
        if self.distance_traveled > CONFIG['PLAYER_SHOT_RANGE']:
            self.kill()


class UFOShot(arcade.Sprite):
    """shot fired by the ufo"""

    def __int__(self, **kwargs):
        super().__init__(**kwargs)

    def update(self):
        """update position/kill if out of bounds"""

        self.center_x += self.change_x
        self.center_y += self.change_y

        self.distance_traveled += CONFIG['UFO_SHOT_SPEED']

        self.angle = ((self.change_x / self.change_y) * -90)  # set ange based on our direction

        # kill when traveled far enough
        if self.distance_traveled > CONFIG['UFO_SHOT_RANGE']:
            self.kill()

        # wrap
        wrap(self)


class BonusUFO(arcade.Sprite):
    """occasionally moves across the screen. Grants the player points if shot"""

    sound_fire = arcade.load_sound("sounds/laserRetro_001.ogg")
    sound_explosion = arcade.load_sound("sounds/explosionCrunch_000.ogg")

    def __int__(self, shot_list, level=1, **kwargs):

        kwargs['filename'] = "images/ufoBlue.png"

        # UFOs are big or small
        kwargs['scale'] = CONFIG['SPRITE_SCALING'] * random.choice([CONFIG['UFO_SIZE_SMALL'], CONFIG['UFO_SIZE_BIG']])

        # set random position off-screen
        kwargs['center_x'] = random.choice([0, CONFIG['SCREEN_WIDTH']])
        kwargs['center_y'] = random.choice([0, CONFIG['SCREEN_HEIGHT']])

        # send arguments upstairs
        super().__init__(**kwargs)

        self.level = level
        self.shot_list = shot_list

        # set random direction. always point towards center, with noise
        self.change_x = random.randrange(1, CONFIG['UFO_SPEED']) + (self.level - 1) * CONFIG['UFO_SPEED_MOD_PR_LEVEL']
        if self.center_x > CONFIG['SCREEN_WIDTH'] / 2:
            self.change_x *= -1

        self.change_y = CONFIG['UFO_SPEED'] - self.change_x + (self.level - 1) * CONFIG['UFO_SPEED_MOD_PR_LEVEL']
        if self.center_y > CONFIG['SCREEN_HEIGHT'] / 2:
            self.change_y *= -1

        # setup direction changing
        arcade.schedule(self.change_dir, CONFIG['UFO_DIR_CHANGE_RATE'])

        # setup shooting
        arcade.schedule(self.shoot, CONFIG['UFO_FIRE_RATE'] + (self.level - 1) * CONFIG['UFO_FIRE_RATE_MOD_PR_LEVEL'])

    def change_dir(self, delta_time):
        """
        set a new direction
        """

        r = random.randrange(-CONFIG['UFO_SPEED'], CONFIG['UFO_SPEED'])
        self.change_x -= r
        self.change_y += r

    def shoot(self, delta_time):
        """
        fire a new shot
        """
        BonusUFO.sound_fire.play()
        new_ufo_shot = UFOShot()  # sprites created with arcade.schedule don't __init__ it has to be manually called
        new_ufo_shot.__init__(
            filename="images/Lasers/laserGreen07.png",
            scale=CONFIG['SPRITE_SCALING'],
            center_x=self.center_x,
            center_y=self.center_y
        )

        new_ufo_shot.change_x = random.randrange(-CONFIG['UFO_SHOT_SPEED'], CONFIG['UFO_SHOT_SPEED'])
        new_ufo_shot.change_y = new_ufo_shot.change_x - CONFIG['UFO_SHOT_SPEED']
        new_ufo_shot.distance_traveled = 0
        self.shot_list.append(new_ufo_shot)

    def update(self):
        """update position, and kill if out of bounds"""

        # keep spinning. just for graphics purposes
        self.angle += self.change_x + self.change_y  # the faster it moves, the faster it spins.

        self.center_x += self.change_x
        self.center_y += self.change_y

        # kill if out of bounds
        if self.center_x > CONFIG['SCREEN_WIDTH'] or self.center_x < 0 or self.center_y > CONFIG[
            'SCREEN_HEIGHT'] or self.center_y < 0:
            self.destroy()

    def destroy(self):
        """
        kill the sprite and unschedule all functions
        """
        arcade.unschedule(self.shoot)
        arcade.unschedule(self.change_dir)
        self.kill()


class IntroView(arcade.View):
    """
    View for the intro screen.
    """

    def __init__(self):
        super().__init__()

        self.title_graphics = arcade.load_texture("images/UI/asteroidsTitle.png")
        self.play_button = arcade.load_texture("images/UI/asteroidsStartButton.png")

        arcade.set_background_color(SCREEN_COLOR)

    def on_draw(self):
        """
        draw everything on the screen
        """

        arcade.start_render()

        self.title_graphics.draw_scaled(
            center_x=CONFIG['TITLE_X'],
            center_y=CONFIG['TITLE_Y']
        )

        self.play_button.draw_scaled(
            center_x=CONFIG['BUTTON_X'],
            center_y=CONFIG['BUTTON_Y'],
        )

    def on_key_press(self, symbol: int, modifiers: int):
        self.start_game()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """
        called whenever the mouse is clicked on the screen
        """
        if arcade.get_distance(x, y, CONFIG['BUTTON_X'], CONFIG['BUTTON_Y']) < self.play_button.width // 2:
            self.start_game()

    def start_game(self):
        in_game_view = InGameView()
        self.window.show_view(in_game_view)


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

        # loading sounds

        self.sound_explosion = arcade.load_sound("sounds/explosionCrunch_000.ogg")
        self.sound_thrust = arcade.load_sound("sounds/spaceEngine_003.ogg")
        self.sound_thrust_player = None

        # Variable that will hold a list of shots fired by the player
        self.player_shot_list = None
        self.player_shot_fire_rate_timer = 0

        # Asteroid SpriteList
        self.asteroid_list = None

        # The current level
        self.level = 1

        # Set up the player info
        self.player_sprite: Player = None
        self.player_score = None
        self.player_lives = None
        self.player_speed = 0
        self.opposite_angle = 0
        self.thrust_emitter = None
        self.explosion_emitter = None

        # set up ufo info
        self.ufo_list = None
        self.ufo_shot_list = None

        # Track the current state of what key is pressed
        self.space_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.thrust_pressed = False
        self.turn_right_pressed = False
        self.turn_left_pressed = False

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
        arcade.set_background_color(SCREEN_COLOR)

    def next_level(self, level=None):
        """
        Advance the game to the next level
        or start a specific level
        """

        # if no specific level was requested, advance to the next level
        if level is None:
            self.level += 1
        else:
            self.level = level

        # FIXME: Player needs to know that level was cleared

        # Spawn Asteroids
        for r in range(CONFIG['ASTEROIDS_PR_LEVEL'] + (self.level - 1) * CONFIG['ASTEROID_NUM_MOD_PR_LEVEL']):
            self.asteroid_list.append(Asteroid(level=self.level))

    def spawn_ufo(self, delta_time):
        """
        spawns an ufo object into self.ufo_list.
        has to take delta_time because it needs to be called by arcade.schedule
        """

        new_ufo_obj = BonusUFO()
        new_ufo_obj.__int__(self.ufo_shot_list, self.level)  # it needs the list so it can send shots to MyGame
        self.ufo_list.append(new_ufo_obj)

    def get_explosion(self, position, textures=None):
        """
        Makes an explosion effect
        """
        if textures is None:
            textures = PARTICLE_TEXTURES

        self.explosion_emitter = arcade.make_burst_emitter(
            center_xy=position,
            filenames_and_textures=textures,
            particle_count=CONFIG['EXPLOSION_PARTICLE_AMOUNT'],
            particle_speed=CONFIG['EXPLOSION_PARTICLE_SPEED'],
            particle_lifetime_min=CONFIG['EXPLOSION_PARTICLE_LIFETIME_MIN'],
            particle_lifetime_max=CONFIG['EXPLOSION_PARTICLE_LIFETIME_MAX'],
            particle_scale=CONFIG['EXPLOSION_PARTICLE_SIZE'])

    def on_show_view(self):
        """ Set up the game and initialize the variables. """

        self.sound_thrust_player = None

        # No points when the game starts
        self.player_score = 0

        # Sprite lists
        self.player_shot_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()

        self.ufo_list = arcade.SpriteList()
        self.ufo_shot_list = arcade.SpriteList()

        # Create a Player object
        self.player_sprite = Player(
            center_x=CONFIG['PLAYER_START_X'],
            center_y=CONFIG['PLAYER_START_Y'],
            lives=CONFIG['PLAYER_START_LIVES'],
            scale=CONFIG['SPRITE_SCALING']
        )

        # setup spawn_ufo to run regularly
        arcade.schedule(self.spawn_ufo, CONFIG['UFO_SPAWN_RATE'] + (self.level - 1) * CONFIG['UFO_SPAWN_RATE_MOD_PR_LEVEL'])

        # Add an emitter that makes the thrusting particles
        self.thrust_emitter = arcade.Emitter(
            center_xy=(self.player_sprite.center_x, self.player_sprite.center_y),
            emit_controller=arcade.EmitterIntervalWithTime(0, 0),  # setting a blank controller when not thrusting.
            particle_factory=lambda emitter: arcade.FadeParticle(
                filename_or_texture=random.choice(PARTICLE_TEXTURES),
                change_xy=(0, 12.0),
                lifetime=0.2,
            )
        )
        self.thrust_emitter.angle = self.player_sprite.angle

        # Start level 1
        self.next_level(1)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # draw particle emitter
        self.thrust_emitter.draw()

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

        # and their shots
        self.ufo_shot_list.draw()

        # draw explosion
        if self.explosion_emitter is not None:
            self.explosion_emitter.draw()

        # Draw players score on screen
        arcade.draw_text(
            "SCORE: {}".format(self.player_score),  # Text to show
            10,  # X position
            CONFIG['SCREEN_HEIGHT'] - 20,  # Y_position
            arcade.color.WHITE  # Color of text
        )
        arcade.draw_text(
            "LIVES: {}".format(self.player_sprite.lives),  # Text to show
            10,  # X position
            CONFIG['SCREEN_HEIGHT'] - 45,  # Y positon
            arcade.color.WHITE  # Color of text
        )
        arcade.draw_text(
            "LEVEL: {}".format(self.level),
            10,
            CONFIG['SCREEN_HEIGHT'] - 70,
            arcade.color.WHITE
        )

    def on_update(self, delta_time):
        """
        Movement and game logic
        """

        # Calculate player speed based on the keys pressed
        # Move player with keyboard
        if self.turn_left_pressed and not self.turn_right_pressed:
            self.player_sprite.angle += CONFIG['PLAYER_ROTATE_SPEED']
        elif self.turn_right_pressed and not self.turn_left_pressed:
            self.player_sprite.angle += -CONFIG['PLAYER_ROTATE_SPEED']

        # rotate player with joystick if present
        if self.joystick:
            self.player_sprite.angle += round(self.joystick.x) * -CONFIG['PLAYER_ROTATE_SPEED']

        # checks if ufo shot collides with player
        for ufo_shot_hit in self.player_sprite.collides_with_list(self.ufo_shot_list):
            self.player_sprite.lives -= 1
            self.player_sprite.reset()
            self.get_explosion(self.player_sprite.position)
            ufo_shot_hit.kill()

        # Check if collision with Asteroids and dies and kills the Asteroid
        for a in self.player_sprite.collides_with_list(self.asteroid_list):
            if not self.player_sprite.is_invincible:
                # In the future, the Player will explode instead of disappearing.
                self.player_sprite.lives -= 1
                self.player_sprite.reset()
                self.get_explosion(self.player_sprite.position)
                a.kill()

        # check for collision with bonus_ufo
        for ufo in self.player_sprite.collides_with_list(self.ufo_list):
            if not self.player_sprite.is_invincible:
                # In the future, the Player will explode instead of disappearing.
                self.player_sprite.lives -= 1
                self.player_sprite.reset()
                self.get_explosion(self.player_sprite.position)
                ufo.destroy()

        # Player shot
        for shot in self.player_shot_list:

            for ufo_hit in arcade.check_for_collision_with_list(shot, self.ufo_list):
                shot.kill()
                self.sound_explosion.play()
                ufo_hit.destroy()
                self.player_score += CONFIG['UFO_POINTS_REWARD']
                self.get_explosion(
                    ufo_hit.position,
                    textures=UFO_EXPLOSIONS_PARTICLE_TEXTURES
                )

        if self.sound_thrust_player is not None and self.thrust_pressed is False and self.sound_thrust.is_playing(
                self.sound_thrust_player):
            v = self.sound_thrust.get_volume(self.sound_thrust_player) * 0.95
            self.sound_thrust.set_volume(v, self.sound_thrust_player)
            if v == 0:
                self.sound_thrust.stop(self.sound_thrust_player)

        # Check for PlayerShot - Asteroid collisions
        for s in self.player_shot_list:

            for a in arcade.check_for_collision_with_list(s, self.asteroid_list):
                for n in range(CONFIG['ASTEROIDS_PR_SPLIT']):
                    if a.size > 1:
                        a_angle = random.randrange(s.angle - CONFIG["ASTEROIDS_SPREAD"], s.angle + CONFIG["ASTEROIDS_SPREAD"])
                        new_a = Asteroid(a.size-1, self.level, a.position, a_angle)
                        self.asteroid_list.append(new_a)

                    else:
                        pass
                s.kill()
                a.kill()
                self.sound_explosion.play()
                self.player_score += a.value

        # check for thrust
        if self.thrust_pressed:
            self.player_sprite.thrust()

        if self.player_shot_fire_rate_timer < CONFIG['PLAYER_FIRE_RATE']:
            self.player_shot_fire_rate_timer += delta_time

        # Update player sprite
        self.player_sprite.on_update(delta_time)

        # Update the player shots
        self.player_shot_list.update()

        # Update Asteroids
        self.asteroid_list.update()

        # update UFOs
        self.ufo_list.update()

        # update UFO shot_lists
        self.ufo_shot_list.update()

        # check if the player is dead
        if self.player_sprite.lives <= 0:
            arcade.stop_sound(self.sound_thrust_player)
            arcade.unschedule(self.spawn_ufo)
            game_over_view = GameOverView(player_score=self.player_score, level=self.level)
            self.window.show_view(game_over_view)

        # create a new emit-controller for the thruster if thrusting.
        if self.thrust_pressed and self.thrust_emitter.rate_factory.is_complete():
            self.thrust_emitter.rate_factory = arcade.EmitterIntervalWithTime(CONFIG['THRUSTER_EMIT_RATE'], CONFIG['THRUSTER_EMIT_TIME'])

        self.thrust_emitter.update()
        self.thrust_emitter.angle = self.player_sprite.angle - 270 + random.randint(
            -CONFIG['PLAYER_ENGINE_SHAKE'],
            CONFIG['PLAYER_ENGINE_SHAKE']
        )
        self.thrust_emitter.center_x = self.player_sprite.center_x
        self.thrust_emitter.center_y = self.player_sprite.center_y

        if len(self.asteroid_list) == 0:
            self.next_level()

        if self.explosion_emitter is not None:
            self.explosion_emitter.update()

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """

        # Track state of arrow keys
        if key == CONFIG["PLAYER_TURN_RIGHT_KEY"]:
            self.turn_right_pressed = True
        elif key == CONFIG["PLAYER_TURN_LEFT_KEY"]:
            self.turn_left_pressed = True
        elif key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.SPACE:
            self.space_pressed = True

        if key == CONFIG["PLAYER_THRUST_KEY"]:
            # if thrust just got pressed start sound loop
            if self.thrust_pressed is False:
                if self.sound_thrust_player is not None:
                    self.sound_thrust.stop(self.sound_thrust_player)
                self.sound_thrust_player = self.sound_thrust.play(loop=True)
            self.thrust_pressed = True

        if key == CONFIG["PLAYER_FIRE_KEY"]:
            if not self.player_sprite.is_invincible:
                if self.player_shot_fire_rate_timer >= CONFIG['PLAYER_FIRE_RATE']:
                    new_shot = PlayerShot(
                        self.player_sprite.center_x,
                        self.player_sprite.center_y,
                        self.player_sprite.angle
                    )

                    self.player_shot_list.append(new_shot)
                    self.player_shot_fire_rate_timer = 0

        if key == CONFIG['RESTART_BUTTON']:
            new_game = InGameView()
            self.window.show_view(new_game)

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
        if key == CONFIG["PLAYER_THRUST_KEY"]:
            self.thrust_pressed = False
        elif key == CONFIG["PLAYER_TURN_RIGHT_KEY"]:
            self.turn_right_pressed = False
        elif key == CONFIG["PLAYER_TURN_LEFT_KEY"]:
            self.turn_left_pressed = False

    def on_joybutton_press(self, joystick, button_no):
        print("Button pressed:", button_no)
        # Press the fire key
        self.on_key_press(CONFIG["PLAYER_FIRE_KEY"], [])

    def on_joybutton_release(self, joystick, button_no):
        print("Button released:", button_no)

    def on_joyaxis_motion(self, joystick, axis, value):
        print("Joystick axis {}, value {}".format(axis, value))

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        print("Joystick hat ({}, {})".format(hat_x, hat_y))


class GameOverView(arcade.View):
    """
    the game over screen
    """

    def __init__(self, player_score, level):
        super().__init__()

        self.game_over_sign = arcade.load_texture("images/UI/asteroidsGameOverSign.png")
        self.restart_button = arcade.load_texture("images/UI/asteroidsRestartButton.png")

        self.player_score = player_score
        self.level = level

        # set background color
        arcade.set_background_color(SCREEN_COLOR)

    def on_draw(self):
        """
        draw the screen
        """

        arcade.start_render()

        self.game_over_sign.draw_scaled(
            center_x=CONFIG['TITLE_X'],
            center_y=CONFIG['TITLE_Y']
        )

        self.restart_button.draw_scaled(
            center_x=CONFIG['BUTTON_X'],
            center_y=CONFIG['BUTTON_Y']
        )

        arcade.draw_text(
            f"SCORE: {self.player_score}    LEVEL: {self.level}",
            CONFIG['SCREEN_WIDTH'] * 0.4,
            CONFIG['SCREEN_HEIGHT'] * 0.6,
            arcade.color.WHITE
        )

    def on_key_press(self, symbol: int, modifiers: int):
        self.new_game()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """
        called whenever the mouse is clicked on the screen.
        """

        if arcade.get_distance(x, y, CONFIG['BUTTON_X'], CONFIG['BUTTON_Y']) < self.restart_button.height // 2:
            self.new_game()

    def new_game(self):
        in_game_view = InGameView()
        self.window.show_view(in_game_view)


def main():
    """
    Main method
    """

    window = arcade.Window(CONFIG['SCREEN_WIDTH'], CONFIG['SCREEN_HEIGHT'])
    intro_view = IntroView()
    window.show_view(intro_view)
    arcade.run()


if __name__ == "__main__":
    main()
