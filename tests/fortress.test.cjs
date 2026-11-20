const test=require('node:test');
const assert=require('node:assert/strict');
const {createModel,createValidationModel}=require('./model.cjs');
const fixture=require('./fixtures/save-v38.json');

test('Fortress convoys cluster the existing quota of tanks between two fast escorts',()=>{
 const m=createModel();
 for(const [wave,count] of [[3,3],[6,3],[9,4]]){
  m.set({level:2,g:{wave:wave-1}});
  const threat=m.threats(wave);
  assert.equal(threat.tank,count);
  assert.equal(threat.fast,2);
  assert.equal(threat.air,0);
  assert.equal(m.begin(),true);
  const size=m.state().g.total;
  for(let i=0;i<size;i++)m.spawn();
  const enemies=m.state().g.enemies,first=enemies.findIndex(e=>e.tank);
  assert.equal(enemies.filter(e=>e.tank).length,count);
  assert.ok(enemies.slice(first,first+count).every(e=>e.tank&&!e.air));
  assert.ok(enemies[first-1].fast&&enemies[first+count].fast);
  assert.ok(enemies.every(e=>!e.air));
 }
});

test('A historical Fortress wave keeps its airborne units, while the new plan survives saving',()=>{
 const m=createModel();
 m.set({level:2,g:{wave:9,active:true,total:32,spawned:2}});
 assert.ok(m.threats(9).air>0);
 m.spawn();
 assert.equal(m.state().g.enemies[0].air,true);

 m.set({level:2,g:{wave:8}});
 assert.equal(m.begin(),true);
 const g=m.state().g;
 const checked=createValidationModel()({...fixture,level:2,buildCheckpoint:null,g});
 assert.equal(checked.ok,true,checked.error);
 assert.equal(checked.data.g.activeAirKind,'');
 m.set({level:2,g:{...checked.data.g,spawned:2}});
 m.spawn();
 assert.equal(m.state().g.enemies[0].air,false);
 assert.equal(m.threats(9).air,0);
});
