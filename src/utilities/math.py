import flet as ft

import math
import random

from typing import Union, Tuple


def is_within_radius(
    center: Union[ft.Offset, Tuple[float, float]],
    point: Union[ft.Offset, Tuple[float, float]],
    radius: float,
) -> bool:
    """
    Checks if a `point` lies within the `radius` distance from `center`.
    
    Args:
        center (Offset or Tuple[float, float]): Takes an `Offset` value or a tuple of two floats.
        point (Offset or Tuple[float, float]): Takes an `Offset` value or a tuple of two floats.
        radius float: The radius distance.
    
    Returns:
        bool: True if point is inside or on the circle, False otherwise.
    """
    # normalize input
    if isinstance(center, ft.Offset):
        cx, cy = center.x, center.y
    else:
        cx, cy = center

    if isinstance(point, ft.Offset):
        px, py = point.x, point.y
    else:
        px, py = point

    dx = px - cx
    dy = py - cy
    distance = math.hypot(dx, dy)

    return distance <= radius

def chance(percent: int) -> bool:
    """
    Returns `True` with the given percentage chance.
    
    Args:
        percent (int): 0-100, percentage chance.
    
    Returns:
        bool: `True` if the event occurs, False otherwise.
    """
    if percent <= 0:
        return False
    if percent >= 100:
        return True
    return random.random() < (percent / 100.0)