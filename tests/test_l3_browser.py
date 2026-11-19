"""Exercise the permanent workshop and rotating cards in disposable Chromium profiles."""
import copy
import unittest

import test_browser as progression


class HeroProgressionBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        progression.ProgressionBrowserTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        progression.ProgressionBrowserTests.tearDownClass.__func__(cls)

    setUp = progression.ProgressionBrowserTests.setUp
    tearDown = progression.ProgressionBrowserTests.tearDown
    page = progression.ProgressionBrowserTests.page
    saved = progression.ProgressionBrowserTests.saved
    continue_game = progression.ProgressionBrowserTests.continue_game
    reload_and_continue = progression.ProgressionBrowserTests.reload_and_continue

    def test_workshop_previews_all_tiers_and_acquired_upgrade_survives_reload(self):
        seed = copy.deepcopy(progression.FIXTURE)
        seed["workshopOpen"] = True
        page = self.page({progression.NORMAL: seed}, viewport={"width": 854, "height": 393})
        self.continue_game(page)
        stages = page.locator("#metaTabs button")
        self.assertEqual(stages.count(), 3)
        self.assertIn("Acquis", stages.nth(0).inner_text())
        self.assertIn("disponible", stages.nth(2).get_attribute("aria-label"))
        stages.nth(2).click()
        self.assertIn("35 %", page.locator("#metaPowerEffect").inner_text())
        page.locator("#metaBuy").click()
        self.reload_and_continue(page)
        saved = self.saved(page)
        self.assertEqual(saved["metaLevels"][0], 3)
        self.assertEqual(saved["stars"], seed["stars"] - 24)
        self.assertEqual(saved["bestWave"], seed["bestWave"])

    def test_rotating_offer_persists_at_an_open_choice_and_in_checkpoint(self):
        seed = copy.deepcopy(progression.FIXTURE)
        seed["g"].update(wave=3, bonus=True, bonusRotation=1)
        page = self.page({progression.NORMAL: seed}, viewport={"width": 320, "height": 568})
        self.continue_game(page)
        cards = page.locator("#bonus .perk")
        self.assertEqual(cards.count(), 4)
        self.assertIn("Brèche", cards.last.inner_text())
        self.reload_and_continue(page)
        self.assertIn("Brèche", cards.last.inner_text())
        cards.last.click()
        self.reload_and_continue(page)
        saved = self.saved(page)
        self.assertIn("shieldBreach", saved["g"]["perks"])
        self.assertIn("shieldBreach", saved["buildCheckpoint"]["perks"])
        self.assertEqual(saved["stars"], seed["stars"])
