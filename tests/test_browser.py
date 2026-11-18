"""Regression checks on the real standalone page, in disposable browser contexts."""

import copy
import functools
import http.server
import json
import os
from pathlib import Path
import shutil
import threading
import unittest

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
NORMAL = "friends-defense-save-v38"
DEV = "friends-defense-dev-save-v38"
SETTINGS = "friends-defense-settings-v15"
DEV_SETTINGS = "friends-defense-dev-settings-v15"
FIXTURE = json.loads((ROOT / "tests/fixtures/save-v38.json").read_text())


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class ProgressionBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = functools.partial(QuietHandler, directory=str(ROOT))
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/index.html"
        cls.playwright = sync_playwright().start()
        executable = os.environ.get("FRIENDS_DEFENSE_CHROMIUM") or shutil.which("chromium")
        cls.browser = cls.playwright.chromium.launch(
            headless=True, executable_path=executable, args=["--no-sandbox"]
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.contexts = []
        self.errors = []

    def tearDown(self):
        for context in self.contexts:
            context.close()
        self.assertEqual(self.errors, [], "Unexpected JavaScript error in the game")

    def page(self, saves=None, query="", viewport=None):
        context = self.browser.new_context(
            viewport=viewport or {"width": 390, "height": 844},
            has_touch=True, is_mobile=True
        )
        self.contexts.append(context)
        # Seeding happens once per disposable context. Reloads use the game's own writes.
        context.add_init_script("""(function(){
          const seeds=SEEDS;
          if(!sessionStorage.getItem('fd-test-seeded')){
            for(const [key,value] of Object.entries(seeds))localStorage.setItem(key,JSON.stringify(value));
            sessionStorage.setItem('fd-test-seeded','1');
          }
          window.__storageReads=[];
          const read=Storage.prototype.getItem;
          Storage.prototype.getItem=function(key){
            if(this===localStorage)window.__storageReads.push(key);
            return read.call(this,key);
          };
        })();""".replace("SEEDS", json.dumps(saves or {})))
        page = context.new_page()
        page.on("pageerror", lambda error: self.errors.append(str(error)))
        page.on("dialog", lambda dialog: dialog.accept())
        page.goto(self.base + query, wait_until="load")
        return page

    def saved(self, page, key=NORMAL):
        return page.evaluate("key => JSON.parse(localStorage.getItem(key))", key)

    def continue_game(self, page):
        page.locator("#menuContinue").click()

    def new_game(self, page):
        page.locator("#menuNew").click()
        page.locator("#metaPlay").click()

    def reload_and_continue(self, page):
        page.reload(wait_until="load")
        self.continue_game(page)

    def test_active_first_wave_abandons_never_award_stars_or_records(self):
        page = self.page()
        self.new_game(page)
        # First, abandoning before any wave starts is also worth zero.
        page.locator("#mapsButton").click()
        self.assertEqual(self.saved(page)["stars"], 0)
        page.locator("#rrReplay").click()
        for _ in range(2):
            page.locator("#start").click()
            page.locator("#mapsButton").click()
            save = self.saved(page)
            self.assertEqual((save["stars"], save["bestWave"]), (0, 0))
            self.assertIn("0/10", page.locator("#rrSubtitle").inner_text())
            self.assertIn("0/10", page.locator(".rrStage.current .rrStageWave").inner_text())
            self.assertEqual(page.locator(".rrStage.done").count(), 0)
            self.assertIn("+0", page.locator(".rrFooterHint").inner_text())
            # A second programmatic finish attempt must not issue another receipt.
            page.locator("#mapsButton").evaluate("element => element.onclick()")
            self.assertEqual(self.saved(page)["stars"], 0)
            page.locator("#rrReplay").click()

    def test_v38_progression_survives_rewards_and_reload_at_reward_and_workshop(self):
        page = self.page({NORMAL: FIXTURE})
        self.continue_game(page)
        loaded = self.saved(page)
        for key in ("stars", "bestWave", "completed", "metaLevels"):
            self.assertEqual(loaded[key], FIXTURE[key])
        page.locator("#mapsButton").click()
        awarded = self.saved(page)
        self.assertEqual(awarded["stars"], 78)  # Historical non-record reward: +5.
        self.assertEqual(awarded["bestWave"], 48)
        self.assertEqual(awarded["metaLevels"], FIXTURE["metaLevels"])
        self.assertTrue(awarded["completed"])
        self.assertIn("2/10", page.locator("#rrSubtitle").inner_text())
        self.assertEqual(page.locator(".rrStage.done").count(), 0)
        self.reload_and_continue(page)
        self.assertTrue(page.locator("#runReward").is_visible())
        self.assertEqual(self.saved(page)["stars"], 78)
        page.locator("#rrImprove").click()
        self.assertTrue(page.locator("#metaWorkshop").is_visible())
        self.reload_and_continue(page)
        self.assertTrue(page.locator("#metaWorkshop").is_visible())
        self.assertEqual(self.saved(page)["stars"], 78)

    def test_reload_mid_wave_does_not_count_the_active_wave(self):
        seed = copy.deepcopy(FIXTURE)
        seed["g"].update(wave=2, active=True, spawned=0, total=16, clock=999)
        page = self.page({NORMAL: seed})
        self.continue_game(page)
        self.reload_and_continue(page)
        self.assertEqual(self.saved(page)["stars"], 73)
        page.locator("#mapsButton").click()
        save = self.saved(page)
        self.assertEqual(save["metaLastEarned"]["n"], 1)
        self.assertEqual(save["stars"], 78)
        self.assertIn("1/10", page.locator("#rrSubtitle").inner_text())
        self.assertIn("1/10", page.locator(".rrStage.current .rrStageWave").inner_text())

    def test_legacy_finished_receipt_is_not_awarded_again(self):
        seed = copy.deepcopy(FIXTURE)
        seed.update(stars=79, runEnded=True, rewardOpen=True, paused=True)
        seed["g"].update(wave=1, active=True, spawned=0, total=14, clock=999)
        seed["buildCheckpoint"]["wave"] = 0
        # This historical receipt credited an active wave. Preserve the acquired balance.
        seed["metaLastEarned"] = {
            "earned": 6, "record": True, "n": 1, "before": 73,
            "after": 79, "win": False
        }
        page = self.page({NORMAL: seed})
        self.continue_game(page)
        self.assertEqual(self.saved(page)["stars"], 79)
        self.reload_and_continue(page)
        save = self.saved(page)
        self.assertEqual(save["stars"], 79)
        self.assertEqual(save["bestWave"], 48)
        self.assertEqual(save["metaLevels"], FIXTURE["metaLevels"])
        self.assertTrue(save["completed"])

    def test_unpaid_legacy_defeat_is_finalized_once_without_reducing_old_progress(self):
        seed = copy.deepcopy(FIXTURE)
        seed.update(runEnded=False, rewardOpen=False)
        seed["g"].update(wave=2, active=False, ended=True, life=0, retries=0)
        seed["buildCheckpoint"]["retries"] = 0
        page = self.page({NORMAL: seed})
        self.continue_game(page)
        save = self.saved(page)
        self.assertEqual(save["stars"], 78)
        self.assertEqual(save["bestWave"], 48)
        self.assertEqual(save["metaLastEarned"]["n"], 1)
        self.assertTrue(save["runEnded"])
        self.assertTrue(save["paused"])
        self.reload_and_continue(page)
        self.assertEqual(self.saved(page)["stars"], 78)

    def test_legacy_closed_finished_screens_reopen_without_awarding_or_resetting(self):
        for receipt in (None, {"earned": 6, "n": 1, "before": 73,
                              "after": 79, "record": True, "win": False}):
            with self.subTest(receipt=receipt is not None):
                seed = copy.deepcopy(FIXTURE)
                seed.update(runEnded=True, rewardOpen=False, workshopOpen=False,
                            paused=False, stars=79, metaLastEarned=receipt)
                page = self.page({NORMAL: seed})
                self.continue_game(page)
                expected = "#runReward" if receipt else "#metaWorkshop"
                self.assertTrue(page.locator(expected).is_visible())
                save = self.saved(page)
                self.assertTrue(save["paused"])
                self.assertEqual(save["stars"], 79)
                self.assertEqual(save["metaLevels"], FIXTURE["metaLevels"])
                self.assertEqual(save["bestWave"], 48)
                self.assertTrue(save["completed"])
                self.reload_and_continue(page)
                self.assertTrue(page.locator(expected).is_visible())
                self.assertEqual(self.saved(page)["stars"], 79)

    def test_intermediate_map_victory_does_not_pay_stars_before_the_attempt_ends(self):
        seed = copy.deepcopy(FIXTURE)
        seed["g"].update(wave=10, active=False, ended=True, life=15)
        page = self.page({NORMAL: seed})
        self.continue_game(page)
        self.assertTrue(page.locator("#nextMap").is_visible())
        self.assertFalse(page.locator("#runReward").is_visible())
        self.assertEqual(self.saved(page)["stars"], 73)
        page.locator("#nextMap").click()
        self.assertEqual(self.saved(page)["level"], 1)
        self.assertEqual(self.saved(page)["stars"], 73)
        page.locator("#mapsButton").click()
        self.assertEqual(self.saved(page)["metaLastEarned"]["n"], 10)
        self.assertEqual(self.saved(page)["stars"], 80)  # Existing record: +7 at level 1.
        self.assertEqual(page.locator(".rrStage.done").count(), 1)

    def test_carried_hearts_survive_transition_reload_and_two_checkpoint_retries(self):
        seed = copy.deepcopy(FIXTURE)
        seed.update(runHearts=2, runEnded=False)
        seed["g"].update(wave=10, active=False, ended=True, life=15, retries=2)
        page = self.page({NORMAL: seed})
        self.continue_game(page)
        page.locator("#nextMap").click()
        self.reload_and_continue(page)
        carried = self.saved(page)
        self.assertEqual(carried["level"], 1)
        self.assertEqual(carried["g"]["retries"], 2)
        self.assertEqual(carried["buildCheckpoint"]["retries"], 2)
        checkpoint_money = carried["buildCheckpoint"]["money"]
        for remaining in (1, 0):
            loss = copy.deepcopy(carried)
            loss["g"].update(wave=1, active=False, ended=True, life=0,
                             total=14, spawned=14, money=checkpoint_money-35+10)
            loss["g"]["towers"]["31"] = {
                "type": 0, "lvl": 1, "invested": 35, "cd": 0, "fresh": False
            }
            failed_page = self.page({NORMAL: loss})
            self.continue_game(failed_page)
            self.assertTrue(failed_page.locator("#retryWave").is_visible())
            failed_page.locator("#retryWave").click()
            carried = self.saved(failed_page)
            self.assertEqual(carried["g"]["retries"], remaining)
            self.assertEqual(carried["buildCheckpoint"]["retries"], remaining)
            self.assertEqual(carried["g"]["money"], checkpoint_money)
            self.assertEqual(carried["g"]["towers"], {})
            self.assertEqual(carried["stars"], 73)
            self.assertEqual(carried["bestWave"], 48)

    def test_campaign_victory_rewards_once_and_marks_only_completed_maps(self):
        seed = copy.deepcopy(FIXTURE)
        seed.update(level=6, stars=0, bestWave=0, completed=False, runEnded=False)
        seed["g"].update(wave=10, active=False, ended=True, life=15)
        page = self.page({NORMAL: seed})
        self.continue_game(page)
        save = self.saved(page)
        self.assertEqual((save["stars"], save["bestWave"]), (36, 70))
        self.assertTrue(save["completed"])
        self.assertEqual(page.locator(".rrStage.done").count(), 7)
        self.reload_and_continue(page)
        self.assertEqual(self.saved(page)["stars"], 36)

    def test_normal_dev_handler_is_hidden_and_guarded_even_programmatically(self):
        for query in ("", "?dev=0", "?dev=true", "?dev=01"):
            with self.subTest(query=query):
                page = self.page({NORMAL: FIXTURE}, query=query)
                self.continue_game(page)
                self.assertFalse(page.locator("#devSkip").is_visible())
                before = self.saved(page)
                page.locator("#devSkip").evaluate("element => element.click()")
                after = self.saved(page)
                for key in ("g", "stars", "bestWave", "completed", "metaLevels"):
                    self.assertEqual(after[key], before[key])
                page.context.close()
                self.contexts.remove(page.context)

    def test_explicit_test_profile_never_reads_or_overwrites_normal_profile(self):
        normal_settings = {"sound": False, "damage": False, "effects": False}
        page = self.page({NORMAL: FIXTURE, SETTINGS: normal_settings}, query="?dev=1")
        self.assertIn("MODE TEST", page.locator(".menuButtons").inner_text())
        self.assertFalse(page.locator("#menuContinue").is_enabled())
        self.assertIn("TEST", page.locator("#menuNew").get_attribute("aria-label"))
        self.new_game(page)
        self.assertTrue(page.locator("#devSkip").is_visible())
        self.assertTrue(page.locator("#soundToggle").is_checked())
        page.locator("#settingsButton").click()
        page.locator("#soundToggle").uncheck()
        page.locator("#settingsClose").click()
        page.locator("#devSkip").click()
        self.assertEqual(self.saved(page, DEV)["g"]["wave"], 10)
        for _ in range(6):
            page.locator("#nextMap").click()
            page.locator("#devSkip").click()
        test_save = self.saved(page, DEV)
        self.assertEqual((test_save["stars"], test_save["bestWave"]), (36, 70))
        self.assertTrue(test_save["completed"])
        reads_before_reload = page.evaluate("window.__storageReads")
        self.reload_and_continue(page)
        self.assertEqual(self.saved(page, DEV)["stars"], 36)
        reads = reads_before_reload + page.evaluate("window.__storageReads")
        self.assertNotIn(NORMAL, reads)
        self.assertNotIn(SETTINGS, reads)
        self.assertEqual(self.saved(page, NORMAL), FIXTURE)
        self.assertEqual(self.saved(page, SETTINGS), normal_settings)
        self.assertFalse(self.saved(page, DEV_SETTINGS)["sound"])
        # Return to normal in the same context: restore normal progress, never dev progress.
        page.goto(self.base, wait_until="load")
        self.continue_game(page)
        self.assertFalse(page.locator("#devSkip").is_visible())
        normal = self.saved(page)
        self.assertEqual(normal["g"]["wave"], 2)
        for key in ("stars", "bestWave", "metaLevels", "completed"):
            self.assertEqual(normal[key], FIXTURE[key])


if __name__ == "__main__":
    unittest.main(verbosity=2)
