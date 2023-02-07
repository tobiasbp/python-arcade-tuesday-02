from random import randint, random
from typing import Tuple

import arcade

class Star(arcade.Sprite):
    """
    A flashing star.
    """    
    def __init__(self, position: Tuple[int, int], size:int = 10, scale:float=0.5, alpha_min:int=0, alpha_max:int=255):

        super().__init__(
            texture=arcade.make_circle_texture(diameter=size,color=arcade.color.WHITE),
            scale=scale * random(),
            center_x=position[0],
            center_y=position[1],
        )
        
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.angle = arcade.rand_angle_360_deg()

        self.blink()

    def blink(self):
        """
        Randomly set alpha
        """
        self.alpha = randint(self.alpha_min, self.alpha_max)

    def on_update(self, delta_time: float = 1/60):
        """
        Move the star while randomly blinking
        """
        if randint(1, 10) == 1:
            self.blink()
        
        # Bigger stars move faster than small stars
        self.center_x += self.scale * self.change_x
        self.center_y += self.scale * self.change_y