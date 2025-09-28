import flet as ft

from ui.images import Miku
from utilities.data import get_day_period
from utilities.debug import get_full_username
from utilities.helpers import rnd_miku_chat
from utilities.monitor import get_monitor_for_window

# TODO: Make a class for chatting, if possible

CHAT_GREETINGS = [
    (f"Hello there {get_full_username()}! (｡･∀･)ﾉﾞ", Miku.HAPPY),
    ("Hello, I'm Hatsune Miku! ヾ(•ω•`)o", Miku.HAPPY),
    (f"Good {get_day_period(return_str=True).capitalize()}! Genki? ヾ(^▽^*)))", Miku.HAPPY),
    (f"Let's start the {get_day_period(return_str=True)} feeling energized! o(^▽^)o", Miku.JOY),
]

EXIT_APP_MSGS = [
    ("\'Til next time! ヽ（≧□≦）ノ", Miku.HAPPY),
    ("Don't forget about me! (≧﹏ ≦)", Miku.AMGRY),
    ("I'm going to miss you... 〒▽〒", Miku.PONDER),
    ("Don't forget to review!\nヾ(≧▽≦*)o", Miku.ECSTATIC),
]

WHEN_HEADPAT_MSGS = [
    ("I-I do like h-headpats (≧﹏ ≦)", Miku.PONDER),
    ("Hehehe~ (p≧w≦q)", Miku.ECSTATIC),
    ("Headpats? Yippee q(≧▽≦q)", Miku.ECSTATIC),
    ("I-I don't mind h-headpats\n(≧﹏ ≦)", Miku.PONDER),
]

WHEN_DRAGGED_MSGS = [
    ("Where we going? o((>ω< ))o", Miku.ECSTATIC),
    ("Weeeee \\(≧▽≦)/", Miku.ECSTATIC),
    ("P-please be gentle... (*/ω＼*)", Miku.PONDER),
    ("You can place me in any monitor space! ヾ(•ω•`)o", Miku.GLASSES),
]

AFTER_DRAGGED_MSGS = [
    ("╰(￣ω￣ｏ)", Miku.HAPPY),
]

def after_dragged_msgs(page: ft.Page):
    m = get_monitor_for_window(page=page)
    status = "currently" if m.is_primary else "NOT"
    add_list = [
        (f"Hmm... My sources tell me that I'm {status} in your main monitor! "
         f"And its name is\n{m.name}? ( *︾▽︾)", Miku.READING),
        (f"The monitor name {m.name} sounds weird (°ー°〃)", Miku.PONDER),
        (f"Your monitor is quite spacious... A {m.width} x {m.height} monitor is cool!\n( •̀ ω •́ )y", Miku.ECSTATIC),
    ]
    new_list = AFTER_DRAGGED_MSGS + add_list
    return new_list

WHEN_IN_VOID_MSGS = [
    ("W-woah... So that's what the void looks like (⊙_⊙;)", Miku.SHOCK),
    ("W-what was that? I-I think I saw something over there... (*゜ー゜*)", Miku.SHOCK),
    ("I wonder what will happen if I kept going...", Miku.SHOCK),
]

WHEN_FED_UP_MSGS = [
    ("Grr, I've had enough! (* ￣︿￣)", Miku.AMGRY),
    ("Hmph, suit yourself! I'm leaving! ￣へ￣", Miku.AMGRY),
    ("andfgknjdf,mcvngopdifgnbye ヽ（≧□≦）ノ", Miku.AMGRY),
]

WHEN_FLUSTERED_MSGS = [
    ("W-what are you doing?! ヽ（≧□≦）ノ", Miku.SHOCK),
    ("S-stop it! (〃＞目＜)", Miku.SHOCK),
    ("I'm not yet ready for those kind of stuff... (。>︿<)_θ", Miku.PONDER),
    ("And what are you trying to do, huh? (ㆆ_ㆆ)", Miku.AMGRY),
    ("Keep going, and I'll just leave! (╯▔皿▔)╯", Miku.AMGRY),
    ("I cannot offer you comfort in that way... (/_ \\ )", Miku.PONDER),
    ("Eeeeeeehh-? Nani wo shiterun desuka!? o(≧口≦)o", Miku.SHOCK),
    ("S-soko dameee-! ヾ(≧へ≦)〃", Miku.SHOCK),
]