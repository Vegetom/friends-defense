"""Validate workshop layout, visual stages and purchase isolation in Chromium."""
import copy
import os
import unittest

import test_browser as progression
import test_l3_browser as l3



class WorkshopBrowserTests(unittest.TestCase):
    setUpClass = classmethod(l3.HeroProgressionBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(l3.HeroProgressionBrowserTests.tearDownClass.__func__)
    setUp = l3.HeroProgressionBrowserTests.setUp
    tearDown = l3.HeroProgressionBrowserTests.tearDown
    page = l3.HeroProgressionBrowserTests.page
    saved = l3.HeroProgressionBrowserTests.saved
    continue_game = l3.HeroProgressionBrowserTests.continue_game
    reload_and_continue = l3.HeroProgressionBrowserTests.reload_and_continue

    def workshop(self, viewport=None, stars=73, ranks=None):
        seed = copy.deepcopy(progression.FIXTURE)
        seed.update(workshopOpen=True, stars=stars, metaLevels=ranks or [0]*5)
        page = self.page({progression.NORMAL: seed}, viewport=viewport)
        self.continue_game(page)
        return page

    def test_arrows_portraits_and_all_twenty_visual_forms(self):
        page = self.workshop({"width": 854, "height": 393})
        page.emulate_media(reduced_motion="reduce")
        page.locator("#metaPrev").tap()
        self.assertEqual(page.locator("#metaHeroName").inner_text(), "POY")
        page.locator("#metaNext").tap()
        self.assertEqual(page.locator("#metaHeroName").inner_text(), "Tom")
        seen = set()
        for i, name in enumerate(["Tom", "Raphaël", "Ylvine", "Jordan", "POY"]):
            page.get_by_role("button", name=name, exact=True).tap()
            self.assertEqual(page.locator("#metaHeroName").inner_text(), name)
            self.assertEqual(page.locator("#metaForm").inner_text(), "Base")
            for n in range(4):
                if n:
                    page.locator("#metaTabs button").nth(n-1).tap()
                canvas = page.locator("#metaSprite")
                self.assertEqual(canvas.get_attribute("data-hero"), str(i))
                self.assertEqual(canvas.get_attribute("data-stage"), str(n))
                data = canvas.evaluate("canvas => canvas.toDataURL()")
                self.assertNotIn(data, seen, f"Duplicate rendering for {name} at {n}")
                seen.add(data)
        self.assertEqual(len(seen),20)

    def test_preview_and_cancel_keep_the_raw_save_then_purchase_reveals_and_persists(self):
        page = self.workshop(stars=5)
        raw = lambda: page.evaluate("key => localStorage.getItem(key)", progression.NORMAL)
        original = raw()
        tabs = page.locator("#metaTabs button")
        tabs.nth(1).tap()
        self.assertTrue(page.locator("#metaBuy").is_disabled())
        self.assertIn("Verrouillé", page.locator("#metaPowerState").text_content())
        self.assertEqual(raw(), original)
        tabs.nth(0).tap()
        self.assertIn("1 tir → 2 tirs", page.locator("#metaPowerEffect").inner_text())
        self.assertEqual(raw(), original)
        page.locator("#metaCancel").tap()
        self.assertEqual(page.locator("#metaSprite").get_attribute("data-stage"), "0")
        self.assertEqual(raw(), original)
        tabs.nth(0).tap()
        page.locator("#metaBuy").tap()
        page.wait_for_function("document.querySelector('#metaSprite').dataset.stage === '1'")
        self.assertEqual(self.saved(page)["metaLevels"], [1,0,0,0,0])
        self.assertEqual(self.saved(page)["stars"], 0)
        self.reload_and_continue(page)
        self.assertEqual(page.locator("#metaForm").inner_text(), "N1")
        tabs.nth(1).tap()
        self.assertIn("Il manque", page.locator("#metaPowerState").text_content())
        self.assertTrue(page.locator("#metaBuy").is_disabled())
        self.assertEqual(self.saved(page)["stars"], 0)

    def test_mobile_controls_fit_without_page_scroll(self):
        for width, height in [(854,393),(667,375),(568,320),(390,844),(320,568)]:
            with self.subTest(width=width,height=height):
                page = self.workshop({"width":width,"height":height})
                page.get_by_role("button", name="Jordan", exact=True).tap()
                page.locator("#metaTabs button").nth(2).tap()
                metrics = page.locator("#metaWorkshop").evaluate("""root => {
                  const ids=['metaHeroName','metaHeroRole','metaForm','metaPowerState','metaPowerName',
                    'metaPowerEffect','metaStars','metaRunStats','metaPlay','metaHard','metaBuy','metaCancel'];
                  const nodes=[...ids.map(id=>document.getElementById(id)), ...root.querySelectorAll('.metaArrow,#metaTabs button,#metaRoster button')];
                  return {
                    size:[innerWidth,innerHeight],page:[document.documentElement.scrollWidth,document.documentElement.scrollHeight],
                    boxes:nodes.map(el=>[el.id,...['left','top','right','bottom','width','height'].map(key=>el.getBoundingClientRect()[key]),el.tagName]),
                    panels:['.metaStage','.metaLoadout'].map(q=>{const p=root.querySelector(q);return [p.clientHeight,p.scrollHeight]})
                  };
                }""")
                self.assertEqual(metrics["size"], [width,height])
                self.assertEqual(metrics["page"], [width,height])
                for element,x,y,right,bottom,w,h,tag in metrics["boxes"]:
                    self.assertTrue(x>=0 and y>=0 and right<=width+.5 and bottom<=height+.5, metrics)
                    if tag=="BUTTON":
                        self.assertGreaterEqual(w,44,element)
                        self.assertGreaterEqual(h,44,element)
                self.assertTrue(all(total<=client+1 for client,total in metrics["panels"]), metrics)
                if os.environ.get("FD_WORKSHOP_SCREENSHOTS"):
                    page.screenshot(path=f"/tmp/fd-workshop/{width}x{height}.png")

    def test_storage_failure_keeps_previous_save_and_exposes_export(self):
        page = self.workshop({"width":568,"height":320})
        old = self.saved(page)
        page.evaluate("""() => {
          const write=Storage.prototype.setItem;
          Storage.prototype.setItem=function(key,value){
            if(key==='friends-defense-save-v38')throw new Error('Synthetic write failure');
            return write.call(this,key,value);
          };
        }""")
        page.locator("#metaTabs button").first.tap()
        page.locator("#metaBuy").tap()
        self.assertEqual(self.saved(page), old)
        self.assertTrue(page.locator("#exportProgress").is_visible())
        self.assertIn("Progression non enregistrée", page.locator("#saveStatusMessage").text_content())
