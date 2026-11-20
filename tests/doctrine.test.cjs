const test=require('node:test');
const assert=require('node:assert/strict');
const {createModel,createValidationModel}=require('./model.cjs');
const fixture=require('./fixtures/save-v38.json');

function enemy(x,y,overrides={}){
 return {x,y,k:0,progress:0,hp:1000,max:1000,vel:80,reward:4,
   slow:0,slowPower:.3,shield:0,armor:0,mark:0,flash:0,burn:0,...overrides};
}

test('only a resolved and defeated first boss offers a lasting choice',()=>{
 const m=createModel(), enemyBoss=enemy(30,270,{boss:true,hp:0,reward:45});
 m.set({g:{wave:5,active:true,total:1,spawned:1,life:15,enemies:[enemyBoss]}});
 assert.equal(m.choose('escadron'),false);
 m.step(1/60);
 assert.deepEqual(Array.from(m.bonusOptions(),b=>b.id),['escadron','embuscade','sansDoctrine']);
 assert.equal(m.begin(),false);
 assert.equal(m.choose('embuscade'),true);
 assert.equal(m.choose('escadron'),false);
 assert.equal(m.state().buildCheckpoint.doctrine,'embuscade');
 assert.deepEqual(m.state().g.perks,[]);
 m.setGame({wave:10,ended:true});
 m.nextLevel();
 assert.equal(m.state().level,1);
 assert.equal(m.state().g.doctrine,'embuscade');
 assert.equal(m.state().buildCheckpoint.doctrine,'embuscade');
 m.startLevel(0);
 assert.equal(m.state().g.doctrine,undefined);
 m.set({g:{wave:5,life:10,active:true,total:1,spawned:1,bossEscaped:true}});
 m.step(1/60);
 assert.equal(m.state().g.bonus,false);
});

test('Escadron affects air shots from eligible positions only',()=>{
 const damage=(cell,air,doctrine)=>{
  const m=createModel();
  m.set({g:{wave:4,doctrine}});
  const p=m.position(cell);
  m.setGame({towers:{[cell]:{type:1,lvl:1,cd:0}},enemies:[enemy(p.x,270,{air})]});
  m.attack(cell,1/60);
  return 1000-m.state().g.enemies[0].hp;
 };
 assert.ok(Math.abs(damage(31,true,'escadron')-48.8)<1e-9);
 assert.equal(damage(21,true,'escadron'),40);
 assert.equal(damage(31,false,'escadron'),40);
 assert.equal(damage(31,true,'sansDoctrine'),40);
});

test('Embuscade expands only the explosion into a slowed ground group',()=>{
 const secondary=(slow,air,doctrine)=>{
  const m=createModel();
  m.set({g:{wave:4,doctrine}});
  const p=m.position(31);
  m.setGame({towers:{31:{type:2,lvl:1,cd:0}},
   enemies:[enemy(p.x+20,p.y,{progress:3,slow,air}),enemy(p.x+80,p.y,{progress:2,air})]});
  m.attack(31,1/60);
  return m.state().g.enemies[1].hp;
 };
 assert.ok(secondary(1,false,'embuscade')<1000);
 assert.equal(secondary(0,false,'embuscade'),1000);
 assert.equal(secondary(1,true,'embuscade'),1000);
 assert.equal(secondary(1,false,'sansDoctrine'),1000);
});

test('v38 supports the doctrine in the checkpoint without adding it to old saves',()=>{
 const validate=createValidationModel();
 assert.equal(validate(fixture).data.g.doctrine,undefined);
 const fresh=structuredClone(fixture);
 fresh.g.doctrine=fresh.buildCheckpoint.doctrine='escadron';
 const saved=validate(fresh);
 assert.equal(saved.ok,true);
 assert.equal(saved.data.buildCheckpoint.doctrine,'escadron');
 fresh.g.doctrine='invalid';
 assert.equal(validate(fresh).ok,false);
});
