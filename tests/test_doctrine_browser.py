"""Exercise doctrine selection and persistence in Chromium mobile."""
import copy
import unittest

import test_browser as progression


class DoctrineBrowserTests(unittest.TestCase):
    setUpClass = classmethod(progression.ProgressionBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(progression.ProgressionBrowserTests.tearDownClass.__func__)
    setUp = progression.ProgressionBrowserTests.setUp
    tearDown = progression.ProgressionBrowserTests.tearDown
    page = progression.ProgressionBrowserTests.page
    saved = progression.ProgressionBrowserTests.saved
    continue_game = progression.ProgressionBrowserTests.continue_game
    reload_and_continue = progression.ProgressionBrowserTests.reload_and_continue

    def test_choice_is_tappable_persists_and_does_not_pay_stars(self):
        seed=copy.deepcopy(progression.FIXTURE)
        seed["g"].update(wave=5,active=False,ended=False,bonus=True,bossDefeated=True,bossKills=1)
        page=self.page({progression.NORMAL:seed},viewport={"width":854,"height":393})
        self.continue_game(page)
        self.assertIn("Choisis ta doctrine",page.locator("#bonus h2").inner_text())
        self.assertEqual(page.locator("#bonus .perk").count(),3)
        self.reload_and_continue(page)
        page.locator("#bonus .perk").filter(has_text="Escadron").tap()
        stored=self.saved(page)
        self.assertEqual(stored["g"]["doctrine"],"escadron")
        self.assertEqual(stored["buildCheckpoint"]["doctrine"],"escadron")
        self.assertEqual(stored["stars"],seed["stars"])
        self.reload_and_continue(page)
        self.assertIn("Escadron",page.locator("#airHint").inner_text())
        self.assertFalse(page.locator("#bonus").is_visible())

    def test_transition_retains_doctrine_and_clears_local_bonus(self):
        seed=copy.deepcopy(progression.FIXTURE)
        seed["buildCheckpoint"]=None
        seed["g"].update(wave=10,active=False,ended=True,bonus=False,life=12,
                         doctrine="embuscade",perks=["tom"])
        page=self.page({progression.NORMAL:seed},viewport={"width":854,"height":393})
        self.continue_game(page)
        page.locator("#nextMap").tap()
        state=self.saved(page)
        self.assertEqual(state["level"],1)
        self.assertEqual(state["g"]["doctrine"],"embuscade")
        self.assertEqual(state["g"]["perks"],[])
        self.assertIn("Embuscade",page.locator("#airHint").inner_text())
