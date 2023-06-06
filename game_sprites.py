"""
file that contains all game-sprite classes in the project. They are imported into main when used in-game
"""

from random import randrange, random, randint, uniform, choice
from typing import Tuple
from math import cos, pi, sqrt

import arcade


class ObjInSpace(arcade.Sprite):
    """
    all in-game objects will inherit from this class.
    This class only moves the sprite based on its change_x and change_y, and wraps them to a given width
    """

    def __init__(self, wrap_max_x, wrap_max_y, speed_scale=1.0, **kwargs):

        super().__init__(**kwargs)

        self.wrap_max_x = wrap_max_x
        self.wrap_max_y = wrap_max_y
        self.speed_scale = speed_scale

    def on_update(self, delta_time):

        self.center_x += self.change_x * self.speed_scale
        self.center_y += self.change_y * self.speed_scale

        # wrap
        if self.right < 0:
            self.center_x += self.wrap_max_x
        elif self.left > self.wrap_max_x:
            self.center_x -= self.wrap_max_x

        if self.top < 0:
            self.center_y += self.wrap_max_y
        elif self.bottom > self.wrap_max_y:
            self.center_y -= self.wrap_max_y


class Shot(ObjInSpace):
    """
    universal class for shot objects
    """

    def __init__(self, filename, scale, center_x, center_y, angle, speed, range, fade_start, fade_speed, wrap_max_x, wrap_max_y, speed_scale=1.0, sound=None):

        super().__init__(
            filename=filename,
            scale=scale,
            center_x=center_x,
            center_y=center_y,
            angle=angle,
            flipped_horizontally=True,
            flipped_diagonally=True,
            wrap_max_x=wrap_max_x,
            wrap_max_y=wrap_max_y,
            speed_scale=speed_scale
        )

        self.speed = speed
        self.range = range
        self.fade_start = fade_start
        self.fade_speed = fade_speed
        self.wrap_max_x = wrap_max_x
        self.wrap_max_y = wrap_max_y
        self.speed_scale = speed_scale

        self.distance_traveled = 0

        self.forward(self.speed)

        # play the shot sound if present
        if sound:
            sound.play(speed=self.speed_scale)

    def on_update(self, delta_time):
        """
        move the sprite and fade
        """

        super().on_update(delta_time)

        # check if the shot traveled too far
        self.distance_traveled += self.speed * self.speed_scale

        # FIXME: make a function for when the fading of the shot should start, based on teh range

        # start fading when flown far enough
        if self.distance_traveled > self.fade_start:
            self.alpha *= self.fade_speed * self.speed_scale

        if self.distance_traveled > self.range:
            self.kill()


class Star(arcade.Sprite):
    """
    A flashing star.
    """

    def __init__(self, position: Tuple[int, int], base_size:int = 10, scale:float=0.5, fade_speed:int=30, speed_scale=1.0):
        """
        base_size: The size of the circle texture used for stars.
        scale: Will be multiplied with a random float between 0.0 & 1.0 to calculate the scaling of the star.
        fade_speed: Higher int, slower fade.
        """
        super().__init__(
            texture=arcade.make_circle_texture(diameter=base_size,color=arcade.color.WHITE),
            scale=scale * random(),
            center_x=position[0],
            center_y=position[1],
        )

        #self.angle = arcade.rand_angle_360_deg()

        # Start fade pos between 0 and 2 * pi
        self.fade_pos = 2 * random() * pi

        self.speed_scale = speed_scale

        self.fade_speed = random() / fade_speed

    def on_update(self, delta_time: float = 1/60):
        """
        Move the star while randomly blinking
        """

        # cos() returns floats between -1.0 and 1.0.
        # We want make that a number between 0.0 and 256
        self.alpha = int(128 + (128 * cos(self.fade_pos)))

        self.fade_pos += self.fade_speed

        # Bigger stars move faster than small stars
        self.center_x += self.scale * self.change_x * self.speed_scale
        self.center_y += self.scale * self.change_y * self.speed_scale


class Asteroid(ObjInSpace):

    def __init__(self, scale, screen_width, screen_height, min_spawn_dist_from_player, player_start_pos, score_values, spread, speed, size=3, level=1, speed_scale=1.0, spawn_pos=None, angle=None):
        # Initialize the asteroid

        # Graphics
        super().__init__(
            filename='images/Meteors/meteorGrey_med1.png',
            scale=size * scale,
            wrap_max_x=screen_width,
            wrap_max_y=screen_height,
            speed_scale=speed_scale
        )

        self.size = size
        self.level = level
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.min_spawn_dist_from_player = min_spawn_dist_from_player
        self.player_start_pos = player_start_pos
        self.score_values = score_values
        self.spread = spread
        self.speed = speed
        self.speed_scale = speed_scale

        if angle == None:
            self.angle = randrange(0, 360)
        else:
            self.angle = angle

        # Spawning Astroids until the distance to the player is longer than ASTEROIDS_MINIMUM_SPAWN_DISTANCE_FROM_PLAYER
        if not spawn_pos is None:
            self.position = spawn_pos
        else:
            while True:
                self.center_x = randint(0, self.screen_width)
                self.center_y = randint(0, self.screen_height)

                if arcade.get_distance(
                        self.center_x,
                        self.center_y,
                        self.player_start_pos[0],
                        self.player_start_pos[1]
                ) > min_spawn_dist_from_player:
                    break
        self.angle += randint(-self.spread, self.spread)
        self.forward(self.speed)

        self.level = level

        self.rotation_speed = randrange(0, 5)

        self.direction = self.angle  # placeholder for initial angle - angle changes during the game
        self.value = score_values[self.size - 1]

    def on_update(self, delta_time):

        super().on_update(delta_time)

        # Rotate Asteroid
        self.angle += self.rotation_speed * self.speed_scale


class Player(ObjInSpace):
    """
    The player
    """

    def __init__(self,
                 scale,
                 center_x,
                 center_y,
                 lives,
                 thrust_speed,
                 speed_limit,
                 invincibility_seconds,
                 start_speed_min,
                 start_speed_max,
                 start_angle_min,
                 start_angle_max,
                 wrap_max_x,
                 wrap_max_y,
                 speed_scale=1.0):
        """
        Setup new Player object
        """

        # Graphics to use for Player
        super().__init__(filename="images/playerShip1_red.png",
                         scale=scale,
                         center_x=center_x,
                         center_y=center_y,
                         angle=randint(start_angle_min, start_angle_max),
                         flipped_horizontally=True,
                         flipped_diagonally=True,
                         wrap_max_x=wrap_max_x,
                         wrap_max_y=wrap_max_y,
                         speed_scale=speed_scale)

        self.start_x = center_x
        self.start_y = center_y

        self.lives = lives
        self.thrust_speed = thrust_speed
        self.speed_limit = speed_limit
        self.invincibility_seconds = invincibility_seconds

        self.forward(uniform(start_speed_min, start_speed_max))
        self.invincibility_timer = 0

        self.start_angle_min = start_angle_min
        self.start_angle_max = start_angle_max
        self.start_speed_min = start_speed_min
        self.start_speed_max = start_speed_max

        self.speed_scale = speed_scale

    def thrust(self):
        """
        increase speed in the direction pointing
        """

        self.forward(self.thrust_speed * self.speed_scale)
        # Keep track of Player Speed
        player_speed_vector_length = sqrt(self.change_x ** 2 + self.change_y ** 2)

        # Calculating the value used to lower the players speed while keeping the x - y ratio
        player_x_and_y_speed_ratio = self.speed_limit / player_speed_vector_length

        # If player is too fast slow it down
        if player_speed_vector_length > self.speed_limit * self.speed_scale:
            self.change_x *= player_x_and_y_speed_ratio
            self.change_y *= player_x_and_y_speed_ratio

    def reset(self):
        """
        The code works as when you get hit by the asteroid you will disappear for 2 seconds.
        After that you are invincible for 3 seconds, and you can get hit again.
        """
        self.invincibility_timer = self.invincibility_seconds
        # The Player is Invisible
        self.alpha = 0

    @property
    def is_invincible(self):
        return self.invincibility_timer > 0

    def on_update(self, delta_time):
        """
        Move the sprite and wrap
        """

        super().on_update(delta_time)

        # Time when you can't get hit by an asteroid
        if self.is_invincible:
            self.invincibility_timer -= delta_time * self.speed_scale
            # Time when you are not visible
            if self.invincibility_timer < 3:
                # Visible
                if self.alpha == 0:
                    self.alpha = 155
                    self.center_x = self.start_x
                    self.center_y = self.start_y
                    self.change_y = 0
                    self.change_x = 0
                    self.angle = randint(self.start_angle_min, self.start_angle_max)
                    self.forward(uniform(self.start_speed_min, self.start_speed_max))

        else:
            self.alpha = 255


class BonusUFO(ObjInSpace):
    """occasionally moves across the screen. Grants the player points if shot"""

    sound_fire = arcade.load_sound("sounds/laserRetro_001.ogg")
    sound_explosion = arcade.load_sound("sounds/explosionCrunch_000.ogg")

    def __int__(self, scale, shot_list, target, speed, speed_mod, dir_change_rate, fire_rate, fire_rate_mod, shot_scale, shot_speed, shot_range, shot_fade_start, shot_fade_speed, small_size, big_size, screen_width, screen_height, speed_scale=1.0, **kwargs):

        kwargs['filename'] = "images/ufoBlue.png"

        # UFOs are big or small
        kwargs['scale'] = scale * choice((small_size, big_size))

        # set random position off-screen
        kwargs['center_x'] = choice([0, screen_width])
        kwargs['center_y'] = choice([0, screen_height])

        # send arguments upstairs
        super().__init__(
            wrap_max_x=screen_width,
            wrap_max_y=screen_height,
            speed_scale=speed_scale,
            **kwargs)

        self.shot_list = shot_list
        self.target = target
        self.speed = speed
        self.dir_change_rate = dir_change_rate
        self.fire_rate = fire_rate
        self.fire_rate_mod = fire_rate_mod
        self.shot_scale = shot_scale
        self.shot_speed = shot_speed
        self.shot_range = shot_range
        self.shot_fade_start = shot_fade_start
        self.shot_fade_speed = shot_fade_speed
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.shoot_timer = fire_rate + fire_rate_mod
        self.change_dir_timer = dir_change_rate

        # set random direction. always point towards center, with noise
        self.change_x = randrange(1, speed) + speed_mod
        if self.center_x > screen_width / 2:
            self.change_x *= -1

        self.change_y = speed - self.change_x + speed_mod
        if self.center_y > screen_height / 2:
            self.change_y *= -1

    def change_dir(self):
        """
        set a new direction
        """

        r = randrange(-self.speed, self.speed)
        self.change_x -= r
        self.change_y += r

        self.change_dir_timer = self.dir_change_rate

    def shoot(self):
        """
        fire a new shot
        """

        # -1 and + 90 is to make the UFO shoot the right way
        new_angle = -1 * arcade.get_angle_degrees(
                self.center_x,
                self.center_y,
                self.target.center_x,
                self.target.center_y
            ) + 90

        new_ufo_shot = Shot(
            filename="images/Lasers/laserGreen07.png",
            scale=self.shot_scale,
            center_x=self.center_x,
            center_y=self.center_y,
            angle=new_angle,
            speed=self.shot_speed,
            range=self.shot_range,
            fade_start=self.shot_fade_start,
            fade_speed=self.shot_fade_speed,
            wrap_max_x=self.screen_width,
            wrap_max_y=self.screen_height,
            sound=BonusUFO.sound_fire)

        self.shot_list.append(new_ufo_shot)

        self.shoot_timer = self.fire_rate + self.fire_rate_mod

    def on_update(self, delta_time):
        """update position, and kill if out of bounds"""

        # keep spinning. just for graphics purposes
        self.angle += self.change_x + self.change_y  # the faster it moves, the faster it spins.

        self.center_x += self.change_x
        self.center_y += self.change_y

        self.shoot_timer -= delta_time
        self.change_dir_timer -= delta_time

        # kill if out of bounds
        if self.center_x > self.screen_width or self.center_x < 0 or self.center_y > self.screen_height or self.center_y < 0:
            self.destroy()

    def destroy(self):
        """
        kill the sprite and unschedule all functions
        """
        arcade.unschedule(self.shoot)
        arcade.unschedule(self.change_dir)
        self.kill()



class PowerUp(ObjInSpace):

    # PowerUp colors: Green: Lvl 1, Yellow Lvl 2; Red: Lvl 3
    pu_types = [
        {"filename": "images/Power-ups/powerupGreen_star.png",
         "score": 300,
         "lifetime": 15
         },
        {"filename": "images/Power-ups/powerupYellow_star.png",
         "score": 600,
         "lifetime": 10
         },
        {"filename": "images/Power-ups/powerupRed_star.png",
         "score": 1000,
         "lifetime": 5
         },
        {"filename": "images/Power-ups/powerupGreen_shield.png",
         "life": 1,
         "lifetime": 15
         },
        {"filename": "images/Power-ups/powerupYellow_shield.png",
         "life": 2,
         "lifetime": 10
         },
        {"filename": "images/Power-ups/powerupRed_shield.png",
         "life": 3,
         "lifetime": 5
         }
    ]

    def __init__(self, start_max_x, start_max_y, wrap_max_x, wrap_max_y, speed):

        # Random Type
        self.type = choice(PowerUp.pu_types)

        super().__init__(
            filename=self.type["filename"],
            center_x=randint(0, start_max_x),
            center_y=randint(0, start_max_y),
            wrap_max_x=wrap_max_x,
            wrap_max_y=wrap_max_y
        )

        self.angle = randint(0, 360)
        self.forward(speed)
        # time till death in sec
        self.lifetimer = self.type["lifetime"]

    def on_update(self, delta_time):
        super().on_update(delta_time)
        self.lifetimer -= delta_time
        if self.lifetimer <= 0:
            self.kill()