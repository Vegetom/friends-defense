const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)];
if (scripts.length !== 1) throw new Error('Expected exactly one game script');
const script = scripts[0][1];

function uniqueSlice(start, end) {
  if (script.split(start).length !== 2 || script.split(end).length !== 2) {
    throw new Error(`Game source boundary changed: ${start} / ${end}`);
  }
  const from = script.indexOf(start), to = script.indexOf(end, from);
  if (to < from) throw new Error('Game source boundaries are out of order');
  return script.slice(from, to);
}

function oneLineFunction(name) {
  const matches = script.split('\n').filter(line => line.startsWith(`function ${name}(`));
  if (matches.length !== 1 || !matches[0].endsWith('}')) {
    throw new Error(`Expected one complete single-line function: ${name}`);
  }
  return matches[0];
}

function createModel({ prototypeSession = false } = {}) {
  const context = vm.createContext({ prototypeSession });
  const core = uniqueSlice('const D=[', '\nconst GRAPHICS=');
  const functions = ['globalWaveCleared', 'rewardStars', 'finishRun', 'resetGame', 'startLevel', 'nextLevel'].map(oneLineFunction).join('\n');
  vm.runInContext(`${core}
    let g=initial(),metaLevels=[0,0,0,0,0],stars=0,bestWave=0,completed=false;
    let runHearts=0,runEnded=false,buildCheckpoint=null,clock=0;
    let selected=-1,focus=-1,paused=false,speed=1,choices=[],notice='',shake=0;const cv={};
    let saved=0,rewards=[];const settings={effects:false};
    function saveMeta(){saved++}
    function openRunReward(reward){rewards.push(reward)}
    function playSound(){} function tickFeedback(){} function damageFeedback(){}
    function waveFeedback(){} function deathFeedback(){} function heartDropFeedback(){}
    function clearFeedback(){} function clearPreview(){} function refreshShopSkins(){}
    function buildTerrain(){} function sync(){} function draw(){} function saveProgress(){}
    function $(){return {replaceChildren(){},removeAttribute(){}}}
    ${functions}
    globalThis.api={
      set(input={}){
        configureMap(input.level??0,prototypeSession?2:0);g=initial();Object.assign(g,input.g||{});
        stars=input.stars??0;bestWave=input.bestWave??0;completed=input.completed??false;
        metaLevels=input.metaLevels??[0,0,0,0,0];runHearts=input.runHearts??0;
        hardcore=input.hardcore??false;clock=0;shake=0;
        runEnded=input.runEnded??false;buildCheckpoint=input.buildCheckpoint?JSON.parse(JSON.stringify(input.buildCheckpoint)):null;saved=0;rewards=[];
      },
      state(){return JSON.parse(JSON.stringify({level,g,stars,bestWave,completed,metaLevels,runHearts,runEnded,buildCheckpoint,saved,rewards}))},
      globalWaveCleared,rewardStars,finishRun,startLevel,nextLevel,canRetryWave,retryWave,
      setGame:input=>Object.assign(g,input),
      catalogue:()=>({heroes:D,maps:MAPS,meta:META,bonuses:B}),
      stats:cell=>stats(g,g.towers[cell]),
      buy:(cell,type)=>buy(g,cell,type),upgrade:cell=>upgrade(g,cell),remove:cell=>remove(g,cell),
      bonusOptions:()=>bonusOptions(g),choose:id=>choose(g,bonusOptions(g).find(b=>b.id===id)),
      relocate:(from,to)=>relocate(g,from,to), threats:wave=>waveThreats(g,wave),
      begin:()=>begin(g),step:dt=>{clock+=dt;step(g,dt)},
      spawn:()=>spawn(g),attack:(cell,dt)=>attack(g,cell,g.towers[cell],dt),hurt,
      wavePay:wave=>wavePay(g,wave),path:()=>path(g.towers),
      position:cell=>pos(cell),impactArmor:effectiveImpactArmor,
    };`, context, { filename: 'actual-game-model.js', timeout: 2000 });
  return {
    ...context.api,
    state: () => JSON.parse(JSON.stringify(context.api.state())),
  };
}

function createValidationModel({ prototypeSession = false } = {}) {
  const context = vm.createContext({ prototypeSession });
  const core = uniqueSlice('const D=[', '\nconst GRAPHICS=');
  const validation = uniqueSlice('// Save validation is pure:', '// End pure save validation.');
  vm.runInContext(`${core}\n${validation}\nglobalThis.validate=validateSaveData;globalThis.recover=getRecoverableProfile;`, context,
    { filename: 'actual-save-validation.js', timeout: 2000 });
  const validate = input => JSON.parse(JSON.stringify(context.validate(input)));
  validate.recover = input => JSON.parse(JSON.stringify(context.recover(input)));
  return validate;
}

function createStorageModel(snapshot, raw=JSON.stringify(snapshot)) {
  const values=new Map([['friends-defense-save-v38',raw]]),writes=[];
  let failure=null;
  const elements={};
  const context=vm.createContext({
    seedJson:JSON.stringify(snapshot),
    $:id=>elements[id]||(elements[id]={hidden:false,disabled:false,checked:false,textContent:''}),
    localStorage:{
      getItem(key){if(failure==='get')throw new Error('Synthetic read failure');return values.get(key)??null;},
      setItem(key,value){writes.push(key);if(failure==='set')throw new Error('Synthetic quota failure');values.set(key,value);},
    },
  });
  const core=uniqueSlice('const D=[','\nconst GRAPHICS=');
  const validation=uniqueSlice('// Save validation is pure:','// End pure save validation.');
  const storage=uniqueSlice('let saveProblem=','function hideMenu()');
  vm.runInContext(`${core}\n${validation}
    const seed=JSON.parse(seedJson),SAVE_KEY='friends-defense-save-v38';
    let bastionUnlocked=seed.bastionUnlocked??false,finaleUnlocked=seed.finaleUnlocked??false;
    let menuOpen=false,g=seed.g,metaLevels=seed.metaLevels,stars=seed.stars,bestWave=seed.bestWave;
    let completed=seed.completed,runHearts=seed.runHearts,runVariation=seed.runVariation,runEnded=seed.runEnded;
    let metaLastEarned=seed.metaLastEarned,rewardOpen=seed.rewardOpen,buildCheckpoint=seed.buildCheckpoint;
    let clock=seed.clock,notice=seed.notice,workshopOpen=seed.workshopOpen,paused=seed.paused,speed=seed.speed??1;
    hardcore=seed.hardcore;level=seed.level;
    ${uniqueSlice('const cloneData=', '\n// Save validation is pure:')}
    ${oneLineFunction('buildSaveData')}
    ${storage}
    globalThis.api={save:saveProgress,validation:()=>validateSaveData(buildSaveData()),damage:()=>{g.towers=null},speed:value=>{speed=value}};
  `,context,{filename:'actual-save-storage.js',timeout:2000});
  return {
    ...context.api,
    failure:value=>{failure=value;},
    raw:()=>values.get('friends-defense-save-v38'),
    writes:()=>[...writes],
    message:()=>elements.saveStatusMessage.textContent,
    exportVisible:()=>!elements.exportProgress.hidden,
  };
}

module.exports = { createModel, createValidationModel, createStorageModel, script };
