const test=require('node:test');
const assert=require('node:assert/strict');
const {createModel,createValidationModel}=require('./model.cjs');
const fixture=require('./fixtures/save-v38.json');

function enemy(p, overrides={}){
 return {...p,k:0,hp:500,max:500,vel:80,progress:0,reward:4,
  armor:0,shield:0,flash:0,slow:0,slowPower:0,burn:0,mark:0,...overrides};
}

test('Tom credits the PV removed from each target without counting shields or overkill',()=>{
 const m=createModel();
 m.set({metaLevels:[1,0,0,0,0],g:{towers:{1:{type:0,lvl:1,cd:0}}}});
 assert.ok(m.begin());
 const p=m.position(1);
 m.setGame({enemies:[enemy(p,{hp:2,shield:3,progress:2}),enemy(p,{hp:1,progress:1}),enemy(p)]});
 m.attack(1,1/60);
 let g=m.state().g;
 assert.deepEqual(g.enemies.map(e=>e.hp),[0,0,500]);
 assert.deepEqual(g.combatReport.damage,[3,0,0,0,0]);
 assert.deepEqual(g.combatReport.forms,[1,0,0,0,0]);
});

test('zone ticks and delayed attacks credit their distinct heroes',()=>{
 const m=createModel(),p=m.position(0),dt=1/60;
 const fire={...p,kind:'fire',r:2,life:1,age:0,dps:60,power:.28,air:false};
 const meteor={...p,kind:'meteor',volley:'1:5',wait:0,r:1,dmg:10,air:false};
 const apocalypse={...meteor,kind:'apocalypse',dmg:30};
 m.setGame({active:true,wave:8,total:1,spawned:1,enemies:[enemy(p)],zones:[fire],
  delayed:[meteor,apocalypse,apocalypse]});
 m.step(dt);
 const g=m.state().g;
 assert.equal(g.enemies[0].hp,459);
 assert.deepEqual(g.combatReport.damage,[0,0,11,0,30]);
});

test('Jordan counts each slowed enemy once, including after a v38 reload',()=>{
 const m=createModel(),dt=1/60;
 m.set({level:1,g:{towers:{11:{type:3,lvl:1,cd:0,invested:155}}}});
 assert.ok(m.begin());
 const p=m.position(11);
 m.setGame({spawned:2,enemies:[enemy(p)],zones:[{...p,kind:'ice',r:2,life:1,age:0,dps:0,power:.3}]});
 m.attack(11,dt);
 assert.equal(m.state().g.combatReport.slowed,1);
 const validate=createValidationModel();
 const loaded=validate({...fixture,level:1,buildCheckpoint:null,g:m.state().g});
 assert.equal(loaded.ok,true,loaded.error);
 assert.equal(loaded.data.g.enemies[0].jordanCounted,true);
 m.set({level:1,g:loaded.data.g});
 m.step(dt);
 assert.equal(m.state().g.combatReport.slowed,1);
 assert.ok(m.state().g.combatReport.damage[3]>0);
});

test('retry restores the earlier report, and a new terrain starts a fresh report',()=>{
 const m=createModel();
 const before={damage:[12,0,0,0,0],forms:[1,0,0,0,0],slowed:0,partial:false};
 const failed={...before,damage:[34,0,0,0,0]};
 m.set({g:{wave:7,life:0,ended:true,combatReport:failed},buildCheckpoint:{...fixture.buildCheckpoint,wave:6,combatReport:before}});
 assert.ok(m.retryWave());
 assert.deepEqual(m.state().g.combatReport,before);
 m.setGame({wave:10,life:10,ended:true,combatReport:failed});
 m.nextLevel();
 assert.deepEqual(m.state().g.combatReport,{damage:[0,0,0,0,0],forms:[0,0,0,0,0],slowed:0,partial:false});
});

test('missing or damaged historical recap data cannot block progression',()=>{
 const validate=createValidationModel();
 const m=createModel();
 const bad=validate({...fixture,g:{...fixture.g,combatReport:{damage:['?']}}});
 assert.equal(bad.ok,true);
 assert.equal(bad.data.g.combatReport,undefined);
 assert.equal(bad.data.stars,fixture.stars);
 m.set({g:{...bad.data.g,combatReport:undefined}});
 assert.ok(m.begin());
 assert.equal(m.state().g.combatReport.partial,true);
});
