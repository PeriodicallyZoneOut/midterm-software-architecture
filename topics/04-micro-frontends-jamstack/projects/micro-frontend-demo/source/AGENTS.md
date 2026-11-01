# Deployment guidance

## Resolve installation before rebuilding

- Identify the requested deployment target and inspect existing configuration first.
- Check the actual lockfile format against the declared package-manager version.
  This repository declares Yarn 3 but contains a Yarn v1 lockfile. The Docker
  build uses Yarn Classic 1.22.22 with `--frozen-lockfile`; do not migrate the
  lockfile merely to deploy the demo.
- Identify runtime imports and the tools used by the production build before
  installing dependencies. Installing only production dependencies is insufficient
  when compilation needs Babel, TypeScript, loaders, and Webpack.
- Use the existing Dockerfile and `scripts/prepare-docker.mjs`. The latter narrows
  dependency manifests inside the container. Do not run it in the working checkout:
  it overwrites package manifests and rewrites registry URLs in the lockfile.
- Keep required runtime libraries and build tools. Exclude CRA, test tools,
  development servers, Turbo, and unnecessary optional binaries from this Docker
  build. Update the dependency list when source imports or build tooling change.

## Diagnose network failures directly

- For registry errors, check DNS and HTTPS from a container before retrying a full
  build. Successful host access alone does not establish container access. Use an
  existing local image for diagnostics instead of downloading another image.
- During this deployment, `registry.yarnpkg.com` failed DNS resolution while
  `registry.npmjs.org` worked. The build uses npm's registry for the same locked
  tarballs, preserving versions and integrity checks. Recheck current network
  behavior before attributing future failures to the same cause.
- Docker's DNS address `172.17.0.1` was a working systemd-resolved listener.
  Do not assume a bridge address is invalid or change daemon DNS without evidence.
- Diagnose the failing layer before changing host networking, DNS, or services.
  Prefer a project-scoped repair when it resolves the problem.

## Build once, then verify

- Preserve dependency layers and the BuildKit download cache. Avoid repeated full
  rebuilds or concurrent builds while diagnosing the same installation failure.
- If installation stops reporting progress, check installer activity and transfers
  to distinguish slow downloads from a stall. Do not repeatedly wait without
  gathering evidence or describe installation as complete before it exits successfully.
- Resume interrupted work by checking existing processes, images, and containers.
- Run `docker compose up --build -d` from this repository. When using `pkexec`,
  pass absolute `--project-directory` and `-f` paths because the working directory
  may change.
- Verify container health, both federation remotes, product images, cart updates,
  checkout, and checkout reload before reporting a successful deployment.
- The local demo is served at `http://localhost:9001`; its port binds to loopback.
  The final image contains Nginx and compiled assets, without Node or build tools.
- Report timing accurately: the reduced installation took about 11 seconds using
  the previously populated cache, not a fresh download of all dependencies.
