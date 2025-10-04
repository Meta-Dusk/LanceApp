import flet as ft

from main_ui import main_app
from setup import before_main_app

# TODO: Implement a feature to disable/enable debug mode
DEBUG = False


async def main(page: ft.Page):
    await main_app(page=page, debug=DEBUG)

async def before_main(page: ft.Page):
    await before_main_app(page=page, debug=DEBUG)


if __name__ == "__main__":
    ft.run(main=main, before_main=before_main)