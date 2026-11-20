"""The Fortress briefing shares its rules with the active wave and resume."""
import copy
import unittest

import test_browser as progression


class FortressBrowserTests(unittest.TestCase):
    setUpClass = classmethod(progression.ProgressionBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(progression.ProgressionBrowserTests.tearDownClass.__func__)
    setUp = progression.ProgressionBrowserTests.setUp
    tearDown = progression.ProgressionBrowserTests.tearDown
    page = progression.ProgressionBrowserTests.page
    saved = progression.ProgressionBrowserTests.saved
    continue_game = progression.ProgressionBrowserTests.continue_game
    reload_and_continue = progression.ProgressionBrowserTests.reload_and_continue

    def fortress(self, *, active):
        seed=copy.deepcopy(progression.FIXTURE)
        seed.update(level=2,paused=active,buildCheckpoint=None)
        seed["g"].update(wave=9 if active else 8,money=200,
            active=active,ended=False,bonus=False,total=32,spawned=0,clock=3)
        page=self.page({progression.NORMAL:seed},viewport={"width":854,"height":393})
        self.continue_game(page)
        return page

    def test_forecast_shows_convoy_and_retains_it_midwave(self):
        page=self.fortress(active=False)
        hint=page.locator("#airHint")
        self.assertIn("V9 · Convoi · 4 blindés",hint.inner_text())
        self.assertNotIn("volant",hint.inner_text())
        page.locator("#start").tap()
        page.locator("#pause").tap()
        self.assertEqual(self.saved(page)["g"]["activeAirKind"],"")
        self.reload_and_continue(page)
        self.assertIn("V9 · Convoi · 4 blindés",hint.inner_text())
        self.assertEqual(page.locator("#pause").get_attribute("aria-pressed"),"true")

    def test_historical_active_wave_still_shows_air(self):
        page=self.fortress(active=True)
        hint=page.locator("#airHint").inner_text()
        self.assertIn("volants",hint)
        self.assertNotIn("Convoi",hint)
        self.assertNotIn("activeAirKind",self.saved(page)["g"])
