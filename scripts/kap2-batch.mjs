import {readFileSync} from 'node:fs';
import {parseKAP2} from '../.test-sdk/kap2.js';

const input = JSON.parse(readFileSync(0, 'utf8'));
const result = input.map(raw => {
  try { return {ok:true, frame:parseKAP2(raw)}; }
  catch(error) { return {ok:false,code:error?.code ?? 'E_UNKNOWN'}; }
});
process.stdout.write(JSON.stringify(result));
