# BigChem

A distributed system for scaling and parallelizing quantum chemistry calculations.

## ⚠️ A Note About x86 and ARM Architectures

Most Quantum Chemistry packages (including those used by default in BigChem's worker--psi4, xtb, and rdkit) are only compiled and released for the x86 architecture, not the ARM architecture. This means **BigChem's worker will not work or build on ARM machines like Apple's M1 chip**. If you want to run Quantum Chemistry programs on your ARM machine, please reach out to your favorite QC developer and ask for distributions compiled for ARM. When they exist, I'll add them to BigChem's ARM builds.

If you'd like to play with BigChem without executing QC programs on your ARM machine, comment out the `worker` in the `docker-compose.yaml` file, then run the following commands to run a local version of a BigChem worker that can execute the `add` and `csum` `Tasks` to explore how BigChem works. Note Docker has updated the `docker-compose` command to be a subcommand of the Docker CLI `docker compose` (no `-`). If you are running an older version of Docker Desktop you may still need to use the `docker-compose` command instead.

```sh
docker compose up -d --build
poetry install
poetry run celery -A bigchem.tasks worker --without-heartbeat --without-mingle --without-gossip --loglevel=INFO
```

## 🐰 Quickstart

✅ Make sure you are on an x86 machine (not an ARM machine like Apple's M chip series)

✅ Install [poetry](https://python-poetry.org/) to install BigChem

### 💻 Run BigChem on a Single Node (like your laptop)

- Install project dependencies

  ```sh
  poetry install
  ```

- Check that your installation is working correctly by running the tests. (Requires `docker compose`).

  ```sh
  bash scripts/test.sh
  ```

- You can review test coverage in the now-generated `htmlcov` folder; open `index.html` in a browser.

- Run the following commands to start a broker, backend, and worker.

  ```sh
  docker compose up -d --build
  ```

- You can stop these services by running:

  ```sh
  docker compose down
  ```

- With BigChem running (`docker compose up -d --build`) execute scripts in the `examples` directory to see how to perform computations using BigChem. Add the `-i` flag when running python to drop into an interactive terminal after a script executes to interact with the returned objects.

  ```sh
  poetry run python -i examples/example.py
  ```

If you would like to increase the number of BigChem worker processes running, uncomment and edit the `bigchem_worker_concurrency` value in the `docker-compose.yaml` file.

### 💻💻💻 Run BigChem on Multiple Nodes (Swarm Mode)

You do not need to install BigChem or any Quantum Chemistry package on each node. You only need to have [Docker](https://www.docker.com/) installed on each node. We will use [Docker Swarm](https://docs.docker.com/engine/swarm/) to distribute BigChem to each node. We assume the nodes are networked together and reachable via **TCP port 2377** for cluster management communications, **TCP and UDP port 7946** for communication among nodes, and **UDP port 4789** for overlay network traffic.

Execute the following commands on the node you wish to be your "Manager" node, the node from which you will control the system.

- Start a Swarm

  ```sh
  docker swarm init
  ```

- Collect the join command for adding worker nodes to this swarm

  ```sh
  docker swarm join-token worker
  ```

- Run the printed command on all the nodes you wish to join your swarm and then return to the Manager node.

  ```sh
  docker swarm join --token super-secret-token-xxx ip-addr-of-manager:2377
  ```

- From your manager node deploy BigChem. This will start a broker and backend running on the manager node and one BigChem worker on each node.

  ```sh
  docker stack deploy -c docker-compose.yaml --prune bigchem
  ```

- BigChem will now be running on all nodes. It may take a few moments for the services to start since the worker image is large and will need to be downloaded and decompressed on all nodes.
- You can increase the number of BigChem worker processes running on each node by uncommenting and editing the `bigchem_worker_concurrency` value in the `docker-compose.yaml` file and then running `docker stack deploy ...` again.

- Send work to BigChem by running any of the scripts in the `example` directory. Tasks will be distributed across all worker nodes.

  ```sh
  poetry run python -i examples/energy.py
  ```

- NOTE: If the example scripts are hanging without printing out any status or completing it may be a `localhost` networking issue. Depending on your system configuration `localhost` may be resolving to an ipv4 or ipv6 address. If you deployed your swarm using an ipv4 address yet `localhost` refers to an `ipv6` address on your machine, you won't be able to talk to the broker/backend at `localhost`. Usually just the backend has issues. Try the following to explicitly connect to the backend at `127.0.0.1`. Add the `bigchem_broker_url=amqp://127.0.0.1` as well, if needed.

  ```sh
  bigchem_backend_url=redis://127.0.0.1/0 python examples/energy.py
  ```

- Shutdown BigChem

  ```sh
  docker stack rm bigchem
  ```

### 💻 + 💪 Run BigChem on a Single Node with TeraChem (GPU Support)

- Same as above but use the following instead of `docker compose up -d --build`

  ```sh
  docker compose -f docker-compose.yaml -f docker/terachem.yaml up -d --build
  ```

This will run TeraChem in unlicensed mode. If you'd like to use a license uncomment the `${TERACHEM_LICENSE_PATH}:/terachem/license.key` line in `docker/terachem.yaml` and add `TERACHEM_LICENSE_PATH=/path/to/your/license.key` to a `.env` file in the root of the project using the path on your local machine containing the license.

- Send work to TeraChem by modifying any of the `examples` scripts to use `terachem_fe` instead of `psi4`.
- Run the `examples/terachem.py` script to see how to request files back from TeraChem
  ```sh
  poetry run python -i examples/terachem.py
  ```

### 💻💻💻 + 💪💪💪 Run BigChem on Multiple Nodes with TeraChem (Swarm Mode)

GPU support for Docker Swarm can be implemented multiple ways. We will demonstrated the simplest way here. For more details see [docs/swarm-gpus.md](./docs/swarm-gpus.md). First follow the instructions above to initialize a swarm.

- Follow the instructions [here](https://docs.docker.com/config/containers/resource_constraints/#gpu) to install `nvidia-container-runtime` on each node.
- Update (or create) `/etc/docker/daemon.json` on each node to use `nvidia` as the default runtime with the following:

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

- Restart docker on each node `sudo service docker restart`

- Run the following command to deploy BigChem and TeraChem to all nodes. **Note the second docker-compose file has a different name than the single-node file, `terachem.SWARM.yaml`.**

  ```sh
  docker stack deploy -c docker-compose.yaml -c docker/terachem.swarm.yaml --prune bigchem
  ```

- BigChem and TeraChem will now be running on all nodes. It may take a few moments for the services to start since both images are large and will need to be downloaded and decompressed on all nodes.

## Getting into the Details

### Overview

BigChem is built on [Celery](https://docs.celeryq.dev/en/stable/index.html) and uses a producer/consumer model for delivering and completing work tasks. You may refer to the Celery documentation for a deeper dive on technical details.

Why is BigChem useful? Many computational chemistry tasks require large, distributed resources due to the scale or quantity of computations. Programming highly parallel or distributed computing tasks is challenging and requires specialized skills. BigChem makes it easy to take advantage of modern, distributed system compute paradigms without requiring expert-level understanding of distributed systems or parallelization. End users write very simple, single-threaded code, yet BigChem will efficiently distribute calculations across hundreds or thousands of compute nodes and deliver results back as if the calculations were performed on the local machine. BigChem is easy to use, easy to program, and easy to deploy across a few or thousands of nodes.

BigChem has only a few key ideas that need to be mastered in order to execute distributed tasks or further develop the system to execute new tasks.

A basic system overview helps demonstrate how BigChem works. End users can import BigChem's `Tasks` or `Algorithms` into their code as generic Python functions. Calling these functions using `.delay()` or `.apply_async()` and passing the relevant arguments, e.g., `add.delay(2,2)`, tells BigChem to place the work on the `broker` (messaging queue). The `broker` delivers the `Task` to an available worker which executes the `Task`, confirms successful execution to the `broker`, and places the result in the `backend`. End users get results from the `backend` by calling `.get()` on the future object returned from calling `.delay()` or `.apply_async()`. To end users they appear to be writing single-threaded Python code, but behind the scenes an array of BigChem workers can be executing their compute tasks at any scale on distributed resources anywhere in the world.

Only one `broker` and `backend` are ever running at a time. The system scales by increasing the number of workers connected to the system. Usually one worker runs on a given compute node.

```python
from bigchem.tasks import add
future_result = add.delay(2,2) # sends task to broker, returns `AsyncResult`
# Workers will now receive the task, execute it, and write the result to the backend
result = future_result.get() # collects task's return value from the backend
result.forget() # removes the result from the backend to free up resources for future calculations
```

![Figure 1](./assets/figure_1.jpg)

BigChem's core object is a `Task`. A `Task` is simply a Python function wrapped with the `@bigchem.task` decorator. `Tasks` can be any computing objective written in any language, calling any subprocess, or leveraging any executable. Tasks that cannot be defined as pure Python code or are written in other languages can be called using Python's [subprocess module](https://docs.python.org/3/library/subprocess.html). Tasks can be found in the `bigchem/tasks.py` module. Once a `Task` is registered with BigChem, BigChem will automatically know how to execute it remotely on worker machines and distribute it across all available resources.

`Tasks` can also be combined into more complex computational networks to create `Algorithms`. `Algorithms` make use of `Tasks` plus the `group`, `chain`, or `chord` primitive to define computational tasks comprised of many `Tasks` executed simultaneously or in sequence. Each `Task` in the `Algorithm` will be executed on different distributed workers in parallel. BigChem will orchestrate the execution of `Tasks` and collection of results across distributed resources. `Algorithms` can be found in `bigchem/algos.py` or created on the fly using existing tasks. Below we create an `Algorithm` using BigChem's `add` and `csum` `Tasks`. The function returns a `Signature`, an object that contains the network of tasks to be executed and their arguments. The `Signature` can be executed on BigChem workers by calling `.delay()` or `.apply_async()` on the `Signature`.

```python
from bigchem.tasks import add, csum
from bigchem.canvas import group, Signature

def distributed_sum(max: int) -> Signature:
    """Performs the addition each integer from 0 to max with itself in parallel on
    disparate worker nodes, then sums up all those values into a final number.

    The group tells BigChem to execute all tasks in the group in parallel.
    The | symbol creates a chord and BigChem will pass all the distributed results
    from the group as an argument to csum which will sum up the results.

    Each compute task in the group and the csum task may execute on different
    nodes. BigChem will orchestrate the efficient distribution of tasks across nodes
    and coordinate collection of results from each node, without end users or
    developers needing to consider these complex actions.
    """
    return group(add.s(i, i) for i in range(max)) | csum.s()

# Note that we are passing arguments directly to distributed_sum and then calling
# .delay() rather than passing arguments to .delay() as when calling a basic Task
future_result = distributed_sum(10).delay()
result = future_result.get()
future_result.forget() # to remove results from the backend
```

In summary, BigChem uses a `broker` to distribute `Tasks` to an arbitrary number of workers located anywhere in the world. Workers execute `Tasks` remotely and write their results to the `backend`. Users retrieve results from the backend by calling `.get()` on `AsyncResult` futures objects.

### Workers

A worker process knows about `Tasks` registered with BigChem, where to get work (the `broker`), and where to write results (the `backend`). A worker must have BigChem installed to know about registered `Tasks` and any other software called by `Tasks` installed (such as external Quantum Chemistry packages like `psi4` or `TeraChem`).

Generally, you run a single worker on a given compute node. Unless you are using GPUs or other accelerators or have an unusually complicated deployment it probably doesn't make sense to run more than one worker per node. The worker itself can scale the number of subprocesses that it uses to process tasks by setting the `bigchem_worker_concurrency` environment variable. So one worker can have multiple independent subprocesses accepting `Tasks`.

How do you know how many BigChem worker processes to run on each node? Generally, this depends on the nature of the `Tasks` you are executing. If you are executing code that makes efficient use of all CPU cores on a node, then having `bigchem_worker_concurrency=1` (the default value) is appropriate as the `Task` will be making efficient use of the node. If you are executing `Tasks` that are single-threaded (use only 1 CPU core at a time) then you should set `bigchem_worker_concurrency` to the number of cores on the machine. Setting `bigchem_worker_concurrency=0` will tell BigChem to automatically set the concurrency to the number of cores on the machine. Optimal performance tuning is idiosyncratic to the underlying code, so testing is key if you want to get maximum scaling performance from your code at various levels of concurrency. Scaling the number of nodes running workers will produce linear performance gains for the system.

### Local Development

The `docker-compose.yaml` file creates a local BigChem system with a single worker for executing tasks.

```sh
docker compose up -d --build
```

This command starts up the three BigChem components: a `broker`, a `backend` and a `worker`. The `broker` is a RabbitMQ instance with an admin dashboard available at `http://localhost:15672` using the username and password `guest` and `guest`. The `broker` receives `Tasks` and by default places them on the `celery` queue for consumption by workers. The `backend` is a `redis` instance. The `worker` will get built from the `docker/worker.dockerfile` file and will contain `BigChem`, `psi4`, `rdkit`, and `xtb`. The `worker` will consume tasks from the `broker` and write results to the `backend`.

Services can be monitored in real time using the `container_name` specified in the `docker-compose.yaml` file and the `docker logs` command.

```sh
docker logs {container_name} -f
```

If new `Tasks` are added to BigChem or existing tasks are modified, the worker must be restarted to pickup the new or modified `Tasks`. You can restart the worker by either rebuilding the container (`docker compose up -d --build`) or by just restarting the worker since the code is mounted into the container directly (`docker restart bigchem_worker`), generally restarting the worker should be faster.

If you want to scale your worker subprocesses locally, uncomment and adjust the `bigchem_worker_concurrency` variable to your desired number or to `0` to automatically scale to the number of CPU cores on your machine.

If you want to add additional Quantum Chemistry programs (or any program!) to the worker, modify the `docker/worker.dockerfile` to install the program and then rebuild the image by running `docker compose up -d --build`.

If you have a GPU on your machine and want to run TeraChem as part of BigChem, include `docker/terachem.yaml` when you start BigChem. See the [TeraChem/GPU Section Above](#💻--💪-run-bigchem-on-a-single-node-with-terachem-gpu-support) above for more details.

```sh
docker compose -f docker-compose.yaml -f docker/terachem.yaml up -d --build
```

### Deployment

Deploying BigChem to a production environment consists of running a `broker` and a `backend` that are reachable by `workers` and then as many workers as you'd like. Workers will connect to the `broker` and `backend` and BigChem will automatically coordinate efficient distribution of `Tasks` across all workers and the synchronization of more sophisticated `Algorithms` that need to pass results between workers. Deployment can be done with or without Docker, depending on the access you have to the underlying hardware. We strongly recommend deploying with Docker if you are able. The Multi-Node (Swarm) examples in the [🐰 Quickstart](#🐰-quickstart) are both examples of production deployments.

All configurable environment variables for BigChem can be found in `bigchem/config.py`. If environment variables are set with the same names found as attributes on the `Settings` object, they will be automatically picked up and used by BigChem. Examples of this can be found in the `docker-compose.yaml` file where various settings are modified via environment variables. Variables can be `lower_case` or all `UPPER_CASE`.

#### Broker and Backend

The `broker` and `backend` need to be deployed somewhere that `workers` can connect to via a TCP connection. This means they can be deployed on a local cluster where workers will run, or on a remote server (like a cloud server) that has a public IP address and is reachable from anywhere. If you are deploying your `broker` and `backend` on a cloud service and connecting to them over the open internet we strongly recommend you use `TLS` connections to secure communication between your `workers`, `broker`, and `backend`. For an example of how to deploy a `broker` and `backend` securely behind a [Traefik](https://traefik.io/) reverse proxy that handles `TLS` for you, see `docker/web.yaml` and follow the instructions below. The configuration for running a Traefik reverse proxy can be found [here](https://github.com/mtzgroup/traefik-reverse-proxy).

If you want to secure your broker/backend with usernames/passwords create the following files and populate with their correct secrets and then reference them in your `docker-compose.yaml` file as in `docker/web.yaml`.

- `rabbit.env`

```sh
RABBITMQ_DEFAULT_USER=
RABBITMQ_DEFAULT_PASS=
```

- `redis.conf`

```sh
requirepass ${your_redis_password}
```

#### Docker Swarm

Deploying BigChem workers across many nodes on a cluster is very simple using [Docker Swarm](https://docs.docker.com/engine/swarm/). The examples in the [Quickstart](#🐰-quickstart) can get your started.

If you need to pass secrets (like usernames/password for your broker/backend) to your services use a `worker.env` file as described below. Omit `# pragma: allowlist secret` as that is just for linting purposes in the README.md.

```yaml
# NOTE: depends on a single worker.env file alongside this .yaml file containing two
# environment variables; fill these with the URLs of the broker and backend.
# BIGCHEM_BROKER_URL=amqps://admin123:supersecret987@rabbit.mydomain.com:5671 # pragma: allowlist secret
# BIGCHEM_BACKEND_URL=rediss://:password123@redis.mydomain.com:6379/0?ssl_cert_reqs=CERT_NONE # pragma: allowlist secret
version: "3.8"

services:
  worker:
    image: mtzgroup/bigchem-worker
    env_file: worker.env
    environment:
      - bigchem_worker_concurrency=2
    volumes:
      # qcengine uses /tmp by default for scratch directory
      - scratch:/tmp
    deploy:
      mode: global

volumes:
  scratch:
```

This definition depends on a `worker.env` file living next to the `docker-compose.workers.yaml` file that defines the URLs at which workers can locate the BigChem `broker` and `backend`. If the addresses are local to your cluster and don't contain secrets (like passwords) then you can just place the addresses directly in the `docker-compose.workers.yaml` file as environment variables and delete the `env_file` line from the file. The `worker.env` file should look like this but be filled with the corresponding usernames, passwords, and hosts. If you are using insecure (non-encrypted) protocols over a local network change `amqps` to `amqp` and change the port from `5671` to `5672` (or remove it, `5672` is the default port for RabbitMQ) and `rediss` to `redis` and remove `?ssl_cert_reqs=CERT_NONE` to denote the use of insecure protocols (you may also remove the `6379` port specification). The `docker-compose.yaml` file in the root shows an example of insecure URLs without usernames, passwords, or ports.

- `worker.env`

  ```sh
  BIGCHEM_BROKER_URL=amqps://${USERNAME}:${PASSWORD}@${YOUR_DOMAIN_DOT_COM}:5671
  BIGCHEM_BACKEND_URL=rediss://:${PASSWORD}@${YOUR_DOMAIN_DOT_COM}:6379/0?ssl_cert_reqs=CERT_NONE
  ```

**NOTE:**

- The usernames and passwords in the `worker.env` file should match those set in the `rabbit.env` and `redis.conf` files.
- The amqpS/redisS protocols. If you are connecting over the open internet you should require TLS. Also note the use of the `5671` _secure_ port for `amqps` connections. This is the port on which `traefik` is listening for `amqps` connections.
- We do not verify the SSL certificate for `redis`. This is because `traefik` is dynamically generating and renewing SSL certificates so we do not have a "permanent" certificate that we can place on the client and use for verification. Very low risk of man-in-the-middle attacks here.
- If your workers are not connecting over the open internet they can connect directly using insecure protocols to the broker/backend rather than proxying through the `traefik` reverse proxy.

If you have defined your `broker` and `backend` as services in the same `docker-compose.workers.yaml` (like in the `docker-compose.yaml` file in the root of this project), then you use the name of the service as the hostname and docker will route TCP connections appropriately. See the `environment` section of the `worker` in the `docker-compose.yaml` file as an example.

The `global` deploy mode tells Docker Swarm to place one instance of this service on each node. The `volumes` specification creates a [Docker Volume](https://docs.docker.com/storage/volumes/) on each node to act as a scratch disk for calculations. And we set `bigchem_worker_concurrency=2` so that each node has two worker subprocesses consuming tasks.

You can deploy workers across your swarm by running the following on a manager node:

```sh
docker stack deploy -c docker-compose.workers.yaml --prune bigchem
```

You can inspect the worker services by running:

```sh
docker stack services bigchem
```

Logs can be followed by running:

```sh
docker service logs bigchem_worker -f
```

Workers can be removed by running:

```sh
docker stack rm bigchem
```

For more sophisticated deployments you can tune how many workers run on each node, which queues each worker listens to (the `broker` can host multiple queues and workers can listen to one, many, or all of them, `Tasks` can be sent to specific queues by end users). And you can tune specific environment variables, like which GPU to use, for each individual worker. To see an example of a more sophisticated deployment see `docker/xstream.yaml`. This deployment runs workers in "replicated" mode (as opposed to global mode) to have more than one worker per node, makes use of constraints like the hostname of the node to determine worker placement, and uses dynamic environment variables so that each worker is assigned exactly one GPU to use for calculations on nodes that contain multiple GPUs. The `XStream` deployment allows independent scaling of workers on each node using the `docker service scale` command. Using only a few lines of configuration, one can deploy 88 workers across 88 GPUs on 6 different nodes with unique environment variables for each worker using a single command: `docker stack deploy -c docker/xstream.yaml --prune bigchem`. See [Swarm GPUs](./docs/swarm-gpus.md) for more details on how to configure GPU support for Docker Swarm.

If you want to build a custom worker image with additional `Tasks`, `Algorithms`, or Quantum Chemistry programs you can modify `bigchem/tasks.py` and/or `bigchem/algos.py` and build a new image running the following from the root directory. Note that algorithms do not need to be written in the BigChem repo or deployed to workers. They can be written in any script without needing to deploy it to BigChem since algorithms are composed of `Tasks` that BigChem already knows about and orchestration primitives (`group`/`chain`/`chord`) that simply tell BigChem how to execute those `Tasks`.

```sh
docker build -t whatever_you_name_your_image:0.1.0 .`
```

You can push this image to a free [Docker Hub](https://hub.docker.com/) account and replace the `image:` line in the `docker-compose.workers.yaml` file above with the name of your image.

If you want to add additional Quantum Chemistry programs you can modify the `worker.dockerfile` file to install them into your image and then perform the same steps mentioned above to build, push, and deploy your workers to your swarm.

#### Non-Docker Deployment

Docker makes it easy to deploy a few or hundreds of workers across distributed resources, manage package dependencies, and ensure that each node is running identical code. But Docker is not required to run BigChem workers. The only thing that is required is a BigChem install and any additional executables (like Quantum Chemistry programs) that the `Tasks` use.

You can install BigChem on a node by running the following command. This command will install BigChem and all its required Python dependencies (but not external programs like `psi4` or `TeraChem`):

```sh
python -m pip install bigchem
```

Or if you are wanting to run your own modified version of BigChem, place the source code on a node and from the root directory of this codebase run:

```sh
python -m pip install .
```

Workers can be started by running the following:

```sh
celery -A bigchem.tasks worker --without-heartbeat --without-mingle --without-gossip --loglevel=INFO
```

Note this is the same command issued in the `worker.dockerfile`. Additional executables--like Quantum Chemistry packages used by `Tasks`--must be installed separately on each node. You can learn more about controlling workers in the [Celery documentation](https://docs.celeryq.dev/en/stable/userguide/workers.html).

Deploying non-Dockerized workers on each node consists of installing the BigChem repo on each node, and then starting the workers with the `celery` command. That's it!
