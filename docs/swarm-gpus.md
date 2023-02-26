# GPU Support For Docker Swarm

Docker compose has [nice support for GPUs](https://docs.docker.com/compose/gpu-support/), K8s has moved their [cluster-wide GPU scheduler](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/) from experimental to stable status. Docker swarm has yet to support the `device` option used in `docker compose` so the mechanisms for supporting GPUs on swarm are a bit more open-ended.

## Basic documentation

- [NVIDIA container runtime for docker](https://docs.docker.com/config/containers/resource_constraints/#gpu). The runtime is no longer required to run GPU support with the docker cli or compose; however, it appears necessary so that one can set `Default Runtime: nvidia` for swarm mode.
- [NVIDIA]
- [docker compose GPU support](https://docs.docker.com/compose/gpu-support/)
- [Good GitHub Gist Reference](https://gist.github.com/tomlankhorst/33da3c4b9edbde5c83fc1244f010815c) for an overview on Swarm with GPUs. It is a bit dated, but has good links and conversation.
- [Miscellaneous Options](https://docs.docker.com/engine/reference/commandline/dockerd/#miscellaneous-options) for docker configuration. Go down to "Node Generic Resources" for an explanation of how this is intended to support NVIDIA GPUs. The main idea is one has to change the `/etc/docker/daemon.json` file to advertise the `node-generic-resources` (NVIDIA GPUs) on each node. GPUs have to be added by hand the the `daemon.json` file, swarm does not detect and advertise them automatically.
- [How to create a service with generic resources](https://docs.docker.com/engine/reference/commandline/service_create/#generic-resources). This shows how to create stacks/services requesting the generic resources advertised in the `/etc/docker/daemon.json` file.
- [Quick blog overview](https://sourabhburnwal.medium.com/docker-swarm-and-gpus-c549156d96eb) confirming these basic approaches.
- [Really good overview](https://gabrieldemarmiesse.github.io/python-on-whales/user_guide/generic_resources/) on Generic Resources in swarm.

## Solutions to Enable Swarm GPU Support

Both solutions need to follow these steps first:

1. Install `nvidia-container-runtime`. Follow the steps [here](https://docs.docker.com/config/containers/resource_constraints/#gpu). Takes <5 minutes.
2. Update `/etc/docker/daemon.json` to use `nvidia` as the default runtime. Then restart the docker daemon on each node `sudo service docker restart`. Confirm the default runtime is `nvidia` with `docker info`.

```json
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
```

### Solution 1

You're done. When you deploy a service to a node, it will by default see all the GPUs on that node. Generally this means you are deploying global services (one per node) or assigning services to specific nodes so that there aren't accidental collisions between services accessing the same GPU resources.

If you want to expose only certain GPUs to a given service (e.g., multiple services on one node with each having access only to its own GPU(s)) use the `NVIDIA_VISIBLE_DEVICES` environment variable for each service. See [bigchem/docker/docker-compose.terachem.xstream.yaml](https://github.com/mtzgroup/bigchem/blob/master/docker/docker-compose.terachem.xstream.yaml) for an example of how to do this dynamically so that each services gets access to its own GPU using [docker service templates](https://docs.docker.com/engine/reference/commandline/service_create/#create-services-using-templates). Because `{{.Task.Slot}}` starts counting at `1`, the `global` service is also included in the template to make use of GPU `0`.

### Solution 2

Advertise NVIDA GPUs using [Node Generic Resources](https://docs.docker.com/engine/reference/commandline/dockerd/#miscellaneous-options). This is the most general purpose approach and will enable services to simply declare the required GPU resources and swarm will schedule them accordingly.

The `/etc/docker/daemon.json` file on each node needs to be updated to advertise its GPU resources. You can find the UUID for each GPU by running `nvidia-smi -a | grep UUID`. You only need to include `GPU` plus the first 8 digits of the UUID, it seems, i.e., `GPU-ba74caf3` for the UUID. The following needs to be added to the `daemon.json` file already declaring `nvidia` as the default runtime.

```sh
{
  "node-generic-resources": [
    "NVIDIA-GPU=GPU-ba74caf3",
    "NVIDIA-GPU=GPU-dl23cdb4"
  ]
}
```

Enable GPU resource advertising by uncommenting the `swarm-resource = "DOCKER_RESOURCE_GPU"` line (line 2) in `/etc/nvidia-container-runtime/config.toml`.

The docker daemon must be restarted after updating these files by running `sudo service docker restart` on each node. Services can now request GPUs using the [generic-resource flag](https://docs.docker.com/engine/reference/commandline/service_create/#generic-resources).

```sh
docker service create \
    --name cuda \
    --generic-resource "NVIDIA-GPU=2" \
    --generic-resource "SSD=1" \
    nvidia/cuda
```

The names for `node-generic-resources` in `/etc/docker/daemon.json` could be anything you want. So if you want to declare `NVIDIA-H100` and `NVIDIA-4090` you could and then request specific GPU types with `--generic-resource "NVIDIA-H100"`.

To request GPU resources in a `docker-compose.yaml` file for the stack use the following under the `deploy` key.

```yaml
services:
  my-gpu-service:
    ...
    deploy:
      resources:
        reservations:
          generic_resources:
            - discrete_resource_spec:
              kind: "NVIDIA-GPU"
              value: 2
```
