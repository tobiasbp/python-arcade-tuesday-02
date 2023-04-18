"""
The tools that help in the game...
Like the Joysticks.
"""

import arcade

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
