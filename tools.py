"""
The tools that help in the game...
Like the Joysticks.
"""

import arcade
from typing import Tuple
import random

PARTICLE_COLORS = [
    arcade.color.ORANGE,
    arcade.color.BURNT_ORANGE,
    arcade.color.RED_ORANGE
]


def wrap(sprite: arcade.Sprite, max_x: int, max_y: int):
    """
    if sprite is off-screen move it to the other side of the screen
    """
    if sprite.right < 0:
        sprite.center_x += max_x
    elif sprite.left > max_x:
        sprite.center_x -= max_x

    if sprite.top < 0:
        sprite.center_y += max_y
    elif sprite.bottom > max_y:
        sprite.center_y -= max_y


def get_joystick(func_press, func_release=None, func_axis=None, func_jhat=None):
    """
    :param func_press:
    :param func_release:
    :param func_axis:
    :param func_jhat:
    :return:
    """
    # Get list of joysticks
    joysticks = arcade.get_joysticks()

    if joysticks:
        print("Found {} joystick(s)".format(len(joysticks)))

        # Use 1st joystick found
        js = joysticks[0]

        # Communicate with joystick
        js.open()

        # Map joysticks functions to local functions
        js.on_joybutton_press = func_press
        if func_release is not None:
            js.on_joybutton_release = func_release
        if func_axis is not None:
            js.on_joyaxis_motion = func_axis
        if func_jhat is not None:
            js.on_joyhat_motion = func_jhat

        return js

    else:
        return None


class StoppableEmitter:
    """
    It is possible to start and stop this emitter
    """

    def __init__(self,
                 target: arcade.Sprite,
                 particle_lifetime: float = 0.5,
                 noise: int = 15,
                 offset: Tuple[int] = (0, 5),
                 emit_interval: float = 0.01,
                 particle_count: int = 30,
                 start_alpha: int = 100):
        self.target = target
        self.noise = noise
        self.emit_interval = emit_interval
        self.particle_count = particle_count
        self.particle_color = PARTICLE_COLORS[random.randint(0, 2)]

        # Emit controller enters endless loop with an interval of 0
        assert self.emit_interval > 0, "Emit interval must be greater than 0"

        # An emitter with a controller which does not have particles to emit (it's off)
        self.emitter = arcade.Emitter(
            center_xy=target.position,
            emit_controller=arcade.EmitterIntervalWithCount(self.emit_interval, 0),
            particle_factory=lambda emitter: arcade.FadeParticle(
                filename_or_texture=arcade.make_circle_texture(random.randint(7, 30), self.particle_color),
                change_xy=offset,
                lifetime=particle_lifetime,
                start_alpha=start_alpha
            )
        )

    def start(self):
        """
        Start emitter
        """
        self.emitter.rate_factory = arcade.EmitterIntervalWithCount(self.emit_interval, self.particle_count)

    def stop(self):
        """
        Stop emitter
        """
        self.emitter.rate_factory = arcade.EmitterIntervalWithCount(self.emit_interval, 0)

    def update(self):
        self.emitter.center_x, self.emitter.center_y = self.target.position
        self.emitter.angle = (self.target.angle + 90) + random.randint(-1 * self.noise, self.noise)
        self.emitter.update()
        self.particle_color = PARTICLE_COLORS[random.randint(0, 2)]
