"""Exercise both prototype layouts, save isolation and the Bastion checkpoint."""
import copy
import unittest

import test_browser as progression


PROTOTYPE = "friends-defense-proto-paliers-save-v38"


class PrototypePaliersBrowserTests(unittest.TestCase):
    setUpClass = classmethod(progression.ProgressionBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(progression.ProgressionBrowserTests.tearDownClass.__func__)
    setUp = progression.ProgressionBrowserTests.setUp
    tearDown = progression.ProgressionBrowserTests.tearDown
    page = progression.ProgressionBrowserTests.page
    saved = progression.ProgressionBrowserTests.saved
    continue_game = progression.ProgressionBrowserTests.continue_game
    reload_and_continue = progression.ProgressionBrowserTests.reload_and_continue

    def assert_on_screen(self, page, selector, width=568, height=320):
        box = page.locator(selector).bounding_box()
        self.assertIsNotNone(box, selector)
        self.assertGreaterEqual(box["x"],0,box)
        self.assertGreaterEqual(box["y"],0,box)
        self.assertLessEqual(box["x"]+box["width"],width,box)
        self.assertLessEqual(box["y"]+box["height"],height,box)

    def test_independent_lab_profiles_and_playable_maps(self):
        for level,(slug,name,route) in enumerate([
            ("plaine","Plaine",9),("mare","Mare",16),("forteresses","Forteresses",10),
            ("bastion","Bastion",22),("defile","Défilé",14),("archipel","Archipel",13),
            ("couronne","Couronne",16),
        ]):
            with self.subTest(name=name):
                page = self.page({progression.NORMAL:progression.FIXTURE},
                                 query="?prototype=1",viewport={"width":568,"height":320})
                page.locator("#labChoice").select_option(slug)
                page.locator("#openLab").tap()
                page.wait_for_url("**&lab="+slug)
                self.assertIn(name.lower(), page.locator("#menuNew").inner_text().lower())
                page.locator("#menuNew").tap()
                self.assert_on_screen(page,"#metaPlay")
                page.locator("#metaPlay").tap()
                self.assert_on_screen(page,"#board")
                self.assertIn(str(route)+" cases",page.locator("#route").inner_text())
                key = f"friends-defense-proto-paliers-lab-{level}-save-v38"
                before = self.saved(page,key)
                self.assertEqual((before["level"],before["g"]["wave"]),(level,0))
                self.assertGreater(max(before["metaLevels"]),0)
                self.assertEqual(self.saved(page),progression.FIXTURE)
                page.locator("#start").tap()
                page.locator("#pause").tap()
                self.reload_and_continue(page)
                self.assertEqual(self.saved(page,key)["g"]["wave"],1)
                self.assertEqual(self.saved(page),progression.FIXTURE)

    def test_checkpoint_unlocks_on_terrain_three_win_and_restarts_without_rewards(self):
        seed = copy.deepcopy(progression.FIXTURE)
        seed.update(level=2,bestWave=27,buildCheckpoint=None)
        seed["g"].update(wave=10,active=False,ended=True,life=4,bonus=False,bossDefeated=True)
        page = self.page({progression.NORMAL:seed},viewport={"width":568,"height":320})
        self.continue_game(page)
        self.assertTrue(page.locator(".unlockBastion").is_visible())
        self.assertTrue(self.saved(page)["bastionUnlocked"])
        page.locator("#nextMap").tap()
        page.locator("#mapsButton").tap()
        page.locator("#rrImprove").tap()
        self.assert_on_screen(page,"#metaPlay")
        self.assert_on_screen(page,"#metaPlain")
        page.locator("#metaPlay").tap()
        start = self.saved(page)
        self.assertEqual((start["level"],start["g"]["wave"],start["g"]["money"]),(3,0,215))
        self.assertEqual(start["metaLevels"],seed["metaLevels"])
        self.assertEqual(start["runHearts"],0)
        self.assertNotIn("doctrine",start["g"])
        self.reload_and_continue(page)
        self.assertEqual(self.saved(page)["g"]["runStart"],3)
        page.locator("#start").tap()
        page.locator("#mapsButton").tap()
        end = self.saved(page)
        self.assertEqual((end["stars"],end["bestWave"]),(start["stars"],start["bestWave"]))
        self.assertEqual(end["metaLastEarned"]["earned"],0)
        self.assertEqual(page.locator(".rrStage.done").count(),0)
        page.locator("#rrImprove").tap()
        page.locator("#metaPlain").tap()
        self.assertEqual(self.saved(page)["level"],0)
        self.assertTrue(self.saved(page)["bastionUnlocked"])

    def test_new_finale_checkpoint_and_old_archipelago_save(self):
        seed = copy.deepcopy(progression.FIXTURE)
        seed.update(level=5,bestWave=57,bastionUnlocked=True,buildCheckpoint=None)
        seed["g"].update(wave=10,active=False,ended=True,life=5,bonus=False,bossDefeated=True)
        page = self.page({progression.NORMAL:seed},viewport={"width":568,"height":320})
        self.continue_game(page)
        self.assertEqual(page.locator("#board").evaluate("el=>el.width"),780)
        self.assertTrue(self.saved(page)["finaleUnlocked"])
        self.assertIn("Couronne",page.locator(".unlockBastion").inner_text())
        page.locator("#nextMap").tap()
        page.locator("#mapsButton").tap()
        page.locator("#rrImprove").tap()
        for action in ["#metaPlain","#metaBastion","#metaPlay"]:
            self.assert_on_screen(page,action)
        page.locator("#metaPlay").tap()
        start = self.saved(page)
        self.assertEqual((start["level"],start["g"]["layout"],start["g"]["runStart"]),(6,2,6))
        self.assertEqual(start["runHearts"],0)
        self.reload_and_continue(page)
        page.locator("#mapsButton").tap()
        end=self.saved(page)
        self.assertEqual(end["metaLastEarned"]["earned"],0)
        self.assertEqual(end["bestWave"],start["bestWave"])
        self.assertEqual(page.locator(".rrStage.done").count(),0)

    def test_normal_new_run_and_returning_record_use_the_same_profile(self):
        page=self.page(viewport={"width":568,"height":320})
        page.locator("#menuNew").tap()
        page.locator("#metaPlay").tap()
        fresh=self.saved(page)
        self.assertEqual((fresh["level"],fresh["g"]["layout"]),(0,2))
        self.assertFalse(page.locator("#devSkip").is_visible())

        for key,query,width in [(progression.NORMAL,"",600),(PROTOTYPE,"?prototype=1",660)]:
            with self.subTest(query=query):
                seed=copy.deepcopy(progression.FIXTURE)
                seed.update(level=1,bestWave=66,buildCheckpoint=None)
                page=self.page({key:seed},query=query,viewport={"width":568,"height":320})
                self.continue_game(page)
                restored=self.saved(page,key)
                self.assertEqual(page.locator("#board").evaluate("el=>el.width"),width)
                self.assertNotIn("layout",restored["g"])
                for attr in ["stars","bestWave","metaLevels"]:
                    self.assertEqual(restored[attr],seed[attr])
                self.assertTrue(restored["bastionUnlocked"] and restored["finaleUnlocked"])
                page.locator("#mapsButton").tap()
                page.locator("#rrImprove").tap()
                page.locator("#metaPlay").tap()
                start=self.saved(page,key)
                self.assertEqual((start["level"],start["g"]["layout"],start["g"]["runStart"]),(6,2,6))
                self.assertEqual(start["bestWave"],seed["bestWave"])
