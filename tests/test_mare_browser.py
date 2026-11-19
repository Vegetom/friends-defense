"""Verify tactical briefings and tower relocation in the real mobile game."""
import copy
import unittest

import test_browser as progression


class MareBrowserTests(unittest.TestCase):
    setUpClass = classmethod(progression.ProgressionBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(progression.ProgressionBrowserTests.tearDownClass.__func__)
    setUp = progression.ProgressionBrowserTests.setUp
    tearDown = progression.ProgressionBrowserTests.tearDown
    page = progression.ProgressionBrowserTests.page
    saved = progression.ProgressionBrowserTests.saved
    continue_game = progression.ProgressionBrowserTests.continue_game
    reload_and_continue = progression.ProgressionBrowserTests.reload_and_continue

    def mare(self, *, active=False):
        seed=copy.deepcopy(progression.FIXTURE)
        seed.update(level=1,paused=active,buildCheckpoint=None)
        seed["g"].update(wave=2 if active else 1,active=active,ended=False,bonus=False,
                         towers={"31":{"type":0,"lvl":2,"invested":85,"fresh":False,"cd":0}},
                         total=16 if active else 0,spawned=2 if active else 0,clock=10)
        page=self.page({progression.NORMAL:seed},viewport={"width":854,"height":393})
        self.continue_game(page)
        return page

    @staticmethod
    def tap_cell(page,cell):
        board=page.locator("#board")
        board.scroll_into_view_if_needed()
        box=board.bounding_box()
        page.touchscreen.tap(box["x"]+box["width"]*((cell%10)+.5)/10,
                            box["y"]+box["height"]*((cell//10)+.5)/8)

    def test_preparation_counts_and_single_move_survive_reload(self):
        page=self.mare()
        self.assertIn("V2 · 4 volants",page.locator("#airHint").inner_text())
        self.tap_cell(page,31)
        page.locator("#relocate").tap()
        self.tap_cell(page,34)
        self.assertNotIn("relocated",self.saved(page)["g"])
        self.assertIn("impossible",page.locator("#info").inner_text())
        self.tap_cell(page,32)
        moved=self.saved(page)
        self.assertEqual(moved["g"]["towers"]["32"]["lvl"],2)
        self.assertEqual(moved["g"]["towers"]["32"]["invested"],85)
        self.assertEqual(moved["g"]["money"],progression.FIXTURE["g"]["money"])
        self.assertEqual(moved["stars"],progression.FIXTURE["stars"])
        self.reload_and_continue(page)
        self.tap_cell(page,32)
        self.assertTrue(page.locator("#relocate").is_hidden())
        self.assertTrue(self.saved(page)["g"]["relocated"])
        page.locator("#start").tap()
        self.assertEqual(self.saved(page)["g"]["activeAirKind"],"mixed")

    def test_loaded_wave_keeps_historical_briefing_until_completion(self):
        page=self.mare(active=True)
        self.assertIn("V2",page.locator("#airHint").inner_text())
        self.assertNotIn("volant",page.locator("#airHint").inner_text())
        self.assertNotIn("activeAirKind",self.saved(page)["g"])
        self.assertTrue(page.locator("#start").is_disabled())
