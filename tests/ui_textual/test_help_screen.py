import asyncio

from textual.app import App

from tko.ui_textual.app import HelpScreen


class _HelpApp(App[None]):
    BINDINGS = [("h", "help", "Help")]

    def action_help(self) -> None:
        self.push_screen(HelpScreen())


def test_help_screen_opens_and_closes() -> None:
    async def exercise() -> None:
        app = _HelpApp()
        async with app.run_test() as pilot:
            default_screen = app.screen
            await pilot.press("h")
            assert isinstance(app.screen, HelpScreen)
            await pilot.press("escape")
            assert app.screen is default_screen

    asyncio.run(exercise())
