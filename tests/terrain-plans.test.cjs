const test=require('node:test');
const assert=require('node:assert/strict');
const {createModel,createValidationModel}=require('./model.cjs');
const fixture=require('./fixtures/save-v38.json');

const ids=m=>Array.from(m.bonusOptions(),b=>b.id);
test('a new wave completion on pilot maps offers Budget; a pending legacy choice is unchanged',()=>{
 const m=createModel();
 m.set({level:1,g:{wave:3,active:true,total:18,spawned:18}});
 m.step(1/60);
 assert.deepEqual(ids(m),['supplies','contract']);
 const cash=m.state().g.money;
 assert.equal(m.choose('supplies'),true);
 assert.equal(m.state().g.money,cash+75);
 assert.equal(m.state().buildCheckpoint.money,cash+75);
 assert.equal(m.choose('supplies'),false);
 m.set({level:1,g:{wave:3,bonus:true}});
 assert.ok(ids(m).includes('eco5'));
 m.set({level:3,g:{wave:3,active:true,total:22,spawned:22}});
 m.step(1/60);
 assert.ok(ids(m).includes('eco5'));
});

test('the Contract pays 55 exact Z only after waves 4 and 5 on every pilot map',()=>{
 const m=createModel();
 for(const level of [0,1,2]){
  m.set({level});
  const without=[4,5,6].map(w=>m.wavePay(w));
  m.set({level,g:{wave:3,bonus:true,planOffer:true}});
  assert.equal(m.choose('contract'),true);
  const withContract=[4,5,6].map(w=>m.wavePay(w));
  assert.deepEqual(withContract.map((v,i)=>v-without[i]),[55,55,0]);
  const cash=m.state().g.money;
  assert.equal(m.begin(),true);
  assert.equal(m.state().g.money,cash);
  m.setGame({spawned:1,total:1,life:0});
  m.step(1/60);
  assert.equal(m.state().g.money,cash);
  m.set({level,g:{wave:4,active:true,spawned:1,total:1,money:cash,perks:['contract']}});
  const earned=m.wavePay(4);
  m.step(1/60);
  assert.equal(m.state().g.money,cash+earned);
  m.step(1/60);
  assert.equal(m.state().g.money,cash+earned);
 }
});

test('tactical choices stay usable and show Jordan when he can defend a Fortress convoy',()=>{
 const m=createModel(),g={wave:6,bonus:true,planOffer:true};
 m.set({level:2,g});
 assert.deepEqual(ids(m),['rangePlan','airBeacon']);
 m.set({level:2,g:{...g,perks:['airBeacon']}});
 assert.deepEqual(ids(m),['rangePlan','cadencePlan']);
 m.set({level:2,g:{...g,towers:{11:{type:3,lvl:1}}}});
 assert.deepEqual(ids(m),['rangePlan','airBeacon','longWinter']);
 assert.equal(m.choose('longWinter'),true);
 assert.equal(m.state().buildCheckpoint.terrainTactic,'longWinter');
});

test('repair appears only when needed and caps actual healing at 15 lives',()=>{
 const m=createModel(),g={wave:9,bonus:true,planOffer:true};
 m.set({g});
 assert.deepEqual(ids(m),['assaultPlan','escortPlan']);
 m.set({g:{...g,life:14}});
 assert.ok(ids(m).includes('repairPlan'));
 assert.equal(m.choose('repairPlan'),true);
 const state=m.state();
 assert.equal(state.g.life,15);
 const result=createValidationModel()({...fixture,g:state.g,buildCheckpoint:state.buildCheckpoint});
 assert.equal(result.ok,true,result.error);
 assert.deepEqual(result.data.g.perks,['repairPlan']);
});
