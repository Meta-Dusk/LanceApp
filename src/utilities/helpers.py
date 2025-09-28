import random

from typing import List, Tuple, Optional
from ui.images import Miku


def rnd_miku_chat(miku_chat_params: List[Tuple[str, Miku, Optional[float]]]) -> List[Tuple[str, Miku, Optional[float]]]:
    """
    Chooses a random index from the list of tuples, which represent the parameters of
    the `miku_chat()` function. Make sure to unpack the tuple with `*` inside the function.
    `miku_chat_params` is a list of tuples, that contains a `msg: str`, an `emote: Miku`
    and an optional `duration: float`.
    
    Args:
        miku_chat_params (list): A list of tuples.
        
    Returns:
        list: Use this inside the `miku_chat()` function, and make sure to unpack with `*`.
    """
    return random.choice(miku_chat_params)