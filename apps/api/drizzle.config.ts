import { defineConfig } from 'drizzle-kit';

// Drizzle owns the schema and the migrations: `drizzle-kit generate` → review the SQL → apply
// (`pnpm migrate`). Never `db:push`.
export default defineConfig({
  schema: './src/schema/index.ts',
  out: './drizzle',
  dialect: 'postgresql',
  // `?? ''` is intentional, not a silent fallback: `drizzle-kit generate` (how migrations are
  // authored) needs no live connection, so it must not fail when DATABASE_URL is unset. The
  // commands that DO connect fail loudly on an empty URL.
  dbCredentials: { url: process.env.DATABASE_URL ?? '' },
});
