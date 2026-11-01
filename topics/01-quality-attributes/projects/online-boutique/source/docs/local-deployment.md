# Run Online Boutique locally

The demo has 11 microservices plus Redis. The local deployment uses the public
v0.10.7 images referenced by `release/kubernetes-manifests.yaml`. You do not need
to install the individual language runtimes, Skaffold, or Google Cloud tools.
This runs the checked-in release; source changes require rebuilding the images
as described in [the development guide](development-guide.md).

Allow at least 4 CPUs, 4 GiB of available memory, and 32 GB of disk space, as
recommended in the development guide. Internet access is required to download
packages, the Kind node image, and application images.

## Install and launch

On Arch Linux, run in your normal terminal:

```sh
yay -S --needed docker kind kubectl
sudo systemctl start docker
docker info
```

`docker info` must succeed as your current user before continuing. If it reports
permission denied, add your user to the existing Docker group in your normal
host terminal:

```sh
sudo usermod -aG docker "$USER"
newgrp docker
docker info
```

`newgrp` starts a shell with the updated group membership. Run the deployment
from that same shell. Logging out of the desktop completely and signing back in
also refreshes group membership. Docker group membership grants root-level
access to the host; see [Docker's post-installation guide](https://docs.docker.com/engine/install/linux-postinstall/).

From the `microservices-demo` directory:

```sh
bash scripts/deploy-local.sh
```

The script creates or reuses the `online-boutique` Kind cluster, deploys all
services in the `online-boutique` namespace, waits for deployment readiness,
and forwards the frontend to <http://localhost:8080>. Keep the terminal open.
Use `PORT=8081 bash scripts/deploy-local.sh` if port 8080 is already occupied.

The initial run can take several minutes while images download. The script
prints pod status and events if deployment fails. The `frontend-external`
LoadBalancer service can remain pending on Kind; access uses port forwarding.
The load generator is enabled by the release and generates synthetic shopping
traffic. Payments and email delivery are mocked.

## Inspect and stop

The cluster credentials stay in the ignored `.local-demo/kubeconfig` file.

```sh
export KUBECONFIG="$PWD/.local-demo/kubeconfig"
kubectl --context kind-online-boutique -n online-boutique get pods
kubectl --context kind-online-boutique -n online-boutique logs deployment/frontend
curl --fail http://localhost:8080/_healthz
curl --fail http://localhost:8080/ -o /tmp/online-boutique.html
```

Ctrl+C stops port forwarding. To remove the demo cluster and its resources:

```sh
kind delete cluster --name online-boutique
```

## OverlayFS mount rejected while preparing Kind nodes

If the root filesystem is a small or RAM-backed overlay, use the disk-storage
procedure below instead of the native-snapshotter workaround. File copying can
quickly fill that filesystem.

If container creation fails with `failed to mount ... fstype: overlay` and the
kernel reports `not supported as upperdir`, check the daemon's backing filesystem:

```sh
findmnt -T /var/lib/containerd
sudo journalctl -k -b --no-pager | grep -i overlay
```

On this machine the reported filesystem was itself `overlay`. A workaround is
to use containerd's `native` snapshotter, which copies files instead of making
OverlayFS mounts. This uses more disk space and can be slower. Switching the
Docker snapshotter affects all Docker workloads: restarting Docker may stop
running containers, and containers from the previous snapshotter become hidden
until the original configuration is restored. Existing images may need pulling
again for the new snapshotter.

The preparation script preserves your other Docker settings and validates the
proposed JSON. It writes only inside this project. From the project directory:

```sh
python scripts/prepare-native-docker.py
cat .local-demo/docker-daemon-native.json
sudo cp -a /etc/docker/daemon.json "/etc/docker/daemon.json.before-native.$(date +%s)"
sudo install -m 644 .local-demo/docker-daemon-native.json /etc/docker/daemon.json
sudo systemctl restart docker
docker info --format '{{.Driver}}'
docker run --rm hello-world
bash scripts/deploy-local.sh
```

The driver should read `native`. The deployment script detects this driver and
also selects `native` for containerd inside new Kind nodes. If a demo cluster
already exists, changing its internal snapshotter requires recreating that
cluster; this removes its deployed resources. The failed node-preparation
attempt normally leaves no cluster.

To revert, restore the timestamped `/etc/docker/daemon.json.before-native.*`
backup created above to `/etc/docker/daemon.json` and restart Docker.

References: [containerd snapshotters](https://github.com/containerd/containerd/blob/main/docs/snapshotters/README.md),
[Docker snapshotter selection](https://github.com/moby/moby/blob/master/daemon/daemon.go),
and [Kind snapshotter configuration](https://github.com/kubernetes-sigs/kind/blob/main/images/base/files/usr/local/bin/entrypoint).

## Small root overlay runs out of space during Kubernetes startup

The failed control-plane attempt logged `no space left on device` in the Docker
journal. The root overlay has only 5.8 GB capacity, while the project directory
is on a Btrfs filesystem with about 53 GB available at the time of inspection.
The kubeadm timeout alone does not identify which control-plane process failed;
the storage error is a concrete problem to resolve before another attempt.

Prepare disk-backed storage for both daemons:

```sh
python scripts/prepare-disk-storage.py
```

This preserves current settings, selects `overlayfs` on the actual disk
filesystem, and places runtime data in `.local-demo/runtime` under this project.
Docker's `data-root` and containerd's global `root` must both be changed.
The generated configurations are validated without starting either daemon.

Applying these settings restarts Docker and containerd and uses fresh runtime
directories. Existing containers and images stay in their old directories and
are not migrated or deleted. Running workloads may be interrupted. Do not move
or remove this project directory while these system services use its storage.

From the project directory, run in a normal host terminal:

```sh
sudo cp -a /etc/docker/daemon.json "/etc/docker/daemon.json.before-disk.$(date +%s)"
if [ -f /etc/containerd/config.toml ]; then
  sudo cp -a /etc/containerd/config.toml "/etc/containerd/config.toml.before-disk.$(date +%s)"
fi
sudo systemctl stop docker.service docker.socket containerd.service
sudo install -m 644 .local-demo/docker-daemon-disk.json /etc/docker/daemon.json
sudo install -Dm 644 .local-demo/containerd-disk.toml /etc/containerd/config.toml
sudo systemctl start containerd.service docker.service
docker info --format '{{.Driver}} {{.DockerRootDir}}'
unset KIND_EXPERIMENTAL_CONTAINERD_SNAPSHOTTER
bash scripts/deploy-local.sh
```

The driver should now be `overlayfs` and the Docker root should be inside this
project. Images will be downloaded again. If cluster creation still fails, the
deployment script now retains the failed node and exports logs under
`.local-demo/kind-logs-*`. Inspect the kubelet, containerd, and control-plane
logs there before deleting that failed cluster and retrying.

To revert, stop both daemons, restore the timestamped configuration backups,
and start both daemons. If `/etc/containerd/config.toml` was originally absent,
remove the generated config instead of restoring a backup for that file.

See [Docker's daemon data-directory documentation](https://docs.docker.com/engine/daemon/#configure-the-data-directory-location).

## Attempt in the restricted coding session

The project was inspected and dependency installation was attempted on
2026-10-15. Docker is installed, but this session cannot access its socket.
Installing `kubectl` and `kind` with Yay failed because sudo requires a password;
the session also prohibits privilege escalation. Download access failed with
`Could not resolve host: dl.k8s.io`. No cluster was created or application
started. Run the commands above in a normal host terminal with network access
and working Docker permissions.
