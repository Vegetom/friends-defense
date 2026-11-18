const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {createModel,createValidationModel,createStorageModel}=require('./model.cjs');
const validate=createValidationModel();
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/save-v38.json')));
const copy=value=>JSON.parse(JSON.stringify(value));

test('pinned legacy combat fixtures with effects, delayed hits, air units and boss remain loadable',()=>{
 for(const name of ['save-v38-active-effects.json','save-v38-air-boss.json']){
  const save=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures',name)));
  const result=validate(save);assert.equal(result.ok,true,`${name}: ${result.error}`);
  assert.equal(result.data.speed,1);assert.deepEqual(result.data.g.enemies,save.g.enemies);
 }
});

test('legacy v38 keeps all acquired progress, with speed defaulting to one',()=>{
 const before=copy(fixture),result=validate(fixture);
 assert.equal(result.ok,true,result.error);assert.equal(result.data.speed,1);
 for(const key of ['stars','bestWave','completed','metaLevels'])assert.deepEqual(result.data[key],fixture[key]);
 assert.deepEqual(fixture,before,'validation must not mutate its input');
});

test('all three speeds and signed cooldowns/clocks remain valid',()=>{
 for(const speed of [1,2,3]){
  const save=copy(fixture);save.speed=speed;save.clock=-0.01;save.g.clock=-0.1;
  save.g.towers['31']={type:1,lvl:1,cd:-0.04,invested:65,fresh:false};
  const result=validate(save);assert.equal(result.ok,true,result.error);assert.equal(result.data.speed,speed);
  assert.equal(result.data.g.towers['31'].cd,-0.04);
 }
});

test('real running model states validate on all seven maps without narrowing their phases',()=>{
 for(let level=0;level<7;level++){
  const model=createModel();model.set({level,g:{money:5000},metaLevels:[3,3,3,3,3]});
  model.begin();
  for(let step=0;step<60;step++)model.step(1/60);
  const save={...copy(fixture),level,g:model.state().g,buildCheckpoint:null};
  const result=validate(save);assert.equal(result.ok,true,`map ${level}: ${result.error}`);
  assert.equal(result.data.buildCheckpoint,null,'an active state without a checkpoint must not invent one');
 }
});

test('reward receipt with an active ended attempt and workshop phases are legitimate legacy states',()=>{
 const save=copy(fixture);save.rewardOpen=true;save.runEnded=true;save.g.active=true;save.g.total=14;save.g.spawned=0;
 save.metaLastEarned={earned:6,n:1,before:73,after:79,record:true,win:false};
 assert.equal(validate(save).ok,true);
 save.rewardOpen=false;save.workshopOpen=true;save.paused=true;
 assert.equal(validate(save).ok,true);
 save.workshopOpen=false;save.g.active=false;save.g.bonus=true;
 assert.equal(validate(save).ok,true);
});

test('a legacy carried-heart checkpoint is repaired only on an unambiguous unfinalized map entry',()=>{
 const model=createModel();model.set({level:1,g:{wave:0,retries:0}});
 const base={...copy(fixture),level:1,runHearts:2,g:model.state().g};
 base.buildCheckpoint=copy(base.g);base.g.retries=2;
 for(const phase of ['preparation','active','loss']){
  const save=copy(base);if(phase!=='preparation')save.g.wave=1;
  if(phase==='active'){save.g.active=true;save.g.total=14;save.g.spawned=0;}if(phase==='loss'){save.g.ended=true;save.g.life=0;}
  const result=validate(save);assert.equal(result.ok,true,result.error);assert.equal(result.data.buildCheckpoint.retries,2);
 }
 for(const mutation of [s=>s.runEnded=true,s=>s.runHearts=0,s=>s.g.wave=5,s=>s.g.wave=1]){
  const save=copy(base);mutation(save);const result=validate(save);
  assert.equal(result.ok,true,result.error);assert.equal(result.data.buildCheckpoint.retries,0);
 }
});

test('malformed, unknown and dangerous data are rejected without mutation or guessed acquired progress',()=>{
 const cases=[null,{}, {...fixture,version:39},{...fixture,g:null},{...fixture,g:{}},
  {...fixture,stars:-1},{...fixture,speed:4},{...fixture,metaLevels:[9]},
  {...fixture,g:{...copy(fixture.g),towers:{'0':{type:99,lvl:1,invested:0}}}},
  JSON.parse('{"version":38,"__proto__":{"polluted":true}}')];
 for(const input of cases){const before=copy(input);assert.equal(validate(input).ok,false);assert.deepEqual(input,before);}
 assert.equal({}.polluted,undefined);
 const damaged=copy(fixture);damaged.g={};
 assert.deepEqual(validate.recover(damaged),{stars:73,bestWave:48,completed:true,metaLevels:[2,1,3,0,2]});
 assert.equal(validate.recover({...damaged,version:39}),null);
 assert.equal(validate.recover({...damaged,stars:'73'}),null);
});

test('nested entities and collections cannot smuggle invalid runtime bodies',()=>{
 for(const mutate of [
  s=>s.g.enemies=[{}],s=>s.g.fx=[{}],s=>s.g.zones=[{}],s=>s.g.delayed=[{}],
  s=>s.buildCheckpoint={money:0},s=>s.g.perks='tom',s=>s.g.route=null,
 ]){
  const save=copy(fixture);mutate(save);const result=validate(save);
  // The saved route is derived and may be repaired safely; unsafe bodies are not.
  if(save.g.route===null)assert.equal(result.ok,true);else assert.equal(result.ok,false);
 }
});

test('new map checkpoints include all carried hearts before the first wave',()=>{
 for(let level=1;level<7;level++)for(const hearts of [0,1,2]){
  const model=createModel();model.set({runHearts:hearts});model.startLevel(level);
  const state=model.state();assert.equal(state.g.retries,hearts);
  assert.equal(state.runHearts,hearts);assert.equal(state.buildCheckpoint.retries,hearts);
 }
});

test('retry restores only the checkpoint budget and consumes exactly one preexisting heart',()=>{
 const cp=copy(fixture.g);Object.assign(cp,{wave:4,money:410,life:12,retries:2});
 cp.towers={'31':{type:1,lvl:1,invested:65,cd:0,fresh:false}};
 const failed=copy(cp);Object.assign(failed,{wave:5,money:338,life:0,retries:2,ended:true});
 failed.towers['31']={type:1,lvl:2,invested:155,cd:-0.1,fresh:false};
 failed.towers['33']={type:0,lvl:1,invested:35,cd:0,fresh:false};
 const model=createModel();model.set({g:failed,buildCheckpoint:cp,runHearts:2,stars:73});
 for(const remaining of [1,0]){
  assert.equal(model.canRetryWave(),true);assert.equal(model.retryWave(),true);
  const restored=model.state();assert.equal(restored.g.money,410);assert.equal(restored.g.life,12);
  assert.equal(restored.g.retries,remaining);assert.equal(restored.buildCheckpoint.retries,remaining);
  assert.equal(restored.stars,73);assert.deepEqual(Object.keys(restored.g.towers),['31']);
  assert.equal(restored.g.towers['31'].lvl,1);
  model.setGame({wave:5,life:0,ended:true,active:false});
 }
 assert.equal(model.canRetryWave(),false);assert.equal(model.retryWave(),false);
});

test('a heart earned during the failed boss wave cannot fund its own retry',()=>{
 const cp=copy(fixture.g);cp.retries=0;cp.wave=4;
 const model=createModel();model.set({g:{wave:5,life:0,ended:true,retries:1},buildCheckpoint:cp,runHearts:1});
 assert.equal(model.canRetryWave(),false);assert.equal(model.retryWave(),false);
});

test('unsafe checkpoints and noncanonical cell names are rejected before any retry',()=>{
 for(const mutate of [
  s=>s.buildCheckpoint.active=true,s=>s.buildCheckpoint.ended=true,
  s=>s.buildCheckpoint.bonus=true,s=>s.buildCheckpoint.life=0,
  s=>s.buildCheckpoint.wave=3,s=>s.buildCheckpoint.fx=[{}],
  s=>s.g.towers['031']={type:1,lvl:1,invested:65,cd:0,fresh:false},
 ]){
  const save=copy(fixture);mutate(save);assert.equal(validate(save).ok,false);
  assert.deepEqual(validate.recover(save),{stars:73,bestWave:48,completed:true,metaLevels:[2,1,3,0,2]});
 }
});

test('the actual save writer validates memory before replacing a valid stored profile',()=>{
 const raw=JSON.stringify(fixture),model=createStorageModel(fixture,raw);
 model.damage();assert.equal(model.save(),false);
 assert.equal(model.raw(),raw);assert.deepEqual(model.writes(),[]);
 assert.match(model.message(),/non enregistrée/);assert.equal(model.exportVisible(),true);
});

test('the actual writer keeps unknown, corrupt, unreadable and quota-protected profiles intact',()=>{
 for(const raw of ['{invalid json',JSON.stringify({...fixture,version:99}),JSON.stringify({...fixture,g:{}})]){
  const model=createStorageModel(fixture,raw);assert.equal(model.save(),false);
  assert.equal(model.raw(),raw);assert.deepEqual(model.writes(),[]);
 }
 for(const failure of ['get','set']){
  const raw=JSON.stringify(fixture),model=createStorageModel(fixture,raw);model.failure(failure);
  assert.equal(model.save(),false);assert.equal(model.raw(),raw);assert.equal(model.exportVisible(),true);
 }
 const model=createStorageModel(fixture);model.speed(3);assert.equal(model.save(),true);
 const saved=JSON.parse(model.raw());assert.equal(saved.speed,3);assert.equal(saved.stars,73);
});

test('an active wave needs its actual counters instead of silently becoming completed',()=>{
 for(const mutation of [
  s=>delete s.g.total,s=>delete s.g.spawned,s=>s.g.total=0,
  s=>s.g.spawned=15,s=>s.g.spawned=-1,s=>s.g.total=14.5,
 ]){
  const save=copy(fixture);save.g.active=true;save.g.total=14;save.g.spawned=0;
  mutation(save);assert.equal(validate(save).ok,false);
 }
});
