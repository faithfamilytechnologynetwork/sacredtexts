import { fileURLToPath } from 'node:url';
import { drizzle } from 'drizzle-orm/node-postgres';
import { migrate } from 'drizzle-orm/node-postgres/migrator';
import { Pool } from 'pg';

/**
 * Apply the committed, reviewed migrations from `drizzle/` to the database in `DATABASE_URL`. Run as
 * Railway's `preDeployCommand` (inside Railway, where the internal Postgres host is reachable) and
 * usable locally. Idempotent — drizzle records applied migrations, so re-runs are no-ops. This is the
 * deliberate "apply" step (generate → review → apply); it only ever runs the committed SQL files and
 * never diffs the live schema the way `db:push` does.
 */
const databaseUrl = process.env.DATABASE_URL;
if (!databaseUrl) {
  console.error('DATABASE_URL is required to run migrations');
  process.exit(1);
}

// Resolved from this file, not the working directory, so the hosted image's pre-deploy step can run
// it from anywhere.
const migrationsFolder = fileURLToPath(new URL('../drizzle', import.meta.url));

const pool = new Pool({ connectionString: databaseUrl });
const db = drizzle(pool);
await migrate(db, { migrationsFolder });
await pool.end();
console.log('migrations applied');
