"""L1 save recovery and session regressions on the real page, with synthetic data."""

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
BACKUP = NORMAL + "-backup"
FIXTURE = json.loads((ROOT / "tests/fixtures/save-v38.json").read_text())


class L1QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class ReliableProgressBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = functools.partial(L1QuietHandler, directory=str(ROOT))
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/index.html"
        cls.playwright = sync_playwright().start()
        executable = os.environ.get("FRIENDS_DEFENSE_CHROMIUM") or shutil.which("chromium")
        try:
            cls.browser = cls.playwright.chromium.launch(
                headless=True, executable_path=executable, args=["--no-sandbox"]
            )
        except Exception:
            cls.playwright.stop()
            cls.server.shutdown()
            cls.server.server_close()
            cls.thread.join()
            raise

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

    def page(self, raw=None, failure="", viewport=None):
        context = self.browser.new_context(
            viewport=viewport or {"width": 390, "height": 844},
            has_touch=True, is_mobile=True, accept_downloads=True,
        )
        self.contexts.append(context)
        # Seed only once, before the fault is installed. Original accessors are kept
        # only in this test context so assertions can inspect data during getItem faults.
        context.add_init_script("""(function(){
          const primary=PRIMARY, raw=RAW, initialFailure=FAILURE;
          const get=Storage.prototype.getItem, set=Storage.prototype.setItem;
          if(!sessionStorage.getItem('fd-l1-seeded')){
            if(raw!==null)set.call(localStorage,primary,raw);
            sessionStorage.setItem('fd-l1-seeded','1');
          }
          window.__l1Failure=initialFailure;
          window.__l1RawGet=key=>get.call(localStorage,key);
          window.__l1BlockedWrites=[];
          Storage.prototype.getItem=function(key){
            if(this===localStorage && key.startsWith(primary)
                && window.__l1Failure==='get')
              throw new DOMException('Injected read failure','SecurityError');
            return get.call(this,key);
          };
          Storage.prototype.setItem=function(key,value){
            if(this===localStorage && key.startsWith(primary)
                && ['quota','write'].includes(window.__l1Failure)){
              window.__l1BlockedWrites.push(key);
              throw new DOMException('Injected write failure',
                window.__l1Failure==='quota'?'QuotaExceededError':'SecurityError');
            }
            return set.call(this,key,value);
          };
        })();""".replace("PRIMARY", json.dumps(NORMAL))
            .replace("RAW", json.dumps(raw))
            .replace("FAILURE", json.dumps(failure)))
        page = context.new_page()
        page.on("pageerror", lambda error: self.errors.append(str(error)))
        page.goto(self.url, wait_until="load")
        return page

    def raw(self, page, key=NORMAL):
        return page.evaluate("key=>window.__l1RawGet(key)", key)

    def saved(self, page):
        return json.loads(self.raw(page))

    def continue_game(self, page):
        page.locator("#menuContinue").click()

    def reload_and_continue(self, page):
        page.reload(wait_until="load")
        self.continue_game(page)

    def assert_permanent_progress(self, save, stars=73):
        self.assertEqual(save["version"], 38)
        self.assertEqual(save["stars"], stars)
        for key in ("metaLevels", "bestWave", "completed"):
            self.assertEqual(save[key], FIXTURE[key])

    def export_raw(self, page):
        with page.expect_download() as download_info:
            page.locator("#exportSave").click()
        return Path(download_info.value.path()).read_bytes()

    def test_absent_save_is_explained_and_can_start_a_new_profile(self):
        page = self.page()
        self.assertTrue(page.locator("#saveStatus").is_visible())
        self.assertEqual(page.locator("#saveStatus").get_attribute("role"), "status")
        self.assertIn("Aucune sauvegarde", page.locator("#saveStatus").inner_text())
        self.assertTrue(page.locator("#menuContinue").is_disabled())
        page.locator("#menuNew").click()
        self.assertTrue(page.locator("#metaWorkshop").is_visible())
        self.assertEqual(self.saved(page)["stars"], 0)
        self.assertEqual(self.saved(page)["version"], 38)

    def test_invalid_and_unknown_saves_are_not_silently_replaced(self):
        unknown = copy.deepcopy(FIXTURE)
        unknown["version"] = 99
        cases = [
            ("json", '{ "version": 38, "texte": "copie ♥"\n', "reprise"),
            ("structure", '{"version":38,"metaLevels":[],"g":{}}', "reprise"),
            ("version", json.dumps(unknown, ensure_ascii=False, indent=1), "version"),
        ]
        for label, raw, expected_word in cases:
            with self.subTest(case=label):
                page = self.page(raw)
                self.assertTrue(page.locator("#menuContinue").is_disabled())
                self.assertTrue(page.locator("#saveStatus").is_visible())
                self.assertIn(expected_word, page.locator("#saveStatus").inner_text())
                self.assertEqual(self.raw(page), raw)
                page.locator("#menuNew").click()
                self.assertTrue(page.locator("#saveRecovery").is_visible())
                self.assertTrue(page.locator("#recoverSave").is_disabled())
                self.assertEqual(self.raw(page), raw)
                page.locator("#recoveryCancel").click()
                self.assertFalse(page.locator("#saveRecovery").is_visible())
                self.assertEqual(self.raw(page), raw)
                page.reload(wait_until="load")
                self.assertEqual(self.raw(page), raw)
                self.assertTrue(page.locator("#menuContinue").is_disabled())

    def test_corrupt_save_exports_verbatim_and_is_backed_up_before_explicit_reset(self):
        raw = ' {"version":38, "texte":"copie non interprétable ♥"\n'
        page = self.page(raw)
        page.locator("#menuNew").click()
        self.assertTrue(page.locator("#recoverSave").is_disabled())
        self.assertEqual(self.export_raw(page), raw.encode("utf-8"))
        self.assertEqual(self.raw(page), raw)
        self.assertTrue(page.locator("#recoverSave").is_disabled())
        page.locator("#backupConfirmed").check()
        confirmations = []

        def accept(dialog):
            confirmations.append(dialog.message)
            dialog.accept()

        page.once("dialog", accept)
        page.locator("#recoverSave").click()
        self.assertTrue(confirmations, "Reset requires an explicit final confirmation")
        self.assertEqual(self.raw(page, BACKUP), raw)
        self.assertNotEqual(self.raw(page), raw)
        self.assertEqual(self.saved(page)["version"], 38)
        self.assertEqual(self.saved(page)["stars"], 0)
        self.assertTrue(page.locator("#metaWorkshop").is_visible())

    def test_reset_confirmation_cancel_keeps_the_original_verbatim(self):
        raw = '{"version":38,"copie":"à garder exactement"\n'
        page = self.page(raw)
        page.locator("#menuNew").click()
        self.assertEqual(self.export_raw(page), raw.encode("utf-8"))
        page.locator("#backupConfirmed").check()
        page.once("dialog", lambda dialog: dialog.dismiss())
        page.locator("#recoverSave").click()
        self.assertEqual(self.raw(page), raw)
        self.assertTrue(page.locator("#menuContinue").is_disabled())

    def test_invalid_attempt_can_recover_valid_v38_permanent_progress(self):
        seed = copy.deepcopy(FIXTURE)
        seed["g"] = {}
        raw = json.dumps(seed, ensure_ascii=False, indent=2)
        page = self.page(raw)
        self.assertTrue(page.locator("#menuContinue").is_disabled())
        page.locator("#menuNew").click()
        self.assertTrue(page.locator("#saveRecovery").is_visible())
        self.assertEqual(self.raw(page), raw)
        self.assertEqual(self.export_raw(page), raw.encode("utf-8"))
        page.locator("#backupConfirmed").check()
        page.once("dialog", lambda dialog: dialog.accept())
        page.locator("#recoverSave").click()
        self.assertEqual(self.raw(page, BACKUP), raw)
        save = self.saved(page)
        self.assert_permanent_progress(save)
        self.assertEqual((save["level"], save["g"]["wave"]), (0, 0))
        self.assertFalse(save["runEnded"])
        self.reload_and_continue(page)
        self.assert_permanent_progress(self.saved(page))

    def test_unknown_version_does_not_guess_permanent_progress_during_reset(self):
        seed = copy.deepcopy(FIXTURE)
        seed["version"] = 99
        raw = json.dumps(seed, ensure_ascii=False, indent=2)
        page = self.page(raw)
        page.locator("#menuNew").click()
        self.assertEqual(self.export_raw(page), raw.encode("utf-8"))
        page.locator("#backupConfirmed").check()
        page.once("dialog", lambda dialog: dialog.accept())
        page.locator("#recoverSave").click()
        self.assertEqual(self.raw(page, BACKUP), raw)
        save = self.saved(page)
        self.assertEqual((save["version"], save["stars"], save["bestWave"]), (38, 0, 0))
        self.assertEqual(save["metaLevels"], [0, 0, 0, 0, 0])
        self.assertFalse(save["completed"])

    def test_backup_failure_refuses_to_replace_corrupt_primary(self):
        raw = '{"version":38,"copie":"quota simulé"\n'
        page = self.page(raw, failure="quota")
        page.locator("#menuNew").click()
        self.assertEqual(self.export_raw(page), raw.encode("utf-8"))
        page.locator("#backupConfirmed").check()
        page.on("dialog", lambda dialog: dialog.accept())
        page.locator("#recoverSave").click()
        self.assertEqual(self.raw(page), raw)
        self.assertIsNone(self.raw(page, BACKUP))
        self.assertTrue(page.locator("#saveRecovery").is_visible())
        self.assertTrue(page.locator("#menuContinue").is_disabled())
        self.assertTrue(page.evaluate("window.__l1BlockedWrites.length>0"))

    def test_unreadable_storage_is_visible_and_does_not_overwrite_primary(self):
        raw = json.dumps(FIXTURE, ensure_ascii=False, indent=2)
        page = self.page(raw, failure="get")
        self.assertTrue(page.locator("#menuContinue").is_disabled())
        self.assertTrue(page.locator("#saveStatus").is_visible())
        self.assertIn("lire", page.locator("#saveStatus").inner_text())
        if page.locator("#menuNew").is_enabled():
            page.locator("#menuNew").click()
        if page.locator("#saveRecovery").is_visible():
            self.assertTrue(page.locator("#exportSave").is_disabled())
            self.assertTrue(page.locator("#recoverSave").is_disabled())
        self.assertEqual(self.raw(page), raw)
        page.reload(wait_until="load")
        self.assertEqual(self.raw(page), raw)
        self.assertTrue(page.locator("#menuContinue").is_disabled())

    def test_write_failures_are_visible_during_play_and_preserve_the_last_save(self):
        raw = json.dumps(FIXTURE, ensure_ascii=False, indent=2)
        for failure in ("quota", "write"):
            with self.subTest(failure=failure):
                page = self.page(raw, failure=failure)
                self.continue_game(page)
                page.locator("#speed").click()  # A real interaction requests a save.
                status = page.locator("#saveStatus")
                self.assertTrue(status.is_visible())
                self.assertIn("non enregistr", status.inner_text())
                self.assertNotIn("QuotaExceededError", status.inner_text())
                self.assertNotIn("SecurityError", status.inner_text())
                self.assertEqual(self.raw(page), raw)
                self.assertTrue(page.evaluate("window.__l1BlockedWrites.length>0"))
                self.assertTrue(page.locator("#exportProgress").is_visible())
                with page.expect_download() as download_info:
                    page.locator("#exportProgress").click()
                memory = json.loads(Path(download_info.value.path()).read_text())
                self.assert_permanent_progress(memory)
                self.assertEqual(memory["speed"], int(page.locator("#speed").inner_text()[1:]))
                self.assertEqual(self.raw(page), raw)

    def test_read_failure_after_loading_allows_export_without_replacing_the_last_save(self):
        page = self.page(json.dumps(FIXTURE, ensure_ascii=False, indent=2))
        self.continue_game(page)
        last_good_raw = self.raw(page)
        page.evaluate("window.__l1Failure='get'")
        page.locator("#speed").click()
        self.assertTrue(page.locator("#saveStatus").is_visible())
        self.assertIn("lire", page.locator("#saveStatus").inner_text())
        self.assertEqual(self.raw(page), last_good_raw)
        self.assertTrue(page.locator("#exportProgress").is_visible())
        with page.expect_download() as download_info:
            page.locator("#exportProgress").click()
        memory = json.loads(Path(download_info.value.path()).read_text())
        self.assert_permanent_progress(memory)
        self.assertEqual(memory["speed"], int(page.locator("#speed").inner_text()[1:]))
        self.assertEqual(self.raw(page), last_good_raw)

    def test_paused_combat_and_each_speed_survive_reload(self):
        for speed in (1, 2, 3):
            with self.subTest(speed=speed):
                seed = copy.deepcopy(FIXTURE)
                seed.update(speed=speed, paused=True)
                seed["g"].update(wave=2, active=True, spawned=0, total=16, clock=999)
                seed["buildCheckpoint"]["wave"] = 1
                page = self.page(json.dumps(seed))
                self.continue_game(page)
                self.assertEqual(page.locator("#pause").get_attribute("aria-pressed"), "true")
                self.assertEqual(page.locator("#speed").inner_text(), f"×{speed}")
                self.assertTrue(self.saved(page)["paused"])
                self.assertEqual(self.saved(page)["speed"], speed)
                self.reload_and_continue(page)
                self.assertEqual(page.locator("#pause").get_attribute("aria-pressed"), "true")
                self.assertEqual(page.locator("#speed").inner_text(), f"×{speed}")
                self.assert_permanent_progress(self.saved(page))

    def test_legacy_save_without_speed_keeps_pause_and_uses_the_default_speed(self):
        seed = copy.deepcopy(FIXTURE)
        seed["paused"] = True
        seed["g"].update(wave=2, active=True, spawned=0, total=16, clock=999)
        seed["buildCheckpoint"]["wave"] = 1
        self.assertNotIn("speed", seed)
        page = self.page(json.dumps(seed))
        self.continue_game(page)
        self.assertEqual(page.locator("#pause").get_attribute("aria-pressed"), "true")
        self.assertEqual(page.locator("#speed").inner_text(), "×1")
        self.reload_and_continue(page)
        self.assert_permanent_progress(self.saved(page))
        self.assertEqual(self.saved(page)["speed"], 1)

    def test_legacy_paid_receipt_and_workshop_reload_without_duplicate_payment(self):
        seed = copy.deepcopy(FIXTURE)
        seed.update(stars=79, runEnded=True, rewardOpen=True, paused=True)
        seed["g"].update(wave=1, active=True, spawned=0, total=14, clock=999)
        seed["buildCheckpoint"]["wave"] = 0
        seed["metaLastEarned"] = {
            "earned": 6, "record": True, "n": 1, "before": 73,
            "after": 79, "win": False,
        }
        page = self.page(json.dumps(seed))
        self.continue_game(page)
        self.assertTrue(page.locator("#runReward").is_visible())
        self.assert_permanent_progress(self.saved(page), stars=79)
        self.reload_and_continue(page)
        self.assertTrue(page.locator("#runReward").is_visible())
        self.assert_permanent_progress(self.saved(page), stars=79)
        page.locator("#rrImprove").click()
        self.assertTrue(page.locator("#metaWorkshop").is_visible())
        self.reload_and_continue(page)
        self.assertTrue(page.locator("#metaWorkshop").is_visible())
        self.assert_permanent_progress(self.saved(page), stars=79)

    def test_new_profile_cancel_is_distinct_from_a_new_attempt(self):
        raw = json.dumps(FIXTURE, ensure_ascii=False, indent=2)
        page = self.page(raw)
        self.assertIn("Nouveau profil", page.locator("#menuNew").inner_text())
        confirmations = []

        def dismiss(dialog):
            confirmations.append(dialog.message.lower())
            dialog.dismiss()

        page.once("dialog", dismiss)
        page.locator("#menuNew").click()
        self.assertTrue(confirmations)
        for consequence in ("étoiles", "pouvoirs", "record", "tentative"):
            self.assertIn(consequence, confirmations[0])
        self.assertEqual(self.raw(page), raw)
        self.continue_game(page)
        self.assertIn("Terminer", page.locator("#reset").get_attribute("aria-label"))
        page.on("dialog", lambda dialog: dialog.accept())
        page.locator("#reset").click()
        self.assertTrue(page.locator("#runReward").is_visible())
        self.assert_permanent_progress(self.saved(page), stars=78)
        page.locator("#rrReplay").click()
        self.assert_permanent_progress(self.saved(page), stars=78)
        self.assertEqual(self.saved(page)["g"]["wave"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
