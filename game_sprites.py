"""
file that contains all game-sprite classes in the project. They are imported into main when used in-game
"""

from random import randint, random
from typing import Tuple
from math import cos, pi

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
