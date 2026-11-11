# The review service (Spec 154) as one image: /api, the active sample and the built viewer with its
# runs baked in, from one origin. The build context is the REPO ROOT, because the image needs
# apps/viewer, apps/api, review/samples, and the runs/ and items/for-test/ the viewer bakes:
#
#   docker build -f apps/api/Dockerfile -t sacredtexts-review .
#
# The Railway service builds it through its `dockerfilePath` setting (apps/api/README.md § Hosting). A
# Dockerfile, not Nixpacks/Railpack: the repo root holds requirements.txt and no package.json, so
# auto-detection would build Python.
#
# Every COPY names its paths, so no node_modules or dist reaches the image, with or without a
# .dockerignore. Run evidence reaches it only as the viewer's baked dist/runs/, and only for the
# runs the viewer stage names (#159).

FROM node:24-bookworm-slim AS base
# The pnpm the lockfiles were written with (package.json packageManager). Prepared at build time, so
# nothing is downloaded when the container starts.
RUN corepack enable && corepack prepare pnpm@10.30.2 --activate
WORKDIR /app

# Stage 1: build the viewer with the Cloudflare Pages command (`build:pages`: vite build, then
# scripts/bake-runs.ts bakes runs/ into dist/runs/, reading items/for-test/ for the panel's
# questions, #157). The bake takes whatever is under runs/, so this stage copies in only the
# hosted runs.
FROM base AS viewer
COPY apps/viewer/package.json apps/viewer/pnpm-lock.yaml apps/viewer/
RUN pnpm -C apps/viewer install --frozen-lockfile
COPY apps/viewer/index.html apps/viewer/vite.config.ts apps/viewer/tsconfig.json apps/viewer/
COPY apps/viewer/public apps/viewer/public
COPY apps/viewer/vite apps/viewer/vite
COPY apps/viewer/src apps/viewer/src
COPY apps/viewer/scripts apps/viewer/scripts
# The hosted runs: one `COPY runs/<id> runs/<id>` line per run, and nothing else from runs/ (#159).
# This list is the only place the hosted set is named. To host another run, add its line here.
# A named run that is missing fails the build; no other directory under runs/, tracked or not,
# reaches the bake. (Untracked files inside a named run would, in a local build; the git archive
# deploy carries tracked files only.)
COPY runs/facct-2026-11-03 runs/facct-2026-11-03
COPY items/for-test items/for-test
RUN pnpm -C apps/viewer build:pages

# Stage 2: the service. Production dependencies only (tsx, which runs the TypeScript, is one).
FROM base AS service
COPY apps/api/package.json apps/api/pnpm-lock.yaml apps/api/
RUN pnpm -C apps/api install --frozen-lockfile --prod
COPY apps/api/tsconfig.json apps/api/
COPY apps/api/src apps/api/src
COPY apps/api/drizzle apps/api/drizzle
COPY review/samples review/samples
COPY --from=viewer /app/apps/viewer/dist apps/viewer/dist

# Image facts, not secrets. DATABASE_URL and REVIEW_INVITE_CODE come from the environment, and
# SAMPLE_PATH is set per deployment (see apps/api/README.md § Hosting).
ENV NODE_ENV=production \
    VIEWER_DIST=/app/apps/viewer/dist \
    PATH=/app/apps/api/node_modules/.bin:$PATH
WORKDIR /app/apps/api
USER node
EXPOSE 8080
# tsx directly, not `pnpm start`: the node user has no corepack cache, and the start needs no pnpm.
CMD ["tsx", "src/server.ts"]
