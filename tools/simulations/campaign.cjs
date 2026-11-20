'use strict';
const {createModel}=require('./model.cjs');
const COMPOSITIONS={mixed:[1,1,1,.85,1],air:[1.4,1.2,.65,.7,1],sniper:[.45,2,.65,.8,1],zone:[.45,.85,1.8,1.1,1.2],'tom-only':[1,0,0,0,0],'sniper-only':[0,1,0,0,0],'zone-only':[0,0,1,0,0]};
function hash(seed,text){let n=seed>>>0;for(let i=0;i<text.length;i++)n=Math.imul(n^text.charCodeAt(i),16777619)>>>0;return n/4294967296}
function plan(api,{composition='mixed',policy='balanced',seed=1}={},actions){
 const weights=COMPOSITIONS[composition];if(!weights)throw Error('Unknown composition');
 let buys=0;
 for(let i=0;i<120;i++){
  const state=api.view(),next=state.wave+1,counts=[0,0,0,0,0];for(const t of Object.values(state.towers))counts[t.type]++;
  const kind=api.airKind(next),airWeight=kind==='air'?1:kind==='mixed'?.5:.14;
  const opts=api.options(true);let best=null,score=-Infinity;
  const invested=[0,0,0,0,0];for(const t of Object.values(state.towers))invested[t.type]+=t.invested;
  const totalInvested=invested.reduce((a,b)=>a+b,0)||1;
  const shares=composition==='sniper'?[.10,.55,.10,.10,.15]:composition==='zone'?[.10,.15,.45,.10,.20]:composition==='air'?[.40,.25,.10,.10,.15]:[.20,.25,.20,.10,.25];
  let goal=null;
  if(policy!=='greedy'&&weights[3]>0&&state.wave>=3&&counts[3]===0&&Object.keys(state.towers).length>=3)goal=opts.filter(o=>o.kind==='buy'&&o.type===3).sort((a,b)=>(b.ground+b.air)-(a.ground+a.air))[0];
  const focusType=composition==='sniper'||composition==='sniper-only'?1:composition==='zone'||composition==='zone-only'?2:composition==='air'||composition==='tom-only'?0:1;
  const focusStart=policy==='upgrade'?4:policy==='maze'?8:6;
  if(policy!=='greedy'&&!goal&&state.wave>=focusStart&&!Object.values(state.towers).some(t=>t.type===focusType&&t.lvl===3))goal=opts.filter(o=>o.kind==='upgrade'&&o.type===focusType).sort((a,b)=>(b.ground+b.air)-(a.ground+a.air))[0];
  if(policy!=='greedy'&&!goal&&composition==='mixed'&&state.wave>=7&&counts[4]===0)goal=opts.filter(o=>o.kind==='buy'&&o.type===4).sort((a,b)=>(b.ground+b.air)-(a.ground+a.air))[0];
  if(goal){
   if(goal.cost>state.money){actions.push({level:state.level+1,beforeWave:next,action:'reserve',type:goal.type,needed:goal.cost,available:state.money});break}
   const ok=goal.kind==='buy'?api.buy(goal.cell,goal.type):api.upgrade(goal.cell);if(!ok)throw Error('Illegal strategic purchase');
   actions.push({level:state.level+1,beforeWave:next,action:goal.kind,cell:goal.cell,type:goal.type,cost:goal.cost});buys++;continue;
  }
  for(const o of opts){
   if(o.cost>state.money||weights[o.type]===0)continue;
   let raw=o.ground*(1-airWeight)+o.air*airWeight*1.45+Math.max(0,o.maze)*.3*(1-airWeight);
   let value=raw/o.cost*weights[o.type]*(1+Math.max(-.6,shares[o.type]-invested[o.type]/totalInvested)*2);
   if(o.type===3&&counts[3]===0&&Object.keys(state.towers).length>=2)value*=2;
   if(o.type===3&&counts[3]>0)value*=.55;
   if(o.kind==='upgrade')value*=policy==='upgrade'?1.45:policy==='maze'?.75:1.03;
   if(policy==='maze'&&o.kind==='buy')value*=1.1;
   value*=.95+.1*hash(seed,`${state.level}:${state.wave}:${o.kind}:${o.cell}:${o.type}`);
   if(value>score){score=value;best=o}
  }
  if(!best)break;
  const ok=best.kind==='buy'?api.buy(best.cell,best.type):api.upgrade(best.cell);
  if(!ok)throw Error('Planner proposed illegal purchase');
  actions.push({level:state.level+1,beforeWave:next,action:best.kind,cell:best.cell,type:best.type,cost:best.cost});buys++;
 }
 return buys;
}
function bonus(api,composition,seed,perkPolicy,doctrinePolicy,budgetPolicy){
 const list=api.bonuses(),preferred=composition==='tom-only'?['tom','eco10','rempart']:composition==='sniper-only'?['raph','eco10','rempart']:composition==='zone-only'?['eco5','ylvine','rempart']:composition==='sniper'?['raph','eco5','jordan','eco10','rempart','poy','discount']:composition==='zone'?['eco5','tom','ylvine','jordan','rempart','poy','discount']:composition==='air'?['tom','eco5','jordan','ylvine','rempart','poy','discount']:['tom','eco5','jordan','eco10','rempart','poy','discount'];
 if(list.some(b=>b.id==='sansDoctrine'))return doctrinePolicy==='auto'?(composition==='zone'?'embuscade':'escadron'):doctrinePolicy;
 if(list.some(b=>b.id==='supplies'))return budgetPolicy==='auto'?(composition==='air'?'supplies':'contract'):budgetPolicy;
 if(list.some(b=>b.id==='rangePlan')){
  if(composition==='air'&&list.some(b=>b.id==='airBeacon'))return 'airBeacon';
  if(composition==='zone'){
   if(list.some(b=>b.id==='ylvine'))return 'ylvine';
   if(list.some(b=>b.id==='longWinter'))return 'longWinter';
  }
  return 'rangePlan';
 }
 if(list.some(b=>b.id==='assaultPlan'))return api.view().life<=5&&list.some(b=>b.id==='repairPlan')?'repairPlan':'assaultPlan';
 if(perkPolicy==='rotating'){
  const rotating=list.find(b=>['airBeacon','shieldBreach','longWinter'].includes(b.id));
  if(rotating)return rotating.id;
 }
 return list.sort((a,b)=>{const ai=preferred.indexOf(a.id),bi=preferred.indexOf(b.id);return (ai<0?99:ai)-(bi<0?99:bi)||hash(seed,a.id)-hash(seed,b.id)})[0]?.id;
}
function runCampaign({ref=null,html=null,profile=[0,0,0,0,0],composition='mixed',policy='balanced',seed=1,dt=1/30,trace=true,hardcore=false,variation=0,perkPolicy='classic',doctrinePolicy='auto',budgetPolicy='auto'}={}){
 const {api,source}=createModel({ref,html});api.start(profile,hardcore,variation);
 const actions=[],waves=[],transitions=[];let totalSeconds=0,retriesUsed=0,attempt=0;
 for(let guard=0;guard<250;guard++){
  let state=api.view();
  if(state.ended){
   if(state.life>0){
    if(state.level===6){const reward=api.finish(true);return {source,profile,composition,policy,seed,dt,hardcore,variation,perkPolicy,doctrinePolicy,budgetPolicy,win:true,cleared:70,stop:{level:7,wave:10,reason:'campaign-win'},seconds:totalSeconds,retriesUsed,reward,actions:trace?actions:undefined,waves,transitions}}
    const old=state;if(!api.next())throw Error('Actual nextLevel refused a real win');const fresh=api.view();transitions.push({from:old.level+1,to:fresh.level+1,hearts:old.retries,doctrine:fresh.doctrine,money:fresh.money,life:fresh.life});attempt=0;continue;
   }
   if(api.canRetry()){if(!api.retry())throw Error('Actual retry refused');retriesUsed++;attempt++;continue}
   const reward=api.finish(false);return {source,profile,composition,policy,seed,dt,hardcore,variation,perkPolicy,doctrinePolicy,budgetPolicy,win:false,cleared:state.n,stop:{level:state.level+1,wave:state.wave,reason:'life-zero'},seconds:totalSeconds,retriesUsed,reward,actions:trace?actions:undefined,waves,transitions};
  }
  if(state.bonus){const id=bonus(api,composition,seed,perkPolicy,doctrinePolicy,budgetPolicy);if(!id||!api.choose(id))throw Error('Illegal perk selection');actions.push({level:state.level+1,afterWave:state.wave,action:'choose',id});state=api.view()}
  plan(api,{composition,policy,seed:seed+attempt*101},actions);const before=api.view();
  if(!api.begin())throw Error('Actual begin refused');
  const stepped=api.advance(dt,Math.ceil(600/dt));if(stepped.active)throw Error('Simulation exceeded 600 game seconds in a wave');
  const after=api.view(),elapsed=stepped.frames*dt;totalSeconds+=elapsed;
  waves.push({level:after.level+1,wave:after.wave,attempt,finished:!after.ended||after.life>0,lifeBefore:before.life,lifeAfter:after.life,moneyBefore:before.money,moneyAfter:after.money,killed:after.killed,escaped:after.escaped,hearts:after.retries,route:before.routeLength,army:Object.values(before.towers).map(t=>[t.type,t.lvl]),seconds:elapsed});
 }
 throw Error('Controller guard reached without a real terminal state');
}
module.exports={runCampaign,plan,COMPOSITIONS};
