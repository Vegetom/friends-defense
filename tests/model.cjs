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

function createModel() {
  const context = vm.createContext({});
  const core = uniqueSlice('const D=[', '\nconst GRAPHICS=');
  const functions = ['globalWaveCleared', 'rewardStars', 'finishRun'].map(oneLineFunction).join('\n');
  vm.runInContext(`${core}
    let g=initial(),metaLevels=[0,0,0,0,0],stars=0,bestWave=0,completed=false;
    let runHearts=0,runEnded=false,buildCheckpoint=null,clock=0;
    let saved=0,rewards=[];const settings={effects:false};
    function saveMeta(){saved++}
    function openRunReward(reward){rewards.push(reward)}
    function playSound(){} function tickFeedback(){} function damageFeedback(){}
    function waveFeedback(){} function deathFeedback(){} function heartDropFeedback(){}
    ${functions}
    globalThis.api={
      set(input={}){
        configureMap(input.level??0);g=initial();Object.assign(g,input.g||{});
        stars=input.stars??0;bestWave=input.bestWave??0;completed=input.completed??false;
        metaLevels=input.metaLevels??[0,0,0,0,0];runHearts=input.runHearts??0;
        runEnded=input.runEnded??false;saved=0;rewards=[];
      },
      state(){return JSON.parse(JSON.stringify({level,g,stars,bestWave,completed,metaLevels,runHearts,runEnded,saved,rewards}))},
      globalWaveCleared,rewardStars,finishRun,
      buy:(cell,type)=>buy(g,cell,type),begin:()=>begin(g),step:dt=>step(g,dt)
    };`, context, { filename: 'actual-game-model.js', timeout: 2000 });
  return {
    ...context.api,
    state: () => JSON.parse(JSON.stringify(context.api.state())),
  };
}

module.exports = { createModel, script };
