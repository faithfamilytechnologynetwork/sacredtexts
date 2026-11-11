import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    globals: true,
    // Each file's first test boots PGlite and applies the migrations, which takes seconds on a busy
    // machine (the files run in parallel, and server.test.ts spawns real server processes), so the
    // 5 s default timed out on a cold run.
    testTimeout: 20_000,
  },
});
