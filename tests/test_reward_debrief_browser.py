"""Verify reward detail, retry guidance and responsive controls in Chromium."""
import copy
import unittest

import test_browser as progression


class RewardDebriefBrowserTests(unittest.TestCase):
    setUpClass = classmethod(progression.ProgressionBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(progression.ProgressionBrowserTests.tearDownClass.__func__)
    setUp = progression.ProgressionBrowserTests.setUp
    tearDown = progression.ProgressionBrowserTests.tearDown
    page = progression.ProgressionBrowserTests.page
    saved = progression.ProgressionBrowserTests.saved
    continue_game = progression.ProgressionBrowserTests.continue_game
    reload_and_continue = progression.ProgressionBrowserTests.reload_and_continue

    def defeat(self, viewport, *, retry=False):
        seed=copy.deepcopy(progression.FIXTURE)
        seed["g"].update(wave=7,life=0,ended=True,active=False,bonus=False,
            escaped=9,waveLeaks={"air":8,"ground":1,"boss":0},doctrine="escadron")
        if retry:
            seed["buildCheckpoint"].update(wave=6,doctrine="escadron")
        else:
            seed["buildCheckpoint"]=None
        page=self.page({progression.NORMAL:seed},viewport=viewport)
        self.continue_game(page)
        return page

    def test_debrief_and_primes_fit_and_survive_reload(self):
        for width,height in [(854,393),(568,320),(320,568)]:
            with self.subTest(width=width,height=height):
                page=self.defeat({"width":width,"height":height})
                self.assertIn("8 volants",page.locator("#rrDebrief").inner_text())
                self.assertIn("couloir aérien",page.locator("#rrDebrief").inner_text())
                self.assertIn("premier boss +2",page.locator(".rrFooterHint").inner_text())
                self.assertEqual(self.saved(page)["stars"],82)
                boxes=page.locator("#runReward").evaluate("""el => ['#rrDebrief','#rrImprove','#rrReplay'].map(q=>{
                    const rect=el.querySelector(q).getBoundingClientRect();
                    return [rect.top,rect.bottom,rect.left,rect.right];
                })""")
                for top,bottom,left,right in boxes:
                    self.assertTrue(top>=0 and bottom<=height and left>=0 and right<=width,boxes)
                self.reload_and_continue(page)
                self.assertIn("8 volants",page.locator("#rrDebrief").inner_text())
                self.assertEqual(self.saved(page)["stars"],82)

    def test_retry_advice_is_visible_before_spending_a_heart(self):
        page=self.defeat({"width":854,"height":393},retry=True)
        self.assertTrue(page.locator("#retryWave").is_visible())
        self.assertIn("8 volants",page.locator("#result .resultHint").inner_text())
        self.assertEqual(self.saved(page)["stars"],73)
        page.locator("#retryWave").tap()
        self.assertFalse(page.locator("#rrDebrief").is_visible())
        self.assertNotIn("waveLeaks",self.saved(page)["g"])
