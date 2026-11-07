const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function storage() {
  const data = {};
  Object.defineProperties(data, {
    getItem: { value(key) { return this[key] ?? null; } },
    setItem: { value(key, value) { this[key] = String(value); } },
    removeItem: { value(key) { delete this[key]; } },
  });
  return data;
}

function client(fetch) {
  const redirects = [];
  const context = vm.createContext({
    fetch, Headers, atob, console,
    sessionStorage: storage(), localStorage: storage(),
    window: { location: { pathname: '/index.html', replace: url => redirects.push(url) } },
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../static/js/api-client.js'), 'utf8') + '\nthis.api = API;', context);
  return { context, redirects, api: context.api };
}

test('logout waits for server confirmation, clears credentials/cache, keeps application data', async () => {
  let finish;
  const { context, redirects, api } = client((url, options) => {
    assert.equal(url, '/api/auth/logout');
    assert.equal(options.method, 'POST');
    assert.equal(options.credentials, 'same-origin');
    assert.equal(options.headers.get('Authorization'), 'Bearer previous-token');
    return new Promise(resolve => { finish = resolve; });
  });
  for (const store of [context.localStorage, context.sessionStorage]) {
    store.setItem('uni_session_token', 'previous-token');
    store.setItem('uni_cache::auth_me', 'cached-user');
    store.setItem('uni_pasantias_data', 'existing-data');
  }
  const result = api.logout();
  assert.deepEqual(redirects, []);
  finish({ ok: true });
  assert.equal((await result).success, true);
  for (const store of [context.localStorage, context.sessionStorage]) {
    assert.equal(store.getItem('uni_session_token'), null);
    assert.equal(store.getItem('uni_cache::auth_me'), null);
    assert.equal(store.getItem('uni_pasantias_data'), 'existing-data');
  }
  assert.deepEqual(redirects, ['/login']);
});

for (const failure of ['network', 'server']) {
  test(`logout reports ${failure} failure without pretending success`, async () => {
    const { api, redirects, context } = client(async () => {
      if (failure === 'network') throw new Error('offline');
      return { ok: false, status: 500 };
    });
    context.localStorage.setItem('uni_session_token', 'retry-token');
    await assert.rejects(api.logout(), /servidor/);
    assert.deepEqual(redirects, []);
    assert.equal(context.localStorage.getItem('uni_session_token'), 'retry-token');
  });
}

test('local token cannot authenticate the user when the server is unreachable', async () => {
  const { api, context } = client(async () => { throw new Error('offline'); });
  const payload = { uid: 'user', sid: 'session', exp: Math.floor(Date.now() / 1000) + 60 };
  context.localStorage.setItem('uni_session_token', Buffer.from(JSON.stringify(payload)).toString('base64') + '.signature');
  assert.equal(await api.getCurrentUser(), null);
});
