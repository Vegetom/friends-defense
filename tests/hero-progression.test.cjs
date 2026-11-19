const test=require('node:test');
const assert=require('node:assert/strict');
const {createModel,createValidationModel}=require('./model.cjs');
const fixture=require('./fixtures/save-v38.json');

function fight(type,tier,perks=[]){
 const m=createModel(), metaLevels=[0,0,0,0,0];
 metaLevels[type]=tier;
 m.set({level:3,metaLevels});
 const p=m.position(1);
 const target=(overrides={})=>({...p,hp:100000,max:100000,k:0,vel:80,progress:0,reward:4,armor:0,shield:0,maxShield:0,impactArmor:0,flash:0,mark:0,slow:0,slowPower:0,burn:0,...overrides});
 const prepare=(enemies,tower={})=>m.setGame({wave:4,active:true,clock:99,total:24,spawned:24,enemies,perks,towers:{1:{type,lvl:1,invested:155,cd:0,...tower}}});
 return {m,p,target,prepare,attack(){m.attack(1,1/60);return m.state().g}};
}

test('Tom N2 intercepts aircraft and N3 doubles up on an isolated flier',()=>{
 const f=fight(0,2);
 f.prepare([f.target({progress:2}),f.target({air:true,progress:0})]);
 let g=f.attack();
 assert.ok(g.enemies[1].hp<g.enemies[0].hp);
 const routeLength=g.route.length;
 f.prepare([f.target({progress:routeLength-1.1}),f.target({air:true,progress:0})]);
 g=f.attack();
 assert.ok(g.enemies[0].hp<g.enemies[1].hp);
 const n3=fight(0,3);
 n3.prepare([n3.target({air:true})]);
 assert.equal(n3.attack().fx.length,2);
});

test('Raphaël removes extra shield without extra overflow and orbital marks survivors',()=>{
 const f=fight(1,3), e=f.target({shield:110,maxShield:110});
 f.m.hurt(e,100,false,1,.2);
 assert.equal(e.shield,0);
 assert.equal(e.hp,e.max);
 f.prepare([f.target({x:f.p.x+30}),f.target({x:f.p.x+30,y:f.p.y+42})],{shots:2});
 const g=f.attack();
 assert.equal(g.enemies[0].mark,3.1);
 // Use an adjacent enemy outside the direct beam's height on this fixture.
 assert.equal(g.enemies[1].mark,1.5);
});

test('Ylvine fire blocks regeneration in the zone and the shock extends the associated pool',()=>{
 const f=fight(2,3);
 f.prepare([f.target({hp:500,regen:.01})]);
 const p=f.m.position(0);
 f.m.setGame({towers:{},enemies:[f.target({...p,hp:500,regen:.01})],
  zones:[{...p,kind:'fire',key:'pool',r:2,life:1,age:0,dps:60,power:.28,air:false}],
  delayed:[{...p,kind:'shock',fireKey:'pool',wait:0,r:1,dmg:10,air:false}]});
 f.m.step(1/60);
 let g=f.m.state().g;
 assert.equal(g.enemies[0].hp,489);
 assert.ok(g.zones[0].life>1.45);
 f.m.setGame({zones:[]});f.m.step(1/60);
 assert.ok(f.m.state().g.enemies[0].hp>489);
});

test('Jordan prioritizes fresh targets and Long hiver extends direct control',()=>{
 const f=fight(3,1,['longWinter']);
 f.prepare([f.target({progress:2}),f.target({progress:1,slow:.5,slowPower:.3}),f.target()]);
 const g=f.attack();
 assert.equal(g.enemies[0].slow,1.9);
 assert.equal(g.enemies[1].slow,.5);
 assert.equal(g.enemies[2].slow,1.525);
});

test('POY stores Rage until an eligible target and retains its charge in a v38 save',()=>{
 const f=fight(4,2);
 f.prepare([f.target()],{shots:3});
 let g=f.attack();
 assert.equal(g.towers[1].nextRage,4);
 f.prepare([f.target({elite:true})],{shots:4,nextRage:4});
 g=f.attack();
 assert.equal(g.towers[1].nextRage,9);
 const valid=createValidationModel()({...fixture,level:3,buildCheckpoint:null,g});
 assert.equal(valid.ok,true,valid.error);
 assert.equal(valid.data.g.towers[1].nextRage,9);
});

test('each rotating card appears once per terrain and selected perks survive a v38 round trip',()=>{
 const m=createModel(), seen=[];
 for(const wave of [3,6,9]){
  m.set({level:0,g:{wave,bonus:true,bonusRotation:1}});
  const ids=Array.from(m.bonusOptions(),b=>b.id);
  assert.equal(ids.length,4); seen.push(ids[3]);
  assert.equal(m.choose(ids[3]),true);
  const state=m.state();
  const valid=createValidationModel()({...fixture,level:0,buildCheckpoint:state.buildCheckpoint,g:state.g});
  assert.equal(valid.ok,true,valid.error);
  assert.deepEqual(valid.data.g.perks,[ids[3]]);
  assert.equal(valid.data.g.bonusRotation,1);
 }
 assert.deepEqual(seen,['shieldBreach','longWinter','airBeacon']);
});

test('Apocalypse lands once per enemy for a synchronized salvo while legacy impacts remain valid',()=>{
 const f=fight(4,3), p=f.m.position(0);
 f.prepare([f.target({...p})],{shots:4});
 f.m.setGame({towers:{},delayed:Array.from({length:3},()=>({...p,kind:'apocalypse',volley:'1:5',wait:0,r:1,dmg:100,air:false}))});
 f.m.step(1/60);
 assert.equal(f.m.state().g.enemies[0].hp,99900);
});

test('Balise reaches beyond the usual air range and Brèche halves shield recharge',()=>{
 const base=fight(0,0), beacon=fight(0,0,['airBeacon']);
 for(const f of [base,beacon])f.prepare([f.target({air:true,x:f.p.x+72})]);
 assert.equal(base.attack().fx.length,0);
 assert.equal(beacon.attack().fx.length,1);
 const breach=fight(0,0,['shieldBreach']);
 const result=[base,breach].map(f=>{
  f.prepare([f.target({...f.m.position(0),shield:0,maxShield:200})]);
  f.m.setGame({towers:{}});f.m.step(1/60);return f.m.state().g.enemies[0].shield;
 });
 assert.equal(result[0],result[1]*2);
});

test('Ylvine N3 aligns meteor impacts with a vertical ground segment',()=>{
 const f=fight(2,3);
 f.prepare([f.target()]);
 f.m.setGame({route:[0,6,12]});
 const impacts=f.attack().delayed.filter(z=>z.kind==='meteor');
 assert.equal(impacts.length,3);
 assert.deepEqual(impacts.map(z=>[z.x-f.p.x,z.y-f.p.y]),[[0,-58],[0,0],[0,58]]);
});

test('Jordan N2 uses the strongest overlapping ice and N3 extends an existing strong freeze',()=>{
 const ice=fight(3,2), p=ice.m.position(0);
 ice.prepare([ice.target({...p})]);
 const patch={...p,kind:'ice',r:2,life:1,age:0,dps:0,air:false};
 ice.m.setGame({towers:{},zones:[{...patch,power:.4},{...patch,power:.2}]});
 ice.m.step(1/60);
 assert.equal(ice.m.state().g.enemies[0].slowPower,.4);
 const blizzard=fight(3,3);
 blizzard.prepare([blizzard.target({slow:1.8,slowPower:.45})],{shots:3});
 const target=blizzard.attack().enemies[0];
 assert.equal(target.slow,2);
 assert.equal(target.slowPower,.45);
});

test('POY N1 pierces only the primary target impact plating',()=>{
 const base=fight(4,0), evolved=fight(4,1);
 for(const f of [base,evolved])f.prepare([f.target({impactArmor:90}),f.target({impactArmor:90})]);
 const before=base.attack(), after=evolved.attack(), baseDmg=base.m.stats(1).damage,evolvedDmg=evolved.m.stats(1).damage;
 assert.equal(before.enemies[0].hp,100000-(baseDmg-90));
 assert.equal(after.enemies[0].hp,100000-(evolvedDmg-67.5));
 assert.equal(after.enemies[1].hp,100000-(evolvedDmg*.75-90));
});
