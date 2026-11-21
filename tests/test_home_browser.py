"""Title animation and chiptune using the real page in Chromium."""
import unittest

import test_browser as progression


class HomeBrowserTests(unittest.TestCase):
    setUpClass = classmethod(progression.ProgressionBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(progression.ProgressionBrowserTests.tearDownClass.__func__)
    setUp = progression.ProgressionBrowserTests.setUp
    tearDown = progression.ProgressionBrowserTests.tearDown
    page = progression.ProgressionBrowserTests.page

    def test_art_moves_but_respects_reduced_motion_and_keeps_touch_targets(self):
        for width,height in [(320,568),(390,844),(568,320),(844,390)]:
            with self.subTest(width=width,height=height):
                page=self.page(viewport={"width":width,"height":height})
                motion=page.locator(".menuAura")
                self.assertEqual(motion.evaluate("el=>getComputedStyle(el).animationName"),"fdTitleAura")
                self.assertIn("data:image/jpeg",page.locator(".menuHomeArt").evaluate(
                    "el=>getComputedStyle(el).backgroundImage.slice(0,40)"))
                for ident in ["#menuNew","#menuContinue","#menuMusic"]:
                    box=page.locator(ident).bounding_box()
                    self.assertGreaterEqual(box["height"],44)
                    self.assertGreaterEqual(box["x"],0)
                    self.assertGreaterEqual(box["y"],0)
                    self.assertLessEqual(box["x"]+box["width"],width)
                    self.assertLessEqual(box["y"]+box["height"],height)
                if width>height:
                    art=page.locator(".menuHomeArt").bounding_box()
                    frame=page.locator(".menuMotion").bounding_box()
                    self.assertAlmostEqual(frame["x"],art["x"]+(art["width"]-frame["width"])*.14,delta=.5)
                page.emulate_media(reduced_motion="reduce")
                self.assertEqual(motion.evaluate("el=>getComputedStyle(el).animationName"),"none")

    def test_music_is_opt_in_loops_and_stops_away_from_home(self):
        page=self.page({progression.SETTINGS:{"sound":False}},viewport={"width":568,"height":320})
        page.evaluate("""()=>{
          window.musicStarts=[];
          window.musicStops=0;
          const proto=AudioBufferSourceNode.prototype, start=proto.start, stop=proto.stop;
          proto.start=function(...args){
            if(this.loop){
              const channel=this.buffer.getChannelData(0);
              window.musicStarts.push({duration:this.buffer.duration,peak:channel.reduce((v,x)=>Math.max(v,Math.abs(x)),0)});
            }
            return start.apply(this,args);
          };
          proto.stop=function(...args){
            if(this.loop)window.musicStops++;
            return stop.apply(this,args);
          };
        }""")
        button=page.get_by_role("button",name="Musique de l’accueil")
        self.assertEqual(button.get_attribute("aria-pressed"),"false")
        self.assertEqual(page.evaluate("musicStarts.length"),0)
        button.tap()
        page.wait_for_function("document.querySelector('#menuMusic').getAttribute('aria-pressed')==='true'")
        music=page.evaluate("musicStarts")
        self.assertEqual(len(music),1)
        self.assertAlmostEqual(music[0]["duration"],13.33,places=2)
        self.assertGreater(music[0]["peak"],.15)
        self.assertLess(music[0]["peak"],.6)
        self.assertEqual(page.evaluate("key=>JSON.parse(localStorage.getItem(key))",
            progression.SETTINGS),{"sound":False,"music":True,"damage":True,"effects":True})
        button.tap()
        self.assertEqual(button.get_attribute("aria-pressed"),"false")
        self.assertEqual(page.evaluate("musicStops"),1)
        button.tap()
        page.wait_for_function("musicStarts.length===2")
        page.evaluate("""()=>{
          Object.defineProperty(document,'hidden',{configurable:true,value:true});
          document.dispatchEvent(new Event('visibilitychange'));
        }""")
        self.assertEqual(page.evaluate("musicStops"),2)
        self.assertEqual(page.locator(".menuAura").evaluate(
            "el=>getComputedStyle(el).animationPlayState"),"paused")
        page.evaluate("""()=>{
          Object.defineProperty(document,'hidden',{configurable:true,value:false});
          document.dispatchEvent(new Event('visibilitychange'));
        }""")
        page.wait_for_function("musicStarts.length===3")
        page.locator("#menuNew").tap()
        self.assertEqual(page.evaluate("musicStops"),3)
        self.assertFalse(button.is_visible())
        self.assertTrue(page.locator("#metaWorkshop").is_visible())
        page.reload(wait_until="load")
        self.assertEqual(button.get_attribute("aria-pressed"),"false")
        self.assertTrue(page.evaluate("key=>JSON.parse(localStorage.getItem(key)).music",
            progression.SETTINGS))
        button.tap()
        page.wait_for_function("document.querySelector('#menuMusic').getAttribute('aria-pressed')==='true'")
