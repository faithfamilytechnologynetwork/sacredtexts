# The review service (Spec 154) as one image: /api, the active sample and the built viewer, from one
# origin. The build context is the REPO ROOT, because the image needs apps/viewer, apps/api and
# review/samples:
#
#   docker build -f apps/api/Dockerfile -t sacredtexts-review .
#
# Railway builds it through apps/api/railway.json (builder DOCKERFILE). A Dockerfile, not Nixpacks:
# the repo root holds requirements.txt and no package.json, so Nixpacks would detect Python.
#
# Every COPY names its paths, so no node_modules, dist or run evidence reaches the image, with or
# without a .dockerignore.

FROM node:24-bookworm-slim AS base
# The pnpm the lockfiles were written with (package.json packageManager). Prepared at build time, so
# nothing is downloaded when the container starts.
RUN corepack enable && corepack prepare pnpm@10.30.2 --activate
WORKDIR /app

# Stage 1: build the viewer. The plain `vite build`, not `build:pages`: the review origin bakes in no
# runs.
FROM base AS viewer
COPY apps/viewer/package.json apps/viewer/pnpm-lock.yaml apps/viewer/
RUN pnpm -C apps/viewer install --frozen-lockfile
COPY apps/viewer/index.html apps/viewer/vite.config.ts apps/viewer/tsconfig.json apps/viewer/
COPY apps/viewer/public apps/viewer/public
COPY apps/viewer/vite apps/viewer/vite
COPY apps/viewer/src apps/viewer/src
RUN pnpm -C apps/viewer build

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
