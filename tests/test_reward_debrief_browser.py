"""Verify the animated combat recap, rewards and checkpoints in Chromium."""
import copy
import re
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

    def ended_seed(self, *, victory=False, report=True):
        seed = copy.deepcopy(progression.FIXTURE)
        seed["g"].update(wave=10 if victory else 7, life=11 if victory else 0,
                         ended=True, active=False, bonus=False,
                         escaped=9, waveLeaks={"air":8,"ground":1,"boss":0},
                         doctrine="escadron")
        if report:
            seed["g"]["combatReport"] = {"damage":[150,5000,0,80,0],
                "forms":[1,3,0,2,0],"slowed":31,"partial":False}
        return seed

    def assert_visible_bounds(self, page, width, height, selectors):
        boxes = page.evaluate("""selectors => selectors.flatMap(selector =>
          [...document.querySelectorAll(selector)].map(el => {
            const r=el.getBoundingClientRect();
            return [selector,r.top,r.bottom,r.left,r.right];
          }))""", selectors)
        for selector, top, bottom, left, right in boxes:
            self.assertTrue(top>=0 and bottom<=height and left>=0 and right<=width,
                            (width,height,selector,boxes))

    def test_defeat_report_and_primes_fit_and_survive_reload(self):
        for width,height in [(844,390),(568,320),(320,568),(390,844)]:
            with self.subTest(width=width,height=height):
                seed = self.ended_seed()
                seed["buildCheckpoint"] = None
                page = self.page({progression.NORMAL:seed},viewport={"width":width,"height":height})
                self.continue_game(page)
                recap = page.locator("#rrCombatReport")
                cards = recap.locator(".combatCard")
                self.assertEqual(cards.locator(".combatCardName").all_text_contents(),
                                 ["Tom","Raphaël","Ylvine","Jordan","POY"])
                self.assertEqual(recap.locator(".topDamage .combatCardName").inner_text(),"Raphaël")
                self.assertEqual(recap.locator(".combatStatus").all_text_contents(),
                                 ["Non déployé","Non déployé"])
                self.assertIn("31 ralentis",recap.inner_text())
                self.assertEqual(cards.nth(1).locator(".combatShare span").inner_text(),"96 %")
                self.assertNotIn("couloir aérien",page.locator("#runReward").inner_text())
                self.assertIn("premier boss +2",page.locator(".rrFooterHint").inner_text())
                self.assertEqual(self.saved(page)["stars"],82)
                self.assert_visible_bounds(page,width,height,["#rrCombatReport","#rrImprove","#rrReplay"])
                page.wait_for_function("""() => [...document.querySelectorAll('#rrCombatReport canvas')]
                  .every(c => c.getContext('2d').getImageData(0,0,128,128).data.some((v,i)=>i%4===3&&v>0))""")
                recap.tap()
                self.assertRegex(cards.nth(1).locator(".combatValue").inner_text(),r"5\s?000")
                self.reload_and_continue(page)
                self.assertRegex(cards.nth(1).locator(".combatValue").inner_text(),r"5\s?000")
                self.assertEqual(self.saved(page)["stars"],82)

    def test_retry_rolls_back_only_the_failed_wave_and_old_report_can_be_absent(self):
        seed = self.ended_seed()
        before = {"damage":[120,3400,0,50,0],"forms":[1,2,0,1,0],"slowed":21,"partial":False}
        seed["buildCheckpoint"].update(wave=6,doctrine="escadron",combatReport=before)
        page = self.page({progression.NORMAL:seed},viewport={"width":568,"height":320})
        self.continue_game(page)
        self.assertTrue(page.locator("#retryWave").is_visible())
        self.assertIn("31 ralentis",page.locator("#result .combatReport").inner_text())
        self.assertEqual(page.locator("#result .resultHint").count(),0)
        self.assertEqual(self.saved(page)["stars"],73)
        self.assert_visible_bounds(page,568,320,["#result .combatReport","#retryWave","#endAttempt"])
        page.locator("#retryWave").tap()
        self.assertFalse(page.locator("#result .combatReport").is_visible())
        self.assertNotIn("waveLeaks",self.saved(page)["g"])
        self.assertEqual(self.saved(page)["g"]["combatReport"],before)
        self.reload_and_continue(page)
        self.assertEqual(self.saved(page)["g"]["combatReport"],before)
        legacy = self.ended_seed(report=False)
        legacy["buildCheckpoint"] = None
        page = self.page({progression.NORMAL:legacy})
        self.continue_game(page)
        self.assertIn("Dégâts indisponibles",page.locator("#rrCombatReport").inner_text())
        self.assertEqual(page.locator(".combatCard").count(),0)

    def test_victory_animates_and_next_terrain_starts_with_empty_totals(self):
        seed = self.ended_seed(victory=True)
        page = self.page({progression.NORMAL:seed},viewport={"width":568,"height":320})
        page.evaluate("""() => {
          window.recapFrames=[];
          new MutationObserver(() => {
            const value=document.querySelector('#result .topDamage .combatValue');
            if(value) window.recapFrames.push(value.textContent.replace(/\\s/g,''));
          }).observe(document.body,{childList:true,subtree:true});
        }""")
        self.continue_game(page)
        self.assert_visible_bounds(page,568,320,["#result .combatReport","#nextMap"])
        page.wait_for_function("() => window.recapFrames.includes('5000')")
        frames = page.evaluate("window.recapFrames")
        self.assertTrue(any(re.fullmatch(r"\d+",v) and 0 < int(v) < 5000 for v in frames),frames)
        page.locator("#nextMap").tap()
        save = self.saved(page)
        self.assertEqual(save["level"],1)
        self.assertEqual(save["g"]["combatReport"]["damage"],[0,0,0,0,0])

    def test_reduced_motion_shows_the_final_totals_immediately(self):
        seed = self.ended_seed(victory=True)
        page = self.page({progression.NORMAL:seed},viewport={"width":844,"height":390})
        page.emulate_media(reduced_motion="reduce")
        self.continue_game(page)
        card = page.locator("#result .topDamage")
        self.assertRegex(card.locator(".combatValue").inner_text(),r"5\s?000")
        self.assertAlmostEqual(card.locator(".combatTrack i").evaluate(
            "el => new DOMMatrix(getComputedStyle(el).transform).a"),5000/5230,places=5)
