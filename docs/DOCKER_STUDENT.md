# Real runs for students via Docker

Real RTL-to-GDS runs need the OpenROAD toolchain. Instead of every student
installing it natively (hard on Windows/Mac), we ship **one Docker image**
that has the tools + gli-flow + sky130 PDK baked in. Students install Docker
Desktop, pull the image once, and run real flows on their own RTL — results
are design-specific and upload to their account.

---

## Part A — Maintainer: build & publish the image (you, once)

You need a Docker Hub account (free) at https://hub.docker.com. Your
username goes in the image tag; the examples use `sanjai1903`.

```
cd ~/Downloads/project_work/gli-flow-asic

# 1. Log in to Docker Hub
docker login

# 2. Build the image (takes 20-40 min; it compiles/fetches ORFS + PDK)
docker build -f Dockerfile.student -t sanjaimurugan/gli-flow:latest .

# 3. Push it so students can pull it
docker push sanjaimurugan/gli-flow:latest
```

If your Docker Hub username isn't `sanjaimurugan`, replace it everywhere
(the tag here, and `GLI_FLOW_IMAGE` default in the two wrapper scripts under
`docker/`).

> Apple Silicon note: OpenROAD's prebuilt .deb is amd64. On an M-series Mac,
> build with `--platform linux/amd64` (Docker emulates it). Students on any
> chip then pull the amd64 image and Docker handles emulation.
> ```
> docker build --platform linux/amd64 -f Dockerfile.student -t sanjaimurugan/gli-flow:latest .
> ```

### Re-publishing after code changes

Rebuild and push again with the same command. Students get the update with
`docker pull sanjaimurugan/gli-flow:latest`.

---

## Part B — Student: install Docker, then run real flows

### 1. Install Docker Desktop
https://www.docker.com/products/docker-desktop/ — Windows, macOS, or Linux.
Start it (the whale icon should be running).

### 2. Get the wrapper script
Download `gli-flow-docker` (macOS/Linux) or `gli-flow-docker.ps1` (Windows)
from the repo's `docker/` folder, and put it in the folder where your RTL is.

macOS/Linux — make it executable once:
```
chmod +x gli-flow-docker
```

### 3. Log in (opens your browser)
```
./gli-flow-docker login          # macOS/Linux
.\gli-flow-docker.ps1 login      # Windows PowerShell
```
It prints a URL + code — open the URL, sign in with Google, approve. Your
token is saved to `~/.gli-flow` on your machine and reused by the container.

### 4. Build a design from your RTL and run it FOR REAL
```
# macOS/Linux
./gli-flow-docker init mux --rtl mux.v --sdc mux.sdc
./gli-flow-docker run mux

# Windows PowerShell
.\gli-flow-docker.ps1 init mux --rtl mux.v --sdc mux.sdc
.\gli-flow-docker.ps1 run mux
```

Note: **no `--mock`** — this is a real synthesis + place-and-route run, so
different designs give different QoR, area, and timing. Results upload to
your account automatically; refresh https://gli-flow-1-0.vercel.app to see
them.

The first `run` is slow (real tools). Subsequent runs are faster.

---

## How it works (for the curious)

The wrapper runs:
```
docker run --rm -it \
  -v "$(pwd)":/work \                     # your RTL folder -> container
  -v "$HOME/.gli-flow":/root/.gli-flow \  # your login token -> container
  -e GLI_INGEST_URL=... -e GLI_WEB_URL=... \
  sanjaimurugan/gli-flow:latest <your gli-flow args>
```
So the container sees your files and your identity, runs the real flow, and
uploads under your account — exactly like a native run, just with the tools
living in the image instead of on your laptop.

---

## Troubleshooting

- **`docker: command not found`** — Docker Desktop isn't installed or not
  running. Install it and start it.
- **`Cannot connect to the Docker daemon`** — Docker Desktop isn't running;
  open the app and wait for the whale icon to settle.
- **Run says ORFS/PDK missing** — the build-time install didn't finish. Run
  `./gli-flow-docker install` once to fetch them into your mounted
  `~/.gli-flow` (persists for future runs).
- **Very slow on Apple Silicon** — the image is amd64 and emulated. That's
  expected; it still works.
```
