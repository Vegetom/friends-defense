const test=require('node:test');
const assert=require('node:assert/strict');
const {createModel,createValidationModel}=require('./model.cjs');
const fixture=require('./fixtures/save-v38.json');

test('La Mare lets the island be built without blocking the ground route, and a bank can divert it',()=>{
 const m=createModel({prototypeSession:true});
 m.set({level:1});
 const initial=m.state().g.route;
 assert.equal(initial.length-1,16);
 assert.equal(initial.includes(38),false);
 assert.equal(m.buy(38,0),true);
 assert.deepEqual(m.state().g.route,initial);
 assert.equal(m.buy(70,0),true);
 assert.equal(m.state().g.route.length-1,18);
});

test('the Bastion keeps its zigzag when the terraces are built',()=>{
 const m=createModel({prototypeSession:true});
 m.set({level:3});
 const route=m.state().g.route;
 assert.equal(route.length-1,22);
 assert.equal(m.buy(1,0),false); // corridor
 assert.equal(m.buy(11,0),true); // entry terrace
 assert.equal(m.buy(49,0),true); // middle terrace
 assert.equal(m.buy(81,0),true); // exit terrace
 assert.deepEqual(m.state().g.route,route);
});

test('a start at the Bastion only earns stars for played waves',()=>{
 const m=createModel({prototypeSession:true});
 for(const g of [{wave:0},{wave:1,active:true},{wave:1,ended:true,life:0}]){
  m.set({level:3,stars:18,bestWave:27,g:{...g,runStart:3}});
  const reward=m.rewardStars(false,true);
  assert.equal(reward.earned,0);
  assert.equal(reward.record,false);
  assert.equal(reward.extras.terrain,0);
  assert.equal(m.state().bestWave,27);
 }
 m.set({level:3,stars:18,bestWave:30,g:{wave:1,runStart:3}});
 const reward=m.rewardStars(false,true);
 assert.equal(reward.earned,6);
 assert.equal(reward.n,31);
 assert.equal(reward.start,3);
 assert.equal(reward.extras.terrain,0);
});

test('terrain transitions retain the start of the attempt and snapshot it',()=>{
 const m=createModel({prototypeSession:true});
 m.set({level:3,g:{wave:10,ended:true,life:12,retries:1,runStart:3}});
 m.nextLevel();
 assert.equal(m.state().level,4);
 assert.equal(m.state().g.runStart,3);
 assert.equal(m.state().buildCheckpoint.runStart,3);
});

test('the ring has two live sides and blocking its north side diverts enemies south',()=>{
 const m=createModel({prototypeSession:true});
 m.set({level:4});
 assert.ok(m.state().g.route.includes(16));
 assert.ok(m.buy(16,0));
 assert.ok(!m.state().g.route.includes(16));
 assert.ok(m.state().g.route.some(cell=>cell>=55));
});

test('Archipelago spawns an enemy on each arm and preserves both ground paths after loading',()=>{
 const m=createModel({prototypeSession:true});
 m.set({level:5});
 assert.ok(m.begin());
 m.spawn();m.spawn();
 const g=m.state().g,origin=m.position(66);
 assert.equal(g.enemies[0].branch,undefined);
 assert.equal(g.enemies[1].branch,1);
 assert.deepEqual([g.enemies[1].x,g.enemies[1].y],[origin.x,origin.y]);
 const validate=createValidationModel({prototypeSession:true});
 const saved=validate({...fixture,level:5,g,buildCheckpoint:null});
 assert.equal(saved.ok,true,saved.error);
 m.set({level:5,g:saved.data.g});
 m.step(.05);
 assert.ok(m.state().g.enemies[1].x>origin.x);
 assert.equal(m.state().g.enemies[1].y,origin.y);
 const legacy={...fixture.g,route:[],towers:{41:{type:0,lvl:1,invested:35}}};
 const old=validate({...fixture,level:5,g:legacy,buildCheckpoint:null});
 assert.equal(old.ok,true,old.error);
 assert.equal(old.data.g.layout,undefined);
});

test('a new finale start grants zero earned waves until a finale wave is completed',()=>{
 const m=createModel({prototypeSession:true});
 m.set({level:6,stars:20,bestWave:60,g:{runStart:6}});
 assert.equal(m.rewardStars(false).earned,0);
 m.set({level:6,stars:20,bestWave:60,g:{runStart:6,wave:1}});
 assert.equal(m.rewardStars(false).earned,6);
 assert.equal(m.state().bestWave,61);
});
