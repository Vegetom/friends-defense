#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),{runCampaign,COMPOSITIONS}=require('./campaign.cjs');
const args=process.argv.slice(2);const arg=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1]};
const profiles={zero:[0,0,0,0,0],few:[1,1,0,0,0],intermediate:[2,2,1,1,1],max:[3,3,3,3,3]};
const sourcePath=arg('--source',null),html=sourcePath?fs.readFileSync(sourcePath,'utf8'):null;
const ref=arg('--ref',null),out=arg('--out',null),dt=+arg('--dt','0.03333333333333333');
const hardcore=args.includes('--hardcore');
const prototypeSession=args.includes('--prototype'),startAt=Number(arg('--start-terrain','1'))-1;
if(![0,1,3].includes(startAt))throw Error('Supported starts are terrains 1, 2 and 4');
const budgetPolicy=arg('--budget','auto');
if(!['auto','supplies','contract'].includes(budgetPolicy))throw Error('Invalid budget policy');
const doctrinePolicy=arg('--doctrine','auto');
if(!['auto','escadron','embuscade','sansDoctrine'].includes(doctrinePolicy))throw Error('Invalid doctrine policy');
const variation=Number(arg('--variation','0')),perkPolicy=arg('--perks','classic');
if(![0,1,2].includes(variation)||!['classic','rotating'].includes(perkPolicy))throw Error('Invalid variation or perk policy');
const chosenProfiles=arg('--profiles',Object.keys(profiles).join(',')).split(','),compositions=arg('--compositions',Object.keys(COMPOSITIONS).join(',')).split(','),policies=arg('--policies','balanced').split(','),seeds=arg('--seeds','1').split(',').map(Number);
const runs=[];
for(const name of chosenProfiles)for(const composition of compositions)for(const policy of policies)for(const seed of seeds){
 if(!profiles[name])throw Error(`Unknown profile ${name}`);
 const result=runCampaign({ref,html,profile:profiles[name],composition,policy,seed,dt,hardcore,variation,perkPolicy,doctrinePolicy,budgetPolicy,prototypeSession,startAt,trace:true});result.profileName=name;runs.push(result);
 process.stderr.write(`${name}/${composition}/${policy}/${seed}: ${result.win?'WIN':`N${result.stop.level}V${result.stop.wave}`} cleared=${result.cleared} seconds=${result.seconds.toFixed(1)}\n`);
 if(out)fs.writeFileSync(out,JSON.stringify({method:'Actual game core, legal purchases, actual checkpoints/retries/transitions; seeded tie-breaking only, no battle-state or Z injection.',runs},null,2)+'\n');
}
if(!out)process.stdout.write(JSON.stringify({runs},null,2)+'\n');
