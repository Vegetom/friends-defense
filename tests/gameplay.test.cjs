const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {createModel,createValidationModel}=require('./model.cjs');

function enemy(overrides={}){
 return {x:0,y:0,hp:1000,max:1000,vel:80,k:0,progress:0,reward:4,
  impactArmor:90,armor:0,shield:0,maxShield:0,slow:0,slowPower:0,
  mark:0,flash:0,...overrides};
}

test('impact plating subtracts each hit before the remaining shield and percentage armour',()=>{
 const model=createModel();model.set({level:3});
 const e=enemy({shield:10,maxShield:10,armor:.25});
 model.hurt(e,85);assert.equal(e.shield,10);assert.equal(e.hp,1000);
 model.hurt(e,110);assert.equal(e.shield,0);assert.equal(e.hp,992.5);
});

test('marking and freezing reduce plating independently and combine without new permanent-tier rules',()=>{
 const model=createModel();
 assert.equal(model.impactArmor(enemy()),90);
 assert.equal(model.impactArmor(enemy({mark:1})),36);
 assert.equal(model.impactArmor(enemy({slow:1})),72);
 assert.ok(Math.abs(model.impactArmor(enemy({mark:1,slow:1}))-28.8)<1e-10);
 const e=enemy({mark:1});model.hurt(e,40);assert.equal(e.hp,996);
});

test('continuous damage bypasses impact plating while shields and percentage armour still apply',()=>{
 const model=createModel();
 const e=enemy({shield:10,maxShield:10,armor:.25});
 model.hurt(e,5,true);assert.equal(e.shield,5);assert.equal(e.hp,1000);
 model.hurt(e,9,true);assert.equal(e.shield,0);assert.equal(e.hp,997);
});

test('new spawn traits are physical snapshots and missing legacy impact plating means zero',()=>{
 const model=createModel();
 for(let level=0;level<7;level++){
  model.set({level});model.begin();model.spawn();
  const e=model.state().g.enemies[0];
  assert.equal(e.impactArmor,level<3?0:90);
 }
 const legacy=enemy({armor:0,shield:0});delete legacy.impactArmor;
 model.hurt(legacy,5);assert.equal(legacy.hp,995);
});

test('every legal zero-upgrade starting army at the Bastion has zero damaging impacts',()=>{
 const model=createModel();model.set({runHearts:2});model.startLevel(3);
 const start=model.state();
 assert.equal(start.g.money,215);assert.deepEqual(start.g.perks,[]);
 const options=[];
 model.catalogue().heroes.forEach((hero,type)=>{
  let cost=hero.c;
  for(let lvl=1;lvl<=3;lvl++){
   if(lvl>1)cost+=hero.up[lvl-2];
   if(cost<=215)options.push({type,lvl,cost});
  }
 });
 let armies=0;
 function examine(army){
  if(!army.length)return;
  armies++;
  // Grant every potential target freezing for the full shot whenever any Jordan
  // is affordable. This overestimates that army's support, independently of range.
  const freezing=army.some(t=>t.type===3);
  for(const tower of army){
   for(const kind of [{},{fast:true},{tank:true},{boss:true},{air:true}]){
    model.set({level:3,metaLevels:[0,0,0,0,0]});
    const p=model.position(1),targets=[0,1,2].map(()=>enemy({...p,...kind,slow:freezing?1:0}));
    model.setGame({wave:1,active:true,enemies:targets,
     towers:{1:{type:tower.type,lvl:tower.lvl,invested:tower.cost,cd:0,fresh:false}}});
    model.attack(1,1/60);
    const state=model.state();
    assert.ok(state.g.towers[1].cd>0,'the real attack must have fired');
    assert.ok(state.g.fx.length>0,'the real attack feedback must have been created');
    assert.ok(state.g.enemies.every(e=>e.hp===1000),`damaging zero-meta army: ${JSON.stringify(army)}`);
   }
  }
 }
 function enumerate(index,budget,army){
  if(index===options.length){examine(army);return;}
  const option=options[index];
  for(let count=0;count*option.cost<=budget;count++){
   enumerate(index+1,budget-count*option.cost,army.concat(Array(count).fill(option)));
  }
 }
 enumerate(0,215,[]);assert.ok(armies>10);
 // No army can obtain kill income. There are more entrants than the 15 lives,
 // so arbitrary placement or arbitrarily long paths cannot turn zero damage into a win.
 model.set({level:3});model.begin();assert.ok(model.state().g.total>15);
});

test('secondary and delayed impacts pay plating separately while fire damage continues through it',()=>{
 const model=createModel();model.set({level:3,metaLevels:[0,0,0,0,0]});
 const p=model.position(1);
 model.setGame({wave:1,active:true,spawned:18,total:18,clock:999,
  enemies:[enemy({...p}),enemy({...p})],
  towers:{1:{type:2,lvl:1,invested:155,cd:0,fresh:false}}});
 model.attack(1,1/60);
 assert.ok(model.state().g.enemies.every(e=>e.hp===1000));
 model.setGame({towers:{},delayed:[{x:p.x,y:p.y,kind:'meteor',wait:0,r:1,dmg:85,air:false}],
  zones:[{kind:'fire',x:p.x,y:p.y,r:1,life:2,age:0,dps:60,power:.28,air:false}]});
 model.step(1/60);
 assert.ok(model.state().g.enemies.every(e=>e.hp===999));
});

test('a legal zero-meta army actually loses the first Bastion wave without kill rewards',()=>{
 const model=createModel();model.set({level:3});
 const rows=model.catalogue().maps[3].rows.join('');
 for(let i=0;i<rows.length;i++)if(rows[i]==='.')model.buy(i,0);
 assert.equal(model.begin(),true);
 let frames=0;
 while(model.state().g.active&&frames<18000){model.step(1/60);frames++;}
 const state=model.state();assert.ok(frames<18000);
 assert.equal(state.g.life,0);assert.equal(state.g.ended,true);assert.equal(state.g.killed,0);
 assert.equal(state.g.wave,1);assert.equal(state.g.money,215-Object.keys(state.g.towers).length*35);
});

test('v38 preserves invested costs and already spawned legacy enemies instead of rebalancing snapshots',()=>{
 const validate=createValidationModel();
 const legacy=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/save-v38-air-boss.json')));
 const originalEnemies=JSON.parse(JSON.stringify(legacy.g.enemies));
 const costs=Object.fromEntries(Object.entries(legacy.g.towers).map(([cell,t])=>[cell,t.invested]));
 const result=validate(legacy);assert.equal(result.ok,true,result.error);
 assert.deepEqual(result.data.g.enemies,originalEnemies);
 assert.deepEqual(Object.fromEntries(Object.entries(result.data.g.towers).map(([cell,t])=>[cell,t.invested])),costs);
 assert.ok(result.data.g.enemies.every(e=>!Object.hasOwn(e,'impactArmor')));
 const model=createModel();model.set({level:3});model.begin();model.spawn();
 const current={...legacy,level:3,g:model.state().g,buildCheckpoint:null};
 const currentResult=validate(current);assert.equal(currentResult.ok,true,currentResult.error);
 assert.equal(currentResult.data.g.enemies[0].impactArmor,90);
});
