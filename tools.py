"""
The tools that help in the game...
Like the Joysticks.
"""

import arcade
import random
from game_sprites import Star

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

def get_stars(no_of_stars: int, max_x: int, max_y: int, base_size: int, scale: int, fadespeed: int) -> arcade.SpriteList:
    """
    Return a SpriteList of randomly positioned stars.
    """

    # A list to store the stars in
    stars = arcade.SpriteList()

    # Add stars
    for i in range(no_of_stars):
        # Calculate a random postion
        p = (
            random.randint(0, max_x),
            random.randint(0, max_y),
        )
        # Add star
        s = Star(
            position=p,
            base_size=base_size,
            scale=scale,
            fade_speed=fadespeed,
        )
        stars.append(s)

    return stars
