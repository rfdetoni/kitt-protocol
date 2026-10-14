import assert from 'node:assert/strict';
import {readFileSync, readdirSync} from 'node:fs';
import {join} from 'node:path';
import {parseKAP2, encodeKAP2, KAP2Error} from '../.test-sdk/kap2.js';

import {KAP_VERSION_HEADER, negotiateKAPVersion, KAPNegotiationError} from '../.test-sdk/kap-version.js';
assert.equal(KAP_VERSION_HEADER, 'X-Kitt-KAP');
assert.equal(negotiateKAPVersion(undefined), 'KAP/2');
assert.equal(negotiateKAPVersion('KAP/2'), 'KAP/2');
for (const bad of ['KAP/1', 'KAP/3', 'KAP/2,KAP/1', ' KAP/2', '']) assert.throws(() => negotiateKAPVersion(bad), KAPNegotiationError);
const root = 'fixtures/kap2';
function entries(dir) { return readdirSync(join(root,dir)).filter(name=>name.endsWith('.k2')).sort(); }
let checked = 0;
for (const name of entries('valid')) {
  const base = join(root,'valid', name);
  const raw = readFileSync(base,'utf8'), expected = JSON.parse(readFileSync(base.slice(0,-3)+'.json','utf8'));
  assert.deepEqual(JSON.parse(JSON.stringify(parseKAP2(raw).content)), expected, name);
  checked++;
}
for (const name of entries('invalid')) {
  const base = join(root,'invalid',name);
  const raw = readFileSync(base,'utf8'), code = readFileSync(base.slice(0,-3)+'.err','utf8').trim();
  assert.throws(() => parseKAP2(raw), e => e instanceof KAP2Error && e.code === code, name);
  checked++;
}
for (const [symbol, action] of [['W','request_workspace'],['Q','request_tools']]) {
  assert.equal(parseKAP2('K2 '+symbol+'\nK2/END').action,action);
  assert.throws(()=>parseKAP2('K2 '+symbol+'\nignored\nK2/END'), {code:'E_BODY_NOT_ALLOWED'});
}
const schema={type:'object',properties:{version:{type:'string'},active:{type:'string'}}};
assert.deepEqual(JSON.parse(JSON.stringify(parseKAP2('K2 F\nversion: 1.10\nactive: true\nK2/END',{schema}).content)),{version:'1.10',active:'true'});
const encoderCases=[
  {title:'Olá', empty:{}, rows:[{id:'a-b',valid:true}], contents:'first\nK2/END\nlast'},
  {flags:['true','001'], revision:10},
];
let state=3202;
for(let i=0;i<100;i++){
  state=(Math.imul(state,1664525)+1013904223)>>>0;
  encoderCases.push({revision:state%999,flags:['true',String(state%10)],valid:!!(state&1)});
}
for(const item of encoderCases)assert.deepEqual(JSON.parse(JSON.stringify(parseKAP2(encodeKAP2(item)).content)),item);
const rows=Array(1024).fill('  - ok').join('\n');
assert.equal(parseKAP2('K2 F\nitems[1024]:\n'+rows+'\nK2/END').content.items.length,1024);
assert.throws(()=>parseKAP2('K2 F\nitems[1025]:\nK2/END'),{code:'E_ARRAY_SIZE'});
const prefix='K2 F\nvalue: ',tail='\nK2/END';
const exact=prefix+'x'.repeat(65536-prefix.length-tail.length)+tail;
assert.equal(new TextEncoder().encode(exact).length,65536);
assert.equal(parseKAP2(exact).content.value.length,65536-prefix.length-tail.length);
assert.throws(()=>parseKAP2(exact.replace('\nK2/END','x\nK2/END')),{code:'E_SIZE'});
console.log('KAP/2 TS fixtures: '+checked+' cases, seeded encoder round trips and limits OK');
