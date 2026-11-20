const test = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { createModel, script } = require('./model.cjs');

test('the complete actual game script is valid JavaScript', () => {
  const checked = spawnSync(process.execPath, ['--check'], { input: script, encoding: 'utf8' });
  assert.equal(checked.status, 0, checked.stderr);
});

const cases = [
  ['before wave 1', 0, {wave:0}, false, true, 0, 0, false],
  ['wave 1 active abandonment', 0, {wave:1,active:true}, false, true, 0, 0, false],
  ['wave 1 defeat', 0, {wave:1,ended:true,life:0}, false, false, 0, 0, false],
  ['wave 1 completed', 0, {wave:1}, false, true, 1, 6, false],
  ['wave 2 active after wave 1', 0, {wave:2,active:true}, false, true, 1, 6, false],
  ['wave 2 defeat after wave 1', 0, {wave:2,ended:true,life:0}, false, false, 1, 6, false],
  ['bonus choice after wave 3', 0, {wave:3,bonus:true}, false, true, 3, 7, false],
  ['first map final defeat', 0, {wave:10,ended:true,life:0}, false, false, 9, 10, false],
  ['first map victory', 0, {wave:10,ended:true,life:15}, true, false, 10, 11, false],
  ['campaign final defeat', 6, {wave:10,ended:true,life:0}, false, false, 69, 35, false],
  ['campaign victory', 6, {wave:10,ended:true,life:15}, true, false, 70, 46, true],
  ['inconsistent win while active', 6, {wave:10,active:true}, true, false, 69, 35, false],
  ['inconsistent win before campaign', 0, {wave:0}, true, false, 0, 0, false],
  ['inconsistent win in final preparation', 6, {wave:0}, true, false, 60, 34, false],
  ['inconsistent win after final defeat', 6, {wave:10,ended:true,life:0}, true, false, 69, 35, false],
];

for (const [name,level,g,win,forfeit,n,earned,campaignWin] of cases) {
  test(name, () => {
    const model=createModel();model.set({level,g});
    assert.equal(model.globalWaveCleared(),n);
    const reward=model.rewardStars(win,forfeit),state=model.state();
    assert.equal(reward.n,n);assert.equal(reward.earned,earned);
    assert.equal(reward.win,campaignWin);assert.equal(state.completed,campaignWin);
    assert.equal(state.bestWave,n);assert.equal(state.stars,earned);
    assert.equal(reward.record,n>0);
  });
}

test('active first waves on maps 2–7 retain all previously completed maps', () => {
  const expected=[[1,10,13],[2,20,17],[3,30,21],[4,40,26],[5,50,30],[6,60,34]];
  for(const [level,n,earned] of expected){
    const model=createModel();model.set({level,g:{wave:1,active:true}});
    const reward=model.rewardStars(false,true);
    assert.equal(reward.n,n);assert.equal(reward.earned,earned);
  }
});

test('existing progression and records are never retrospectively reduced', () => {
  const model=createModel(),metaLevels=[2,1,3,0,2];
  model.set({stars:73,bestWave:70,completed:true,metaLevels,g:{wave:1,active:true}});
  const reward=model.rewardStars(false,true),state=model.state();
  assert.equal(reward.earned,0);assert.equal(reward.record,false);
  assert.equal(state.stars,73);assert.equal(state.bestWave,70);assert.equal(state.completed,true);
  assert.deepEqual(state.metaLevels,metaLevels);
});

test('a repeated campaign win keeps its victory bonus without another terrain prime', () => {
  const model=createModel();model.set({level:6,bestWave:70,g:{wave:10,ended:true,life:15}});
  const reward=model.rewardStars(true);
  assert.equal(reward.record,false);assert.equal(reward.earned,37);assert.equal(reward.win,true);
  assert.equal(reward.extras.terrain,0);
});

test('finishing one attempt twice pays only once', () => {
  const model=createModel();model.set({g:{wave:2,active:true},runHearts:2});
  model.finishRun(false,true);model.finishRun(false,true);
  const state=model.state();
  assert.equal(state.stars,6);assert.equal(state.bestWave,1);assert.equal(state.saved,1);
  assert.equal(state.rewards.length,1);assert.equal(state.runHearts,0);assert.equal(state.runEnded,true);
});

test('a real end-of-wave step changes the count only after all enemies are resolved', () => {
  const model=createModel();model.set();
  assert.equal(model.buy(31,0),true);assert.equal(model.buy(33,0),true);assert.equal(model.buy(35,1),true);
  assert.equal(model.begin(),true);assert.equal(model.globalWaveCleared(),0);
  let frames=0;
  while(model.state().g.active&&frames<6000){model.step(1/60);frames++}
  const finished=model.state();
  assert.ok(frames<6000);assert.equal(finished.g.wave,1);assert.equal(finished.g.active,false);
  assert.equal(finished.g.killed,14);assert.equal(finished.g.escaped,0);assert.equal(finished.g.life,15);
  assert.equal(model.globalWaveCleared(),1);assert.equal(model.rewardStars(false,true).earned,6);
});

test('a repeated run earns more past the first boss, but never for a boss on an unfinished wave',()=>{
  const m=createModel(),earned=g=>{
    m.set({bestWave:48,g});
    return m.rewardStars(false,true);
  };
  assert.equal(earned({wave:1}).earned,5);
  assert.equal(earned({wave:3}).earned,6);
  assert.equal(earned({wave:5,active:true,bossDefeated:true}).extras.boss,0);
  const win=earned({wave:5,bossDefeated:true,bonus:true});
  assert.equal(win.earned,8);
  assert.deepEqual({...win.extras},{distance:1,boss:2,terrain:0});
  assert.equal(earned({wave:6,doctrine:'sansDoctrine'}).earned,9);
});

test('terrain primes award only newly crossed complete-map thresholds',()=>{
  const m=createModel();
  m.set({level:2,bestWave:19,g:{wave:10,active:true,doctrine:'embuscade'}});
  const result=m.rewardStars(false,true);
  assert.equal(result.n,29);
  assert.equal(result.extras.terrain,1);
  assert.equal(result.extras.boss,2);
  m.set({level:2,bestWave:29,g:{wave:10,ended:true,life:0}});
  assert.equal(m.rewardStars(false).extras.terrain,0);
});

test('resolved leaks are counted by enemy type and copied into a loss receipt',()=>{
  const m=createModel();m.set({g:{wave:5,life:2}});
  m.begin();
  const before=m.state().g,exitIndex=before.route.length-1;
  const p=m.position(before.route[exitIndex]);
  const enemy={...p,k:exitIndex,progress:0,hp:50,max:50,vel:70,reward:4,slow:0,flash:0};
  m.setGame({spawned:before.total,enemies:[{...enemy,air:true,progress:1},enemy]});
  m.step(1/60);
  const after=m.state().g;
  assert.equal(after.life,0);
  assert.deepEqual(after.waveLeaks,{air:1,ground:1,boss:0});
  m.finishRun(false);
  assert.deepEqual(m.state().rewards[0].debrief,{wave:6,air:1,ground:1,boss:0});
});
