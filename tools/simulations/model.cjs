'use strict';
// Headless adapter: combat, purchases, checkpoints and transitions come from the game.
// The adapter removes only DOM/Canvas/audio side effects. It never grants Z or a win.
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const {execFileSync}=require('node:child_process');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'../..');
function readSource(ref){if(!ref)return fs.readFileSync(path.join(ROOT,'index.html'),'utf8');try{return execFileSync('git',['show',`${ref}:index.html`],{cwd:ROOT,maxBuffer:32*1024*1024,encoding:'utf8'})}catch(error){throw Error('Cannot read Git snapshot: '+(error.code||error.status)+'. Export it with git show and pass --source instead.')}}
function createModel({ref=null,html=null}={}){
 const source=html??readSource(ref),script=[...source.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)][0]?.[1];
 if(!script)throw Error('Game script missing');
 const start=script.indexOf('const D=['),end=script.indexOf('\nconst GRAPHICS=');
 if(start<0||end<start)throw Error('Game core markers changed');
 const core=script.slice(start,end),one=name=>{const lines=script.split('\n').filter(l=>l.startsWith(`function ${name}(`));if(lines.length!==1)throw Error(`Expected actual ${name}`);return lines[0]};
 const functions=['resetGame','startLevel','nextLevel','globalWaveCleared','rewardStars','finishRun'].map(one).join('\n');
 const context=vm.createContext({});
 vm.runInContext(`${core}
 let g=initial(),metaLevels=[0,0,0,0,0],stars=0,bestWave=0,completed=false,runHearts=0,runEnded=false,buildCheckpoint=null;
 let runVariation=0,clock=0,selected=-1,focus=-1,paused=false,speed=1,choices=[],notice='',banner=null,shake=0;
 const cv={},settings={effects:false};let finalReward=null;
 const node={replaceChildren(){},removeAttribute(){},className:'',hidden:false};const $=()=>node;
 function clearFeedback(){}function clearPreview(){}function refreshShopSkins(){}function sync(){}function draw(){}
 function saveProgress(){}function saveMeta(){}function buildTerrain(){}
 function playSound(){}function tickFeedback(){}function damageFeedback(){}function waveFeedback(){}
 function deathFeedback(){}function heartDropFeedback(){}function openRunReward(r){finalReward=r}
 ${functions}
 function cover(cell,st,route){
  const p=pos(cell),r=st.range*S;let ground=0;
  for(const i of route){const q=pos(i);if(Math.hypot(q.x-p.x,q.y-p.y)<=r)ground++;}
  const a=pos(ENTRY),b=pos(EXIT),dx=b.x-a.x,dy=b.y-a.y,len=Math.hypot(dx,dy),u=((p.x-a.x)*dx+(p.y-a.y)*dy)/len;
  const d=Math.abs((p.x-a.x)*dy-(p.y-a.y)*dx)/len,ar=r*(typeof airRange==='function'?airRange(g):AIR_RANGE);
  const half=d<ar?Math.sqrt(ar*ar-d*d):0;
  const air=half?Math.max(0,Math.min(len,u+half)-Math.max(0,u-half))/S:0;
  return {ground,air};
 }
 function power(t,st){const m=getMeta(t.type);let f=1;
  if(t.type===0)f=m>=3?2.12:m>=1?1.56:1;
  if(t.type===1)f=(m>=1?1.28:1)*(m>=2?2.25:1.55)*(m>=3?1.55:1);
  if(t.type===2)f=1.8+(m>=1?.3:0)+(m>=2?.3:0)+(m>=3?.5:0);
  if(t.type===3)f=1.25+(m>=1?.18:0)+(m>=2?.3:0)+(m>=3?.2:0);
  if(t.type===4)f=1.85+(m>=2?.35:0)+(m>=3?.5:0);
  const plate=typeof IMPACT_ARMOR==='undefined'?0:IMPACT_ARMOR[level]||0;
  if(!plate)return st.damage/st.rate*f;
  const marked=(t.type===1&&m>=1)||Object.values(g.towers).some(a=>a.type===1&&getMeta(1)>=1);
  const frozen=t.type===3||Object.values(g.towers).some(a=>a.type===3);
  const ward=plate*(marked?.4:1)*(frozen?.8:1),hit=d=>Math.max(0,d-ward);
  const damage=st.damage*(marked?(t.type===1?1.28:1.20):1)*(frozen&&t.type!==3?1.18:1);
  if(t.type===0)return (hit(damage)+(m>=1?hit(damage*.56):0)+(m>=3?hit(damage*.56):0))/st.rate;
  if(t.type===1)return (hit(damage*(m>=2?1.16:1))+(m>=2?3:2)*hit(damage*(m>=2?.9:.48)))/st.rate*(m>=3?1.55:1);
  if(t.type===2)return (hit(damage)+1.7*hit(st.damage*.65)+(m>=2?hit(st.damage*.34):0))/st.rate+(m>=1?st.damage*.12*1.5:0)+(m>=3?st.damage*.5:0);
  if(t.type===3)return hit(damage)/st.rate*1.8;
  return (hit(damage)+1.7*hit(st.damage*.75))/st.rate*(m>=2?1.35:1)*(m>=3?1.3:1);
 }
 function options(includeUnaffordable=false){
  const result=[],oldRoute=g.route,oldLength=oldRoute.length;
  const summary=Object.values(g.towers).reduce((acc,t)=>acc+power(t,stats(g,t)),0);
  for(let type=0;type<D.length;type++){
   const cost=D[type].c;if((!includeUnaffordable&&cost>g.money)||g.wave<unlockAt(type))continue;
   const t={type,lvl:1};const st=stats(g,t),p=power(t,st);
   for(let cell=0;cell<W*H;cell++)if(buildable(cell)&&!g.towers[cell]){
    const route=path({...g.towers,[cell]:t});if(!route)continue;
    const c=cover(cell,st,route);
    result.push({kind:'buy',cell,type,cost,ground:p*c.ground,air:p*c.air,maze:(route.length-oldLength)*summary,range:st.range});
   }
  }
  for(const [key,t] of Object.entries(g.towers))if(t.lvl<3){
   const cost=upgradeCost(g,t);if(!includeUnaffordable&&cost>g.money)continue;
   const cell=+key,next={...t,lvl:t.lvl+1},oldSt=stats(g,t),st=stats(g,next),c=cover(cell,st,oldRoute),oldC=cover(cell,oldSt,oldRoute);
   result.push({kind:'upgrade',cell,type:t.type,cost,ground:power(next,st)*c.ground-power(t,oldSt)*oldC.ground,air:power(next,st)*c.air-power(t,oldSt)*oldC.air,maze:0,range:st.range});
  }
  return result;
 }
 globalThis.api={
  start(profile,hard=false,variation=0){runVariation=variation;metaLevels=[...profile];hardcore=hard;stars=0;bestWave=0;completed=hard;runHearts=0;runEnded=false;finalReward=null;startLevel(0)},
  data(){return {heroes:D,maps:MAPS,meta:META,bonuses:B}},
  view(){return {level,W,H,entry:ENTRY,exit:EXIT,wave:g.wave,money:g.money,life:g.life,active:g.active,ended:g.ended,bonus:g.bonus,retries:g.retries,runHearts,killed:g.killed,escaped:g.escaped,totalKills:g.totalKills,totalLeaks:g.totalLeaks,routeLength:g.route.length-1,towers:JSON.parse(JSON.stringify(g.towers)),perks:[...g.perks],doctrine:g.doctrine,n:globalWaveCleared(),clock}},
  options,
  airKind:wave=>airKind(wave,g),
  buy(cell,type){return buy(g,cell,type)},upgrade(cell){return upgrade(g,cell)},remove(cell){return remove(g,cell)},
  bonuses(){return bonusOptions(g).map(b=>({id:b.id,type:b.type,kind:b.kind}))},
  choose(id){const b=bonusOptions(g).find(b=>b.id===id);return b?choose(g,b):false},
  begin(){return begin(g)},
  advance(dt=1/30,maxFrames=18000){let frames=0;while(g.active&&frames<maxFrames){step(g,dt);clock+=dt;frames++}return {frames,active:g.active}},
  retry(){return retryWave()},canRetry:canRetryWave,
  next(){const before=level;nextLevel();return level===before+1},
  finish(win){finishRun(win,false);return finalReward},
  waveProbe(w){const rows=[];for(let lev=0;lev<7;lev++){configureMap(lev);g=initial();g.wave=w-1;begin(g);while(g.spawned<g.total)spawn(g);rows.push({level:lev,initial:initial().money,normalHp:g.enemies[0].hp,n:g.total,route:path({}).length-1,bossHp:g.enemies.find(e=>e.boss)?.hp||0,shield:g.enemies[0].shield||0,ward:g.enemies[0].impactArmor||0,minWard:Math.min(...g.enemies.map(e=>e.impactArmor||0)),life:initial().life,bosses:g.enemies.filter(e=>e.boss).length,minSpeed:Math.min(...g.enemies.map(e=>e.vel))})}return rows}
 };
 `,context,{filename:'actual-game-simulation-adapter.js',timeout:5000});
 return {api:context.api,source:{ref:ref??'working-tree',sha256:crypto.createHash('sha256').update(source).digest('hex'),coreSha256:crypto.createHash('sha256').update(core).digest('hex')}};
}
module.exports={createModel,readSource};
