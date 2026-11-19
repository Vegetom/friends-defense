"""Render controlled v38 combat scenes through the actual game canvas."""
import copy
import os
import unittest

import test_browser as progression


class EnemyArtBrowserTests(unittest.TestCase):
    setUpClass = classmethod(progression.ProgressionBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(progression.ProgressionBrowserTests.tearDownClass.__func__)
    setUp = progression.ProgressionBrowserTests.setUp
    tearDown = progression.ProgressionBrowserTests.tearDown
    page = progression.ProgressionBrowserTests.page
    saved = progression.ProgressionBrowserTests.saved
    continue_game = progression.ProgressionBrowserTests.continue_game

    def scene(self, level, wave, *, crowded=False):
        seed = copy.deepcopy(progression.FIXTURE)
        seed.update(level=level, paused=True, buildCheckpoint=None, workshopOpen=False)
        enemies = []
        for i in range(30 if crowded else 5):
            role = i % 5
            x, y = 76 + (i % (6 if crowded else 3))*68, 115 + (i // (6 if crowded else 3))*63
            enemies.append(dict(x=x,y=y,k=0,progress=(i%9)*.055 if role==3 else i*.21,hp=600,max=750,vel=75,reward=4,
                fast=role==1,tank=role==2,air=role==3,boss=role==4,elite=role==1,
                shield=120 if role in (2,3) else 0,maxShield=240 if role in (2,3) else 0,
                slow=1 if role==0 else 0,slowPower=.3,mark=1 if role==1 else 0,
                regen=.005 if role==2 else 0))
        seed["g"].update(wave=wave,active=True,ended=False,total=40,spawned=len(enemies),clock=1,
                         towers={},enemies=enemies)
        return seed

    def watch_atlas(self, page):
        page.evaluate("""() => {
          window.enemyFrames = [];
          const draw = CanvasRenderingContext2D.prototype.drawImage;
          CanvasRenderingContext2D.prototype.drawImage = function(image,...args) {
            if(this.canvas.id==='board' && image.naturalWidth===192 && image.naturalHeight===2016){
              window.enemyFrames.push(args.slice(0,4));
              if(window.enemyFrames.length>1000)window.enemyFrames.shift();
            }
            return draw.call(this,image,...args);
          };
        }""")

    def test_factions_and_boss_waves_render_from_distinct_atlas_rows(self):
        for level in range(7):
            for wave in ([5,10] if level==6 else [5]):
                with self.subTest(level=level,wave=wave):
                    seed=self.scene(level,wave)
                    page=self.page({progression.NORMAL:seed},viewport={"width":854,"height":393})
                    self.watch_atlas(page)
                    self.continue_game(page)
                    page.wait_for_function("window.enemyFrames.length >= 5")
                    rows=page.evaluate("() => [...new Set(window.enemyFrames.map(f=>f[1]/48))]")
                    offset=level*6
                    self.assertEqual(set(rows),{offset+i for i in (0,1,2,3,5 if wave==10 else 4)})
                    if os.environ.get("FD_ENEMY_SCREENSHOTS") and (level,wave) in ((0,5),(3,5),(6,10)):
                        page.locator("#board").screenshot(path=f"/tmp/fd-enemy/stage-{level+1}-wave-{wave}.png")

    def test_crowded_wave_loads_and_animation_follows_pause(self):
        seed=self.scene(6,10,crowded=True)
        page=self.page({progression.NORMAL:seed},viewport={"width":667,"height":375})
        self.watch_atlas(page)
        self.continue_game(page)
        page.wait_for_function("window.enemyFrames.length >= 60")
        self.assertEqual(self.saved(page)["g"]["enemies"][0]["hp"],600)
        # Same duplicated art per role is drawn at the same pose while paused.
        before=page.evaluate("() => window.enemyFrames.slice(-30)")
        page.wait_for_function("window.enemyFrames.length >= 180")
        self.assertEqual(page.evaluate("() => window.enemyFrames.slice(-30)"),before)
        paused_flyer=before[3][0]
        page.evaluate("window.enemyFrames=[]")
        page.locator("#pause").tap()
        page.wait_for_function("""column => {
          const flyer=window.enemyFrames.find(frame=>frame[1]===39*48);
          return Boolean(flyer) && window.enemyFrames.filter(frame=>frame[1]===39*48)
            .filter((_,index)=>index%6===0).some(frame=>frame[0]!==column);
        }""",arg=paused_flyer)
        self.assertTrue(page.locator("#board").is_visible())
