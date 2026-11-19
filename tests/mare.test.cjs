const test=require('node:test');
const assert=require('node:assert/strict');
const {createModel,createValidationModel}=require('./model.cjs');
const fixture=require('./fixtures/save-v38.json');

test('Mare preview matches real spawns and keeps bosses even in mixed waves',()=>{
 const m=createModel();
 for(const [wave,air,boss] of [[1,0,0],[2,4,0],[4,20,0],[5,5,1],[8,28,0],[10,10,1]]){
  m.set({level:1,g:{wave:wave-1}});
  const preview=m.threats(wave);
  assert.equal(preview.air,air);assert.equal(preview.boss,boss);
  m.begin();
  for(let i=0;i<m.state().g.total;i++)m.spawn();
  const enemies=m.state().g.enemies;
  assert.equal(enemies.filter(e=>e.air).length,preview.air);
  assert.equal(enemies.filter(e=>e.boss).length,preview.boss);
 }
});

test('legacy ongoing Mare wave stays terrestrial until it ends',()=>{
 const m=createModel();
 m.set({level:1,g:{active:true,wave:2,total:16,spawned:2}});
 m.spawn();
 assert.equal(m.state().g.enemies[0].air,false);
 m.set({level:1,g:{active:true,wave:2,total:16,spawned:2,activeAirKind:'mixed'}});
 m.spawn();
 assert.equal(m.state().g.enemies[0].air,true);
});

test('Mare grants one budget-neutral move only when a route remains',()=>{
 const m=createModel();
 m.set({level:1});
 for(const cell of [10,39,59])assert.equal(m.buy(cell,0),true);
 m.setGame({wave:1,towers:Object.fromEntries(Object.entries(m.state().g.towers)
  .map(([cell,tower])=>[cell,{...tower,fresh:false,lvl:2,invested:85}]))});
 const initial=m.state().g;
 for(const cell of [48,34,39,40]){
  assert.equal(m.relocate(10,cell),false);
  assert.deepEqual(m.state().g,initial);
 }
 assert.equal(m.relocate(10,31),true);
 const moved=m.state().g;
 assert.deepEqual(moved.towers[31],initial.towers[10]);
 assert.equal(moved.money,initial.money);
 assert.equal(moved.relocated,true);
 assert.equal(m.relocate(31,32),false);
 const saved=createValidationModel()({...fixture,level:1,buildCheckpoint:null,g:moved});
 assert.equal(saved.ok,true,saved.error);
 assert.equal(saved.data.g.relocated,true);
 assert.equal(saved.data.g.towers[31].invested,85);
});
