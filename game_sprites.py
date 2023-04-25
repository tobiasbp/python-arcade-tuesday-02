"""
file that contains all game-sprite classes in the project. They are imported into main when used in-game
"""

from random import randrange, random, randint, uniform
from typing import Tuple
from math import cos, pi, sqrt

import arcade


class ObjInSpace(arcade.Sprite):
    """
    base obj for all other sprites
    this obj only wraps, and moves
    """

    def __init__(self, wrap_max_x, wrap_max_y, **kwargs):


        super().__init__(**kwargs)

        self.wrap_max_x = wrap_max_x
        self.wrap_max_y = wrap_max_y

    def update(self):

        self.center_x += self.change_x
        self.center_y += self.change_y

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

    def __init__(self, filename, scale, center_x, center_y, angle, speed, range, fade_start, fade_speed, wrap_max_x, wrap_max_y, sound=None):

        super().__init__(
            filename=filename,
            scale=scale,
            center_x=center_x,
            center_y=center_y,
            angle=angle,
            flipped_horizontally=True,
            flipped_diagonally=True,
            wrap_max_x=wrap_max_x,
            wrap_max_y=wrap_max_y
        )

        self.speed = speed
        self.range = range
        self.fade_start = fade_start
        self.fade_speed = fade_speed
        self.wrap_max_x = wrap_max_x
        self.wrap_max_y = wrap_max_y

        self.distance_traveled = 0

        self.forward(self.speed)

        # play the shot sound if present
        if sound:
            sound.play()

    def update(self):
        """
        move the sprite and fade
        """

        super().update()

        # check if the shot traveled too far
        self.distance_traveled += self.speed

        # start fading when flown far enough
        if self.distance_traveled > self.fade_start:
            self.alpha *= self.fade_speed

        if self.distance_traveled > self.range:
            self.kill()



class Star(arcade.Sprite):
    """
    A flashing star.
    """

    def __init__(self, position: Tuple[int, int], base_size:int = 10, scale:float=0.5, fade_speed:int=30):
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
        self.center_x += self.scale * self.change_x
        self.center_y += self.scale * self.change_y


class Asteroid(ObjInSpace):

    def __init__(self, scale, screen_width, screen_height, min_spawn_dist_from_player, player_start_pos, score_values, spread, speed, size=3, level=1, spawn_pos=None, angle=None):
        # Initialize the asteroid

        # Graphics
        super().__init__(
            filename='images/Meteors/meteorGrey_med1.png',
            scale=size * scale,
            wrap_max_x=screen_width,
            wrap_max_y=screen_height
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

    def update(self):

        super().update()

        # Rotate Asteroid
        self.angle += self.rotation_speed


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
                 wrap_max_y):
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
                         wrap_max_y=wrap_max_y)

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

    def thrust(self):
        """
        increase speed in the direction pointing
        """

        self.forward(self.thrust_speed)
        # Keep track of Player Speed
        player_speed_vector_length = sqrt(self.change_x ** 2 + self.change_y ** 2)

        # Calculating the value used to lower the players speed while keeping the x - y ratio
        player_x_and_y_speed_ratio = self.speed_limit / player_speed_vector_length

        # If player is too fast slow it down
        if player_speed_vector_length > self.speed_limit:
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
                    self.center_x = self.start_x
                    self.center_y = self.start_y
                    self.change_y = 0
                    self.change_x = 0
                    self.angle = randint(self.start_angle_min, self.start_angle_max)
                    self.forward(uniform(self.start_speed_min, self.start_speed_max))

        else:
            self.alpha = 255
