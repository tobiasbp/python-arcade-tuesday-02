#!/usr/bin/env python

"""
Simple program to show moving a sprite with the keyboard.
This program uses the Arcade library found at http://arcade.academy
Artwork from https://kenney.nl/assets/space-shooter-redux
"""

import arcade
import arcade.gui
import math
import random
import tomli_w
import pathlib
import arcade.gui
from pyglet.math import Vec2


from game_sprites import Star, Shot, Asteroid, Player, BonusUFO, PowerUp
from tools import get_joystick, wrap, load_toml, get_stars, StoppableEmitter

# load the config file as a dict
CONFIG = load_toml('my_game.toml')

# Load the user settings file, which is superior to the original config file, into the CONFIG dict
user_settings = load_toml("user_settings.toml")
for k in user_settings.keys():
    CONFIG[k] = user_settings[k]

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


class IntroView(arcade.View):
    """
    View for the intro screen.
    """

    def __init__(self):
        super().__init__()

        self.title_graphics = arcade.load_texture("images/UI/asteroidsTitle.png")
        self.basic_button = arcade.load_texture("images/UI/basicButtonSmall.png")
        self.basic_button_hover = arcade.load_texture("images/UI/basicButtonSmallHover.png")

        # Makes the manager that contains the GUI button and enables it to the game.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Make the restart button.
        self.gui_play_button = arcade.gui.UITextureButton(
            x=CONFIG['BUTTON_X'],
            y=CONFIG['BUTTON_Y'],
            width=100,
            height=100,
            texture=self.basic_button,
            texture_hovered=self.basic_button_hover,
            scale=CONFIG['BUTTON_SCALE'],
            style=None,
            text="Play"
        )

        # Make the settings button
        self.gui_settings_button = arcade.gui.UITextureButton(
            x=CONFIG['SETTINGS_BUTTON_X'],
            y=CONFIG['SETTINGS_BUTTON_Y'],
            width=100,
            height=100,
            texture=self.basic_button,
            texture_hovered=self.basic_button_hover,
            scale=CONFIG['BUTTON_SCALE'],
            style=None,
            text="Settings"
        )

        # Now when the GUI buttons are clicked they run the functions we assign to them
        self.gui_play_button.on_click = self.start_game
        self.gui_settings_button.on_click = self.enter_settings
        # Adds the button to the manager so the manager can draw it.
        self.manager.add(self.gui_play_button)
        self.manager.add(self.gui_settings_button)

        arcade.set_background_color(SCREEN_COLOR)

        self.joystick = get_joystick(
            self.on_joybutton_pressed,
            self.on_joybutton_released,
            print,
            print
        )
        self.stars_list = get_stars(no_of_stars=CONFIG['STARS_ON_SCREEN_INTRO'],
                                    max_x=CONFIG['SCREEN_WIDTH'],
                                    max_y=CONFIG['SCREEN_HEIGHT'],
                                    base_size=CONFIG['STARS_BASE_SIZE'],
                                    scale=CONFIG['STARS_SCALE'],
                                    fadespeed=CONFIG['STARS_FADE_SPEED']
                                    )

        stars_angle = random.uniform(0, 360)

        for s in self.stars_list:
            s.change_x = math.sin(stars_angle)
            s.change_y = math.cos(stars_angle)

    def on_draw(self):
        """
        draw everything on the screen
        """

        arcade.start_render()
        # DRAWS STARS
        self.stars_list.draw()

        self.title_graphics.draw_scaled(
            center_x=CONFIG['TITLE_X'],
            center_y=CONFIG['TITLE_Y']
        )

        # Draws the manager that contains the button.
        self.manager.draw()

    def on_update(self, delta_time):

        # stars
        for s in self.stars_list:
            # Wrap star if off screen
            wrap(s, CONFIG['SCREEN_WIDTH'], CONFIG['SCREEN_HEIGHT'])
        # Move all stars
        self.stars_list.on_update(delta_time)


    def on_key_press(self, symbol: int, modifiers: int):
        # You can start the game and the settings with the keyboard
        if symbol == CONFIG["UI_PLAY_KEY"]:
            self.gui_play_button.hovered = True
        elif symbol == CONFIG["UI_SETTINGS_KEY"]:
            self.gui_settings_button.hovered = True

    def on_key_release(self, _symbol: int, _modifiers: int):
        if _symbol == CONFIG["UI_PLAY_KEY"]:
            self.start_game()
        elif _symbol == CONFIG["UI_SETTINGS_KEY"]:
            self.enter_settings()

    def on_joybutton_pressed(self, joystick, button_no):
        self.gui_play_button.hovered = True

    def on_joybutton_released(self, joystick, button_no):
        self.start_game()

    def start_game(self, event=None):

        in_game_view = InGameView()

        # Stop using  this joystick
        if self.joystick is not None:
            self.joystick.close()

        self.window.show_view(in_game_view)

    def enter_settings(self, event=None):
        settings_view = SettingsView()
        self.window.show_view(settings_view)


class SettingsView(arcade.View):
    """
    Veiw for the Settings Screen
    """

    def __init__(self):
        super().__init__()

        # Making dicts that will help us translate the keys (str) and key IDs (int) from the arcade.key module
        keys = dir(arcade.key)
        self.key_to_id = {}
        self.id_to_key = {}
        non_keys = 0
        for a in keys:
            if a[0] == "_":
                non_keys += 1
        for n in range(non_keys):
            keys.pop(-1)
        for k in keys:
            # Remove the MOTION keys because they are just duplicates of the arrow keys
            if k not in ("MOTION_LEFT", "MOTION_RIGHT", "MOTION_UP", "MOTION_DOWN"):
                self.key_to_id.update({k: eval("arcade.key." + k)})
        for k in self.key_to_id:
            self.id_to_key.update({self.key_to_id[k]: k})

        # Load button textures
        self.basic_button = arcade.load_texture("images/UI/basicButtonBig.png")
        self.basic_button_hover = arcade.load_texture("images/UI/basicButtonBigHover.png")

        self.name_of_key_to_change = None
        self.changed_settings = {}
        # Settings guides that appears under the buttons
        self.settings_guide_select = arcade.gui.UITextArea(
            text="Select setting you wish to change",
            width=215,
            font_size=10
        )
        self.settings_guide_exit = arcade.gui.UITextArea(
            text="Press " + self.id_to_key[CONFIG["EXIT_SETTINGS_KEY"]] + " to return to main screen",
            width=255,
            font_size=10
        )
        self.settings_guide_key_already_in_use = arcade.gui.UITextArea(
            text="",
            width=320,
            font_size=10
        )
        # Settings guide that appears on the buttons when they are clicked
        self.settings_guide_press_key = "Press the key you wish to use"

        # Initialize UI Manager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create layout for UI widets
        self.v_box = arcade.gui.UIBoxLayout()


        # Initialize the widgets
        self.reset_settings_button = arcade.gui.UITextureButton(
            texture=self.basic_button,
            texture_hovered=self.basic_button_hover,
            scale=CONFIG["BUTTON_SCALE"],
            style=None,
            text="Reset Settings"

        )
        self.v_box.add(self.reset_settings_button.with_space_around(bottom=20))

        self.change_player_thrust_key_button = arcade.gui.UITextureButton(
            texture=self.basic_button,
            texture_hovered=self.basic_button_hover,
            scale=CONFIG["BUTTON_SCALE"],
            style=None,
            text="Change Thrust Key: " + self.id_to_key[CONFIG["PLAYER_THRUST_KEY"]]
        )
        self.v_box.add(self.change_player_thrust_key_button.with_space_around(bottom=20))

        self.change_player_fire_key_button = arcade.gui.UITextureButton(
            texture=self.basic_button,
            texture_hovered=self.basic_button_hover,
            scale=CONFIG["BUTTON_SCALE"],
            style=None,
            text="Change Fire Key: " + self.id_to_key[CONFIG["PLAYER_FIRE_KEY"]]
        )
        self.v_box.add(self.change_player_fire_key_button.with_space_around(bottom=20))

        self.change_player_turn_left_key_button = arcade.gui.UITextureButton(
            texture=self.basic_button,
            texture_hovered=self.basic_button_hover,
            scale=CONFIG["BUTTON_SCALE"],
            style=None,
            text="Change Turn Left Key: " + self.id_to_key[CONFIG["PLAYER_TURN_LEFT_KEY"]]
        )
        self.v_box.add(self.change_player_turn_left_key_button.with_space_around(bottom=20))

        self.change_player_turn_right_key_button = arcade.gui.UITextureButton(
            texture=self.basic_button,
            texture_hovered=self.basic_button_hover,
            scale=CONFIG["BUTTON_SCALE"],
            style=None,
            text="Change Turn Right Key: " + self.id_to_key[CONFIG["PLAYER_TURN_RIGHT_KEY"]]
        )
        self.v_box.add(self.change_player_turn_right_key_button.with_space_around(bottom=20))

        self.v_box.add(self.settings_guide_select.with_space_around(bottom=20))
        self.v_box.add(self.settings_guide_exit.with_space_around(bottom=20))
        self.v_box.add(self.settings_guide_key_already_in_use.with_space_around(bottom=20))

        # Assign click functions to buttons
        self.reset_settings_button.on_click = self.on_click_reset
        self.change_player_thrust_key_button.on_click = self.on_click_change_keybind
        self.change_player_fire_key_button.on_click = self.on_click_change_keybind
        self.change_player_turn_left_key_button.on_click = self.on_click_change_keybind
        self.change_player_turn_right_key_button.on_click = self.on_click_change_keybind

        # Background Color
        arcade.set_background_color(SCREEN_COLOR)

        # Add layout to UI Manager
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

        # This dict is used in the function below
        self.button_to_key_name = {self.change_player_thrust_key_button: "PLAYER_THRUST_KEY",
            self.change_player_fire_key_button: "PLAYER_FIRE_KEY",
            self.change_player_turn_left_key_button: "PLAYER_TURN_LEFT_KEY",
            self.change_player_turn_right_key_button: "PLAYER_TURN_RIGHT_KEY"
        }

    def on_click_change_keybind(self, event):
        self.name_of_key_to_change = self.button_to_key_name[event.source]
        # The source of the UIEvent is the button that was clicked
        event.source.text = self.settings_guide_press_key
        self.settings_guide_select.text = ""

    def on_click_reset(self, event):
        # Reset CONFIG dict and log user settings file if it exists
        global CONFIG
        user_config_file = pathlib.Path("user_settings.toml")
        if user_config_file.is_file():
            times_reset = 0
            while True:
                new_user_config_file = pathlib.Path(
                    user_config_file.parent / user_config_file.name.replace(".toml", f"_{times_reset}.toml")
                )
                times_reset += 1
                if not new_user_config_file.is_file():
                    user_config_file.rename(new_user_config_file)
                    CONFIG = load_toml("my_game.toml")
                    print("Logged user_settings.toml")
                    break

        self.change_player_thrust_key_button.text =\
            "Change Thrust Key: " + self.id_to_key[CONFIG["PLAYER_THRUST_KEY"]]
        self.change_player_fire_key_button.text =\
            "Change Fire Key: " + self.id_to_key[CONFIG["PLAYER_FIRE_KEY"]]
        self.change_player_turn_left_key_button.text =\
            "Change Turn Left Key: " + self.id_to_key[CONFIG["PLAYER_TURN_LEFT_KEY"]]
        self.change_player_turn_right_key_button.text =\
            "Change Turn Right Key: " + self.id_to_key[CONFIG["PLAYER_TURN_RIGHT_KEY"]]

    def on_draw(self):
        arcade.start_render()
        self.manager.draw()

    def on_key_press(self, key, modifiers):

        if key == CONFIG["EXIT_SETTINGS_KEY"]:
            intro_view = IntroView()
            self.window.show_view(intro_view)
        else:
            if not self.name_of_key_to_change == None:
                if key == CONFIG["PLAYER_THRUST_KEY"] or key == CONFIG["PLAYER_FIRE_KEY"] or key == CONFIG["PLAYER_TURN_RIGHT_KEY"] or key == CONFIG["PLAYER_THRUST_KEY"]:
                    self.settings_guide_key_already_in_use.text = "This key is already in use. Please select another"
                else:
                    self.changed_settings[self.name_of_key_to_change] = key
                    CONFIG[self.name_of_key_to_change] = key
                    self.name_of_key_to_change = None
                    self.settings_guide_select.text = "Select setting you wish to change"
                    self.change_player_thrust_key_button.text = "Change Thrust Key: " + self.id_to_key[
                        CONFIG["PLAYER_THRUST_KEY"]]
                    self.change_player_fire_key_button.text = "Change Fire Key: " + self.id_to_key[
                        CONFIG["PLAYER_FIRE_KEY"]]
                    self.change_player_turn_left_key_button.text = "Change Turn Left Key: " + self.id_to_key[
                        CONFIG["PLAYER_TURN_LEFT_KEY"]]
                    self.change_player_turn_right_key_button.text = "Change Turn Right Key: " + self.id_to_key[
                        CONFIG["PLAYER_TURN_RIGHT_KEY"]]
                    with open("user_settings.toml", "wb") as f:
                        tomli_w.dump(self.changed_settings, f)
                    self.changed_settings = {}
                    self.settings_guide_key_already_in_use.text = ""

class InGameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        """
        Initializer
        """
        self.sound_thrust_player = None

        # Call the parent class initializer
        super().__init__()

        # loading sounds

        self.sound_explosion = arcade.load_sound("sounds/explosionCrunch_000.ogg")
        self.sound_thrust = arcade.load_sound("sounds/spaceEngine_003.ogg")

        self.sound_fire = arcade.load_sound("sounds/laserRetro_001.ogg")

        # Variable that will hold a list of shots fired by the player
        self.player_shot_list = None

        # Power ups SprteList
        self.power_up_list = None

        # Asteroid SpriteList
        self.asteroid_list = None

        # The current level
        self.level = 1

        # Set up the player info
        self.player_sprite: Player = None
        self.player_score = None
        self.player_speed = 0
        self.opposite_angle = 0
        self.explosion_emitter = None
        self.player_shoot_sound = None
        self.stoppable_emitter = None

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
        self.joystick = get_joystick(
            self.on_joybutton_press,
            self.on_joybutton_release,
            self.on_joyaxis_motion,
            self.on_joyhat_motion
        )

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

        # Background stars
        self.stars_list = get_stars(no_of_stars=CONFIG['STARS_ON_SCREEN_GAME'],
                                    max_x=CONFIG['SCREEN_WIDTH'],
                                    max_y=CONFIG['SCREEN_HEIGHT'],
                                    base_size=CONFIG['STARS_BASE_SIZE'],
                                    scale=CONFIG['STARS_SCALE'],
                                    fadespeed=CONFIG['STARS_FADE_SPEED']
                                    )

        # Spawn Asteroids
        for r in range(CONFIG['ASTEROIDS_PR_LEVEL'] + (self.level - 1) * CONFIG['ASTEROID_NUM_MOD_PR_LEVEL']):
            self.asteroid_list.append(
                Asteroid(scale=CONFIG['SPRITE_SCALING'],
                            screen_width=CONFIG['SCREEN_WIDTH'],
                            screen_height=CONFIG['SCREEN_HEIGHT'],
                            min_spawn_dist_from_player=CONFIG['ASTEROIDS_MINIMUM_SPAWN_DISTANCE_FROM_PLAYER'],
                            player_start_pos=(CONFIG['PLAYER_START_X'], CONFIG['PLAYER_START_Y']),
                            score_values=CONFIG['ASTEROID_SCORE_VALUES'],
                            spread=CONFIG['ASTEROIDS_SPREAD'],
                            speed=CONFIG['ASTEROIDS_SPEED'],
                            level=self.level)
            )

        # Spawn PowerUp
        pu = PowerUp(start_max_x=CONFIG["SCREEN_WIDTH"],
                     start_max_y=CONFIG["SCREEN_HEIGHT"],
                     wrap_max_x=CONFIG["SCREEN_WIDTH"],
                     wrap_max_y=CONFIG["SCREEN_HEIGHT"],
                     speed=random.uniform(CONFIG["POWERUP_MIN_SPEED"], CONFIG["POWERUP_MAX_SPEED"]))

        self.power_up_list.append(
            pu
        )

    def spawn_ufo(self, delta_time):
        """
        spawns an ufo object into self.ufo_list.
        has to take delta_time because it needs to be called by arcade.schedule
        """

        # FIXME: stop calling this function in arcade.schedule

        new_ufo_obj = BonusUFO(0, 0)  # actual values are given below
        # we have to call __init__ manually - if we don't the UFO won't __init__
        new_ufo_obj.__int__(
            scale=CONFIG['SPRITE_SCALING'],
            shot_list=self.ufo_shot_list,
            target=self.player_sprite,
            speed=CONFIG['UFO_SPEED'],
            speed_mod=CONFIG['UFO_SPEED_MOD_PR_LEVEL'] * (self.level - 1),
            dir_change_rate=CONFIG['UFO_DIR_CHANGE_RATE'],
            fire_rate=CONFIG['UFO_FIRE_RATE'],
            fire_rate_mod=CONFIG['UFO_FIRE_RATE_MOD_PR_LEVEL'] * (self.level - 1),
            shot_scale=CONFIG['SPRITE_SCALING'],
            shot_speed=CONFIG['UFO_SHOT_SPEED'],
            shot_range=CONFIG['UFO_SHOT_RANGE'],
            shot_fade_start=CONFIG['SHOT_FADE_START'],
            shot_fade_speed=CONFIG['SHOT_FADE_SPEED'],
            small_size=CONFIG['UFO_SIZE_SMALL'],
            big_size=CONFIG['UFO_SIZE_BIG'],
            screen_width=CONFIG['SCREEN_WIDTH'],
            screen_height=CONFIG['SCREEN_HEIGHT']
        )  # it needs the list so it can send shots to MyGame
        self.ufo_list.append(new_ufo_obj)

    def get_explosion(self, position, textures=None, size=CONFIG["EXPLOSION_PARTICLE_SIZE"], amount=CONFIG["EXPLOSION_PARTICLE_AMOUNT"]):
        """
        Makes an explosion effect
        """
        self.shake(CONFIG['EXPLOSION_SHAKE_AMPLITUDE'])

        if textures is None:
            textures = PARTICLE_TEXTURES

        self.explosion_emitter = arcade.make_burst_emitter(
            center_xy=position,
            filenames_and_textures=textures,
            particle_count=amount,
            particle_speed=CONFIG['EXPLOSION_PARTICLE_SPEED'],
            particle_lifetime_min=CONFIG['EXPLOSION_PARTICLE_LIFETIME_MIN'],
            particle_lifetime_max=CONFIG['EXPLOSION_PARTICLE_LIFETIME_MAX'],
            particle_scale=size)

    def shockwave(self, center: tuple[float, float], range: float, strength: float, sprites: arcade.SpriteList):
        """
        create a shockwave at the center that pushes away all given sprites
        """

        for sprite in sprites:
            dist = arcade.get_distance(sprite.center_x, sprite.center_y, center[0], center[1])

            if dist <= range:

                # point away from the center
                angle_to_center = arcade.get_angle_degrees(sprite.center_x, sprite.center_y, center[0], center[1])
                sprite.angle = sprite.angle - (sprite.angle - angle_to_center) - 180

                #FIXME: why does sprite.forward not work here?

                # the closer to the center, the faster it moves
                impact = abs(dist / range - 1) * strength
                sprite.change_x += math.sin(sprite.radians) * impact
                sprite.change_y += math.cos(sprite.radians) * impact

    def shake(self, amplitude, speed=1.5, damping=0.9):
        # A random float between 0 and 2 * pi (A direction in radians)
        d = random.random() * 2 * math.pi
        # A vector in the random direction
        v = Vec2(
            amplitude * math.cos(d),
            amplitude * math.sin(d)
        )
        self.camera_sprites.shake(v, speed, damping)

    def on_show_view(self):
        """ Set up the game and initialize the variables. """

        # Cameras for observing the game. We need two cams, so we can change
        # the view of the game (like shaking) without affecting the GUI.
        self.camera_sprites = arcade.Camera(CONFIG["SCREEN_WIDTH"], CONFIG["SCREEN_HEIGHT"])
        self.camera_GUI = arcade.Camera(CONFIG["SCREEN_WIDTH"], CONFIG["SCREEN_HEIGHT"])

        self.sound_thrust_player = None

        # No points when the game starts
        self.player_score = 0

        # Sprite lists
        self.player_shot_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.power_up_list = arcade.SpriteList()

        self.ufo_list = arcade.SpriteList()
        self.ufo_shot_list = arcade.SpriteList()

        # Small stars in background
        self.stars_list = arcade.SpriteList()

        # Create a Player object
        self.player_sprite = Player(
            wrap_max_x=CONFIG['SCREEN_WIDTH'],
            wrap_max_y=CONFIG['SCREEN_HEIGHT'],
            scale=CONFIG['SPRITE_SCALING'],
            center_x=CONFIG['PLAYER_START_X'],
            center_y=CONFIG['PLAYER_START_Y'],
            lives=CONFIG['PLAYER_START_LIVES'],
            thrust_speed=CONFIG['PLAYER_THRUST'],
            speed_limit=CONFIG['PLAYER_SPEED_LIMIT'],
            invincibility_seconds=CONFIG['PLAYER_INVINCIBILITY_SECONDS'],
            start_speed_min=CONFIG['PLAYER_START_SPEED_MIN'],
            start_speed_max=CONFIG['PLAYER_START_SPEED_MAX'],
            start_angle_min=CONFIG['PLAYER_START_ANGLE_MIN'],
            start_angle_max=CONFIG['PLAYER_START_ANGLE_MAX'],
            fire_rate=CONFIG['PLAYER_FIRE_RATE']
        )

        # load the player shot sound
        self.player_shoot_sound = arcade.load_sound("sounds/laserRetro_001.ogg")

        # setup spawn_ufo to run regularly
        arcade.schedule(self.spawn_ufo, CONFIG['UFO_SPAWN_RATE'] + (self.level - 1) * CONFIG['UFO_SPAWN_RATE_MOD_PR_LEVEL'])

        # Start level 1
        self.next_level(1)

        self.stoppable_emitter = StoppableEmitter(self.player_sprite)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Render from the view of this camera
        self.camera_sprites.use()

        # Stars in the background drawn first
        self.stars_list.draw()

        # draw particle emitter
        # self.thrust_emitter.draw()
        self.stoppable_emitter.emitter.draw()

        # Draw the player shot
        self.player_shot_list.draw()

        # Draw the player sprite
        self.player_sprite.draw()

        # Draw asteroids
        self.asteroid_list.draw()

        # Draw Power Ups
        self.power_up_list.draw()

        # draw ufo(s)
        self.ufo_list.draw()

        # and their shots
        self.ufo_shot_list.draw()

        # draw explosion
        if self.explosion_emitter is not None:
            self.explosion_emitter.draw()

        # Here comes the GUI. Switch camera
        self.camera_GUI.use()

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

        # UFO shooting and direction changing
        for ufo in self.ufo_list:
            # If shooting timer is finished, call shoot
            if ufo.shoot_timer <= 0:
                self.sound_fire.play()
                ufo.shoot()
            # If direction changing timer is finished, call change_dir
            if ufo.change_dir_timer <= 0:
                ufo.change_dir()

        # Stars in background
        for s in self.stars_list:
            # Star's direction is opposite of the player
            s.change_x = -1 * self.player_sprite.change_x
            s.change_y = -1 * self.player_sprite.change_y
            # Wrap star if off screen
            wrap(s, CONFIG['SCREEN_WIDTH'], CONFIG['SCREEN_HEIGHT'])

        # Move all stars
        self.stars_list.on_update(delta_time)

        # Calculate player speed based on the keys pressed
        # Move player with keyboard
        if self.turn_left_pressed and not self.turn_right_pressed:
            self.player_sprite.angle += CONFIG['PLAYER_ROTATE_SPEED'] * self.player_sprite.speed_scale
        elif self.turn_right_pressed and not self.turn_left_pressed:
            self.player_sprite.angle += -CONFIG['PLAYER_ROTATE_SPEED'] * self.player_sprite.speed_scale

        # rotate player with joystick if present
        if self.joystick:
            self.player_sprite.angle += round(self.joystick.x) * -CONFIG['PLAYER_ROTATE_SPEED']

        # checks if ufo shot collides with player
        if not self.player_sprite.is_invincible:
            for ufo_shot_hit in self.player_sprite.collides_with_list(self.ufo_shot_list):
                self.sound_explosion.play()
                self.player_sprite.lives -= 1
                self.player_sprite.reset()
                self.get_explosion(self.player_sprite.position)
                ufo_shot_hit.kill()

        # Check if colliding whit power_up
        for power_up_hit in self.player_sprite.collides_with_list(self.power_up_list):
            self.player_score += power_up_hit.type.get("score", 0)
            self.player_sprite.lives += power_up_hit.type.get("life", 0)
            self.player_sprite.fire_rate *= power_up_hit.type.get("fire_rate", 1.0)
            # power up that adds more asteroids
            for x in range(0, power_up_hit.type.get("add_asteroids", 0)):
                a = Asteroid(
                    scale=CONFIG['SPRITE_SCALING'],
                    screen_width=CONFIG['SCREEN_WIDTH'],
                    screen_height=CONFIG['SCREEN_HEIGHT'],
                    min_spawn_dist_from_player=CONFIG['ASTEROIDS_MINIMUM_SPAWN_DISTANCE_FROM_PLAYER'],
                    player_start_pos=(CONFIG['PLAYER_START_X'], CONFIG['PLAYER_START_Y']),
                    score_values=CONFIG['ASTEROID_SCORE_VALUES'],
                    spread=CONFIG['ASTEROIDS_SPREAD'],
                    speed=CONFIG['ASTEROIDS_SPEED'],
                    level=self.level
                )
                t = arcade.load_texture("images/Meteors/meteorBrown_tiny1.png")
                self.get_explosion(a.position, [t])
                self.asteroid_list.append(a)
            power_up_hit.kill()

        # Check if collision with Asteroids and dies and kills the Asteroid
        if not self.player_sprite.is_invincible:
            for a in self.player_sprite.collides_with_list(self.asteroid_list):
                self.sound_explosion.play()
                self.player_sprite.lives -= 1
                self.player_sprite.reset()
                self.get_explosion(self.player_sprite.position)
                a.kill()

        # check for collision with bonus_ufo
        if not self.player_sprite.is_invincible:
            for ufo in self.player_sprite.collides_with_list(self.ufo_list):
                self.sound_explosion.play()
                self.player_sprite.lives -= 1
                self.player_sprite.reset()
                self.get_explosion(self.player_sprite.position
                                   )
                ufo.kill()

        # Player shot hits UFO
        for shot in self.player_shot_list:
            for ufo_hit in arcade.check_for_collision_with_list(shot, self.ufo_list):
                shot.kill()
                self.sound_explosion.play()
                ufo_hit.kill()
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

                # Shake the camera in proportion to Asteroid size
                self.shake(amplitude=CONFIG["ASTEROIDS_SHAKE_AMPLITUDE"] * a.size)
                self.player_score += a.value
                self.sound_explosion.play()

                t = arcade.load_texture("images/Meteors/meteorGrey_tiny1.png")
                self.get_explosion(a.position, [t], 1, random.randint(4, 7))

                # Split into smaller Asteroids if not smallest size
                if a.size > 1:
                    for n in range(CONFIG['ASTEROIDS_PR_SPLIT']):
                        # A random angle for the the new Asteroid
                        a_angle = random.randrange(
                            int(s.angle - CONFIG["ASTEROIDS_SPREAD"]),
                            int(s.angle + CONFIG["ASTEROIDS_SPREAD"])
                        )
                        # Create an Asteroid
                        new_a = Asteroid(
                            scale=CONFIG['SPRITE_SCALING'],
                            angle=a_angle,
                            screen_width=CONFIG['SCREEN_WIDTH'],
                            screen_height=CONFIG['SCREEN_HEIGHT'],
                            min_spawn_dist_from_player=CONFIG['ASTEROIDS_MINIMUM_SPAWN_DISTANCE_FROM_PLAYER'],
                            player_start_pos=(CONFIG['PLAYER_START_X'], CONFIG['PLAYER_START_Y']),
                            score_values=CONFIG['ASTEROID_SCORE_VALUES'],
                            spread=CONFIG['ASTEROIDS_SPREAD'],
                            speed=CONFIG['ASTEROIDS_SPEED'],
                            size=a.size - 1,
                            level=self.level,
                            spawn_pos=a.position
                        )
                        # Add the new Asteroid to the sprite list
                        self.asteroid_list.append(new_a)
                # Remove shot Asteroid
                a.kill()
                # Remove the shot which hit the Asteroid
                s.kill()

        self.stoppable_emitter.update()
        # check for thrust
        if self.thrust_pressed and self.player_sprite.alpha > 0:
            self.player_sprite.thrust()
            self.stoppable_emitter.start()

        # Update player sprite
        self.player_sprite.on_update(delta_time)

        # Update the player shots
        self.player_shot_list.on_update(delta_time)

        # Update Asteroids
        self.asteroid_list.on_update(delta_time)

        # Update Power Ups
        self.power_up_list.on_update(delta_time)

        # update UFOs
        self.ufo_list.on_update(delta_time)

        # update UFO shot_lists
        self.ufo_shot_list.on_update(delta_time)

        # check if the player is dead
        if self.player_sprite.lives <= 0:
            assert self.sound_thrust is not None
            self.sound_thrust.stop(self.sound_thrust_player)
            arcade.unschedule(self.spawn_ufo)
            game_over_view = GameOverView(player_score=self.player_score, level=self.level)
            self.window.show_view(game_over_view)

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
                if self.player_sprite.fire():
                    new_shot = Shot(
                        filename="images/Lasers/laserBlue01.png",
                        scale=CONFIG['SPRITE_SCALING'],
                        center_x=self.player_sprite.center_x,
                        center_y=self.player_sprite.center_y,
                        angle=self.player_sprite.angle,
                        speed=CONFIG['PLAYER_SHOT_SPEED'],
                        range=CONFIG['PLAYER_SHOT_RANGE'],
                        fade_start=CONFIG['SHOT_FADE_START'],
                        fade_speed=CONFIG['SHOT_FADE_SPEED'],
                        wrap_max_x=CONFIG['SCREEN_WIDTH'],
                        wrap_max_y=CONFIG['SCREEN_HEIGHT'],
                        sound=self.player_shoot_sound

                    )

                    self.sound_fire.play()
                    self.player_shot_list.append(new_shot)


        if key == CONFIG['UI_RESTART_KEY']:
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
        # Press the fire key on the joystick
        if button_no == CONFIG["PLAYER_FIRE_JOYBUTTON"]:
            self.on_key_press(CONFIG["PLAYER_FIRE_KEY"], [])
        elif button_no == CONFIG["PLAYER_THRUST_JOYBUTTON"]:
            self.thrust_pressed = True

    def on_joybutton_release(self, joystick, button_no):
        if button_no == CONFIG["PLAYER_THRUST_JOYBUTTON"]:
            self.thrust_pressed = False
        elif button_no == CONFIG["PLAYER_SELECT_JOYSTICK"]:
            new_game = InGameView()
            self.window.show_view(new_game)

    def on_joyaxis_motion(self, joystick, axis, value):
        pass

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        pass


class GameOverView(arcade.View):
    """
    the game over screen
    """

    def __init__(self, player_score, level):
        super().__init__()

        self.check_if_started = False
        self.game_over_sign = arcade.load_texture("images/UI/asteroidsGameOverSign.png")
        self.basic_button = arcade.load_texture("images/UI/basicButtonSmall.png")
        self.basic_button_hover = arcade.load_texture("images/UI/basicButtonSmallHover.png")

        self.player_score = player_score
        self.level = level

        # Makes the manager that contains the GUI button and enables it to the game.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Make the restart button.
        self.gui_restart_button = arcade.gui.UITextureButton(
            x=CONFIG['BUTTON_X'],
            y=CONFIG['BUTTON_Y'],
            width=100,
            height=100,
            texture=self.basic_button,
            texture_hovered=self.basic_button_hover,
            scale=CONFIG['BUTTON_SCALE'],
            style=None,
            text="Retry"
        )
        # When the GUI button is now clicked it starts the event self.new_game
        self.gui_restart_button.on_click = self.new_game
        # Adds the button to the manager so the manager can draw it.
        self.manager.add(self.gui_restart_button)

        # set background color
        arcade.set_background_color(SCREEN_COLOR)

        self.joystick = get_joystick(
            self.on_joybutton_pressed,
            self.on_joybutton_release,
            print,
            print
            )

    def on_draw(self):
        """
        draw the screen
        """

        arcade.start_render()

        self.game_over_sign.draw_scaled(
            center_x=CONFIG['TITLE_X'],
            center_y=CONFIG['TITLE_Y']
        )

        # Draws the manager that contains the button
        self.manager.draw()

        arcade.draw_text(
            f"SCORE: {self.player_score}    LEVEL: {self.level}",
            CONFIG['SCREEN_WIDTH'] * 0.4,
            CONFIG['SCREEN_HEIGHT'] * 0.6,
            arcade.color.WHITE
        )

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.R:
            self.gui_restart_button.hovered = True

    def on_key_release(self, symbol: int, _modifiers: int):
        if symbol == arcade.key.R:
            self.new_game()

    def on_joybutton_pressed(self, joystick, button_no):
        self.gui_restart_button.hovered = True

    def on_joybutton_release(self, joystick, button_no):
        if not self.check_if_started:
            self.new_game()
            self.check_if_started = True

    def new_game(self, event=None):
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
