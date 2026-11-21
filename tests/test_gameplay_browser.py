"""Gameplay regression on the real page; reuse helpers without inheriting their tests."""
import copy
import json
from pathlib import Path
import subprocess
import unittest

import test_browser as progression


class GameplayBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        built = subprocess.run(["node", "-e", """
          const {createModel}=require('./tests/model.cjs');
          const fixture=require('./tests/fixtures/save-v38.json');
          const model=createModel();model.set();model.startLevel(3);
          if(!model.buy(11,0)||!model.begin())throw Error('Legal preparation failed');
          model.spawn();model.setGame({clock:999});const state=model.state();
          console.log(JSON.stringify({...fixture,level:3,metaLevels:[0,0,0,0,0],
            runHearts:0,runEnded:false,completed:false,rewardOpen:false,metaLastEarned:null,
            workshopOpen:false,paused:false,speed:1,g:state.g,buildCheckpoint:state.buildCheckpoint}));
        """], cwd=progression.ROOT, text=True, capture_output=True, check=True)
        cls.active = json.loads(built.stdout)
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

    def test_absorbed_feedback_and_trait_explanation_come_from_a_real_blocked_attack(self):
        page = self.page({progression.NORMAL: self.active})
        page.evaluate("""() => {
          window.__combatText=[];
          const fill=CanvasRenderingContext2D.prototype.fillText;
          CanvasRenderingContext2D.prototype.fillText=function(text,...args){
            if(text==='Absorbé')window.__combatText.push(text);
            return fill.call(this,text,...args);
          };
        }""")
        original_hp = self.active["g"]["enemies"][0]["hp"]
        self.continue_game(page)
        page.wait_for_function("window.__combatText.length>0")
        page.locator("#pause").click()
        saved = self.saved(page)
        self.assertEqual(saved["g"]["enemies"][0]["hp"], original_hp)
        self.assertIn("90/impact", page.locator("#route").inner_text())
        page.locator("#settingsButton").click()
        details = page.locator("#economyInfo").inner_text()
        self.assertIn("marquage −60 %", details)
        self.assertIn("gel −20 %", details)
        self.assertIn("pas les boucliers", details)

    def test_tower_can_evolve_even_when_it_is_the_only_visible_action(self):
        for wave, fresh, budget in [(0, True, 150), (1, False, 150), (1, False, 49)]:
            with self.subTest(wave=wave, budget=budget):
                seed = copy.deepcopy(progression.FIXTURE)
                seed["buildCheckpoint"] = None
                seed["g"].update(wave=wave, money=budget, towers={
                    "31": {"type": 0, "lvl": 1, "fresh": fresh, "invested": 35, "cd": 0}
                })
                page = self.page({progression.NORMAL: seed}, viewport={"width": 844, "height": 390})
                self.continue_game(page)
                board = page.locator("#board").bounding_box()
                page.touchscreen.tap(board["x"] + board["width"] * .15,
                                     board["y"] + board["height"] * 3.5 / 8)
                evolve = page.locator("#upgrade")
                self.assertTrue(evolve.is_visible())
                self.assertEqual(page.locator("#remove").is_visible(), fresh)
                self.assertFalse(page.locator("#relocate").is_visible())
                if budget < 50:
                    self.assertTrue(evolve.is_disabled())
                    continue
                evolve.tap()
                state = self.saved(page)["g"]
                self.assertEqual((state["towers"]["31"]["lvl"], state["money"]), (2, 100))
                if fresh:
                    continue
                evolve.tap()
                state = self.saved(page)["g"]
                self.assertEqual((state["towers"]["31"]["lvl"], state["money"]), (3, 30))
                self.assertTrue(page.locator("#panel").is_visible())
                self.assertFalse(page.locator("#panel .acts").is_visible())
                page.locator("#start").tap()
                page.locator("#pause").tap()
                self.assertFalse(page.locator("#panel").is_visible())

    def test_legacy_and_new_enemy_snapshots_survive_a_paused_reload(self):
        old = json.loads((Path(progression.ROOT) / "tests/fixtures/save-v38-air-boss.json").read_text())
        for seed in (old, self.active):
            with self.subTest(legacy=seed is old):
                seed = copy.deepcopy(seed)
                seed["paused"] = True
                original = copy.deepcopy(seed["g"]["enemies"])
                page = self.page({progression.NORMAL: seed})
                self.continue_game(page)
                self.reload_and_continue(page)
                saved = self.saved(page)
                self.assertEqual(saved["g"]["enemies"], original)
                self.assertEqual(saved["stars"], seed["stars"])
                self.assertEqual(saved["metaLevels"], seed["metaLevels"])

    def test_gate_is_announced_before_map_four_and_inside_the_workshop(self):
        seed = copy.deepcopy(progression.FIXTURE)
        seed["level"] = 2
        seed["buildCheckpoint"] = None
        seed["g"].update(wave=10, active=False, ended=True, life=15)
        page = self.page({progression.NORMAL: seed})
        self.continue_game(page)
        warning = page.locator("#nextStageWarning").inner_text()
        self.assertIn("90/impact", warning)
        self.assertIn("pouvoirs permanents adaptés sont nécessaires", warning)
        page.locator("#mapsButton").click()
        page.locator("#rrImprove").click()
        workshop = page.locator("#metaWorkshop").inner_text()
        self.assertIn("90/impact", workshop)
        self.assertIn("Marquage de Raphaël I", workshop)
        self.assertIn("ne suffit pas seul", workshop)


if __name__ == "__main__":
    unittest.main(verbosity=2)
