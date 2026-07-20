// Worker threads spawned by @rollup/plugin-terser (via vite-plugin-pwa's
// service worker build) don't reliably inherit globalThis.crypto in this
// Node build, which crashes serialize-javascript's module-level UID
// generation. Preloaded via `node --require` (in the `build` script) so it
// also runs inside those worker threads, which inherit the parent's execArgv.
if (typeof globalThis.crypto === 'undefined') {
  globalThis.crypto = require('node:crypto').webcrypto;
}
