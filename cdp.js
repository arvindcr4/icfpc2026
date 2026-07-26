#!/usr/bin/env node
/**
 * Minimal raw-CDP driver for the CloakBrowser on :9222.
 * The chrome-devtools MCP dropped its connection, but the browser is still alive,
 * so we speak CDP directly. Node 22 has a global WebSocket — no dependencies.
 *
 *   node cdp.js list
 *   node cdp.js eval <urlMatch> "<js expression>"
 *   node cdp.js newtab <url>
 *   node cdp.js ask <urlMatch> <promptFile>     # type into the ChatGPT composer and send
 */
const HOST = 'http://127.0.0.1:9222';

async function targets() {
  return (await (await fetch(HOST + '/json/list')).json()).filter(t => t.type === 'page');
}

function connect(ws) {
  return new Promise((res, rej) => {
    const s = new WebSocket(ws);
    s.onopen = () => res(s);
    s.onerror = e => rej(new Error('ws: ' + e.message));
  });
}

let _id = 0;
function send(sock, method, params = {}) {
  const id = ++_id;
  return new Promise((res, rej) => {
    const to = setTimeout(() => rej(new Error('timeout ' + method)), 120000);
    const h = ev => {
      const m = JSON.parse(ev.data);
      if (m.id !== id) return;
      clearTimeout(to); sock.removeEventListener('message', h);
      m.error ? rej(new Error(method + ': ' + JSON.stringify(m.error))) : res(m.result);
    };
    sock.addEventListener('message', h);
    sock.send(JSON.stringify({ id, method, params }));
  });
}

async function pick(match) {
  const ts = await targets();
  const t = ts.find(t => t.id === match) ||
            ts.find(t => (t.url || '').includes(match) || (t.title || '').includes(match));
  if (!t) throw new Error('no page matching ' + match);
  return t;
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function evalOn(sock, expr, awaitPromise = true) {
  const r = await send(sock, 'Runtime.evaluate', {
    expression: expr, returnByValue: true, awaitPromise,
  });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'eval failed');
  return r.result.value;
}

async function main() {
  const [cmd, a, b] = process.argv.slice(2);
  if (cmd === 'list') {
    for (const t of await targets()) console.log(t.id, '|', (t.title || '').slice(0, 50), '|', t.url.slice(0, 90));
    return;
  }
  if (cmd === 'newtab') {
    const r = await fetch(`${HOST}/json/new?${encodeURIComponent(a)}`, { method: 'PUT' });
    console.log((await r.json()).id);
    return;
  }
  const t = await pick(a);
  const sock = await connect(t.webSocketDebuggerUrl);
  await send(sock, 'Runtime.enable');
  await send(sock, 'Page.enable');

  if (cmd === 'eval') {
    console.log(JSON.stringify(await evalOn(sock, b), null, 1));
  } else if (cmd === 'ask') {
    const fs = require('fs');
    const text = fs.readFileSync(b, 'utf8');
    // focus the composer
    await evalOn(sock, `(() => { const e = document.querySelector('#prompt-textarea') ||
        document.querySelector('div[contenteditable="true"]'); if(!e) return 'no composer';
        e.focus(); return 'focused'; })()`, false);
    await sleep(400);
    // Input.insertText produces a trusted-looking input event; plain .value/.textContent
    // assignment is ignored by ProseMirror composers.
    await send(sock, 'Input.insertText', { text });
    await sleep(900);
    const got = await evalOn(sock, `(() => { const e = document.querySelector('#prompt-textarea') ||
        document.querySelector('div[contenteditable="true"]'); return e ? (e.innerText||e.value||'').length : -1; })()`, false);
    console.log('composer chars:', got, 'of', text.length);
    if (got < 50) { console.log('INSERT FAILED'); process.exit(2); }
    for (const type of ['keyDown', 'keyUp']) {
      await send(sock, 'Input.dispatchKeyEvent', {
        type, key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13,
      });
    }
    await sleep(1500);
    console.log('sent; url now:', await evalOn(sock, 'location.href', false));
  }
  sock.close();
}
main().catch(e => { console.error('ERR', e.message); process.exit(1); });
