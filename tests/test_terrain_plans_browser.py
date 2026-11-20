"""Exercise the pilot's three moments and their mobile display."""
import copy
import unittest

import test_browser as progression


class TerrainPlansBrowserTests(unittest.TestCase):
    setUpClass = classmethod(progression.ProgressionBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(progression.ProgressionBrowserTests.tearDownClass.__func__)
    setUp = progression.ProgressionBrowserTests.setUp
    tearDown = progression.ProgressionBrowserTests.tearDown
    page = progression.ProgressionBrowserTests.page
    saved = progression.ProgressionBrowserTests.saved
    continue_game = progression.ProgressionBrowserTests.continue_game
    reload_and_continue = progression.ProgressionBrowserTests.reload_and_continue

    def offer(self, wave, level, *, life=15, towers=None):
        seed=copy.deepcopy(progression.FIXTURE)
        seed.update(level=level,buildCheckpoint=None)
        seed["g"].update(wave=wave,bonus=True,active=False,ended=False,
                         planOffer=True,life=life,towers=towers or {})
        page=self.page({progression.NORMAL:seed},viewport={"width":568,"height":320})
        self.continue_game(page)
        return page

    def test_budget_timing_and_selection_survive_reload(self):
        page=self.offer(3,1)
        bonus=page.locator("#bonus")
        self.assertEqual(bonus.locator("h2").inner_text(),"Budget")
        card=bonus.locator(".perk").filter(has_text="Contrat")
        self.assertIn("+55 Z pour chaque vague terminée, V4 et V5",card.inner_text())
        supplies=bonus.locator(".perk").filter(has_text="Ravitaillement")
        self.assertIn("+75 Z",supplies.inner_text())
        self.assertIn("immédiats",supplies.inner_text())
        self.assertIn("+110 Z",card.inner_text())
        self.reload_and_continue(page)
        card.tap()
        self.assertIn("Contrat · jusqu’à V5",page.locator("#airHint").inner_text())
        self.assertEqual(self.saved(page)["g"]["money"],progression.FIXTURE["g"]["money"])
        self.reload_and_continue(page)
        self.assertIn("contract",self.saved(page)["g"]["perks"])
        self.assertFalse(bonus.is_visible())

    def test_tactics_and_last_wave_have_usable_cards_within_the_viewport(self):
        towers={"31":{"type":3,"lvl":1,"invested":155,"fresh":False,"cd":0}}
        page=self.offer(6,2,towers=towers)
        bonus=page.locator("#bonus")
        self.assertEqual(bonus.locator("h2").inner_text(),"Tactique")
        self.assertIn("Actif de V7 à V10",bonus.inner_text())
        self.assertIn("Convoi blindé en V9",bonus.inner_text())
        self.assertNotIn("Brèche",bonus.inner_text())
        cards=bonus.locator(".perk")
        self.assertEqual(cards.count(),3)
        for card in cards.all():
            box=card.bounding_box()
            self.assertGreaterEqual(box["y"],0)
            self.assertLessEqual(box["y"]+box["height"],320)
            self.assertGreaterEqual(box["height"],44)
        cards.filter(has_text="Long hiver").tap()
        self.assertIn("Long hiver · jusqu’à V10",page.locator("#airHint").inner_text())
        final=self.offer(9,0,life=14)
        bonus=final.locator("#bonus")
        self.assertEqual(bonus.locator("h2").inner_text(),"Dernière vague")
        repair=bonus.locator(".perk").filter(has_text="Réparation")
        self.assertIn("+1",repair.inner_text())
        repair.tap()
        self.assertEqual(self.saved(final)["g"]["life"],15)
