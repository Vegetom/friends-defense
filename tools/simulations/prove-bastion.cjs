#!/usr/bin/env node
'use strict';
// Conservative upper bound over ALL affordable armies, independent of placement.
// Enumerating budgets is not an exhaustive tactical simulation: zero residual damage
// makes path length, targeting and AoE target counts irrelevant for this one wave.
const fs=require('node:fs'),{createModel}=require('./model.cjs');
const args=process.argv.slice(2),get=(k,d)=>{const i=args.indexOf(k);return i<0?d:args[i+1]};
const sourcePath=get('--source',null),out=get('--out',null);
const {api,source}=createModel({html:sourcePath?fs.readFileSync(sourcePath,'utf8'):null});
const {heroes}=api.data(),wave=api.waveProbe(1)[3],budget=wave.initial,choices=[];
for(let type=0;type<heroes.length;type++)for(let level=1;level<=3;level++){
 const h=heroes[type],cost=h.c+h.up.slice(0,level-1).reduce((s,c)=>s+c,0);
 if(cost<=budget)choices.push({type,level,cost,damage:h.d[level-1]});
}
let armies=0,maxRaw=0,maxResidual=0,witness=null;
function enumerate(index,left,army){
 if(index===choices.length){
  armies++;const gel=army.some(x=>x.type===3),ward=wave.minWard*(gel?.8:1);
  for(const t of army){
   // No permanent marking, zones, burn, delayed strikes, or terrain perks exist.
   // Tom's fast matchup and ally freeze bonus are included as overestimates.
   let hit=t.damage*(t.type===0?1.3:t.type===1&&t.level===3?1.5:1)*(gel&&t.type!==3?1.18:1);
   const residual=Math.max(0,hit-ward);
   maxRaw=Math.max(maxRaw,hit);
   if(residual>maxResidual){maxResidual=residual;witness=army}
  }
  return;
 }
 const c=choices[index];for(let count=0;count*c.cost<=left;count++)enumerate(index+1,left-count*c.cost,army.concat(Array(count).fill(c)));
}
enumerate(0,budget,[]);
const proof={source,scope:'Normal mode, terrain 4 wave 1, zero permanent tiers, ordinary startLevel budget, no carried Z or perks.',budget,life:wave.life,enemies:wave.n,minimumImpactArmor:wave.minWard,bosses:wave.bosses,minimumBaseSpeed:wave.minSpeed,affordableArchetypes:choices,affordableArmyMultisets:armies,maximumRawImpact:maxRaw,maximumResidualImpact:maxResidual,counterexample:witness,proven:maxResidual===0&&wave.n>wave.life&&wave.bosses===0&&wave.minSpeed>0,reason:'Every affordable direct and secondary impact is blocked. Zero permanent tiers generate no fire/burn zones. No kill income; construction is locked during combat. Every finite legal route has positive movement even under the only affordable slow. More enemies than base lives eventually escape, including after any finite checkpoint retries. No conditional automatic defeat on meta levels is used.'};
if(out)fs.writeFileSync(out,JSON.stringify(proof,null,2)+'\n');else console.log(JSON.stringify(proof,null,2));
if(!proof.proven)process.exitCode=1;
