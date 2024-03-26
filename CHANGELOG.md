# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

## [0.6.6] - 2024-03-26

### Added

- Documentation for a SLURM deploy of BigChem.
- `BIGCHEM_RESULT_EXPIRES` environment variable to set the expiration time of results in the database.

### Changed

- Example scripts are all standalone runnable and don't require the `.xyz` files to be present in the directory.

### Removed

- `version: 3.8` tag from docker-compose files as per [new docs](https://docs.docker.com/compose/compose-file/04-version-and-name/) suggesting this is no longer necessary.

## [0.6.5] - 2024-03-16

### Changed

- Updated `qcop` from `0.4.8` to `0.5.0` which sets `raise_exc=True` by default on `compute(...)` function.
- Updated `black` from `23.x.x` -> `24.x.x`.

## [0.6.4] - 2024-01-12

### Changed

- Updated `qcop` from `0.4.7` to `0.4.8` to fix the bug when geometric exceptions were raised.
- Updated `qcio` from `0.7.1` to `0.8.0`.

## [0.6.3] - 2023-09-27

### Changed

- Updated `qcop` from `0.4.6` to `0.4.7` to use latest `qcparse` encoding of TeraChem input files.

## [0.6.2] - 2023-09-26

### Added

- Added `dftd3` conda package for `psi4` to enable dispersion corrections. Updated other worker packages to latest versions.

## [0.6.1] - 2023-09-22

### Changed

- Updated `qcop` from `0.4.4` -> `0.4.6` to incorporate bugfix for `collect_wfn=True` on adapters that don't support it.

## [0.6.0] - 2023-09-20

### Changed

- Updated `qcio` to `>=0.7.0` which renamed `DualProgramArgs` to `SubProgramArgs`.
- Updated `/docker/fire.yaml` stack configuration to use the latest BigChem image.

### Fixed

- Fixed typo in `multistep_opt` algorithm where the loop was selecting programs `[:1]` instead of `[1:]` for the second and subsequent steps.

## [0.5.4] - 2023-09-08

### Changed

- Installing BigChem to `/opt/` in docker container instead of `/code/`.
- Updated `qcio` from `>=0.5.0` to `>=0.6.0`.
- Updated `qcop` from `>=0.4.3` to `>=0.5.0`.

### Added

- Device configuration to `/docker/terachem.yaml`.
- Test to ensure exception objects raised in workers have `.program_failure` object returned to the client.

## [0.5.3] - 2023-09-03

### Changed

- Moved `qcengine` and `geometric` to be optional dependencies so that client applications can install and use BigChem without these packages.

## [0.5.2] - 2023-09-02

### Changed

- Updated to `qcop>=0.4.2` for patch fixing TeraChem input file `runtime` variable.
- Updated all package dependencies.

## [0.5.1] - 2023-09-02

### Added

- Typos spell check to pre-commit and GitHub actions.

### Removed

- The `energy` kwarg for `frequency_analysis` task since the electronic energy is correctly passed to the underlying geomeTRIC function from the hessian calculation.
- `tcpb`, `pyberny`

### Changed

- Updated to `qcop` `v0.4.1` so that we can access `exception.program_failure` objects.
- `Settings` can now accept extra types. This makes it possible to install BigChem inside other apps--like ChemCloud--and not have the `Settings` object raise an exception if there are values in a `.env` file or other secrets for the second application. BigChem's `Settings` object will pick them up too, but they are never accessed so it doesn't matter.

## [0.5.0] - 2023-08-31

### Added

- Multiple scripts to `/examples/` directory to show basic utilization of BigChem.
- [docs/swarm-gpu.md](./docs/swarm-gpus.md) write up covering GPU support in Docker Swarm.
- TeraChem compose and swarm yaml specifications.
- Quickstart documentation to README.md.
- `qcio` and `qcop` as main data structures and QC program driver packages.

### Changed

- Dropped `docker-compose` from yaml filenames in `/docker` to make commands less verbose.
- Modified `docker-compose.yaml` to work for both `compose` and `swarm`.
- Removed support for Python 3.7 (reached end of life).
- Updated worker container from `micromamba:1.3-jammy` -> `micromamba:1.4-jammy`.
- Upgraded pydantic from `v1` -> `v2`.

### Removed

- Removed support for `QCElemental` and `QCEngine`.
- `scripts/hacking` directory with old, unused files.

## [0.4.0] - 2023-02-3

### Added

- `multistep_opt` algorithm and associated `multistep_opt.py` script to demonstrate how multiple QC packages can be used in unison to optimize a molecule.
- `result_to_input` task to transform results from one process (like an optimization) into inputs for the next (perhaps a subsequent optimization step). This enables easy chaining together of multiple packages in `multistep_opt`.

### Changed

- Modified `env.yaml` to allow flexible versions for worker packages and created a new `env.lock` file for workers.
- Updated `tcpb>=0.13.0` to better return `stdout` data from a crashed TeraChem server.

## [0.3.0] - 2022-12-16

### Added

- Added extensive documentation to README.md to guide new users and developers.

### Changed

- Switched default worker environment from `conda` to `micromamba` to accelerate build times (dramatically!).
- Created `env.lock` file for reproducible builds of `micromamba/conda` installs
- Updated `psi4==1.5 -> 1.7`
- Updated `qcengine==0.21.0 -> 0.26.0`
- Updated `qcelemental==0.24.0 -> 0.25.1`
- Switched geomeTRIC from personal patched version to new 1.0 release.

## [0.2.0] - 2022-07-19

### Changed

- Changed name from `BigQC` to `BigChem` to highlight that backend packages and routines may be related to any computational chemistry algorithm, not just quantum chemistry.

## [0.1.3] - 2022-06-20

### Added

- `C_FORCE_ROOT=true` environment variable to the worker image so the variable doesn't have to be passed to a container at instantiation.
- Added `:latest` tag to `build_worker.sh` script.
- Added `push_worker.sh` scripts so I don't forget to push the tag and the image as the `latest` tag to the docker repo.

## [0.1.2] - 2022-06-15

### Changed

- Wrapped `qcng.compute` and `qcng.compute_procedure` directly with `bigqc.task` rather than redefining each function
- Simplified settings by removing `get_settings` function in favor of globally defined `settings` object. (No advantage to using a callable since we are not using dependency injection of a settings callable.)
- Updated app name to `bigqc` from `tasks` in `app.py`.

## [0.1.1] - 2022-06-14

### Added

- `docker-compose.web.yaml` to specify middleware services for a deployment behind `traefik` reverse proxy.

### Changed

- Separated out dependencies only required for the worker.
- Cleaned up root of project by moving files to `docker` directory
- Cleaned up `docker-compose.xstream.yaml` stack specification

## [0.1.0] - 2022-06-14

### Added

- Initial release of core BigQC feature set. Tasks for `compute` (single point energy, gradient, hessian, and properties calculations) and `compute_procedure` (geometry optimization routine). Algorithms for distributed hessian and normal mode analysis with their associated tasks.

[unreleased]: https://github.com/mtzgroup/bigchem/compare/0.6.6...HEAD
[0.6.6]: https://github.com/mtzgroup/bigchem/releases/tag/0.6.6
[0.6.5]: https://github.com/mtzgroup/bigchem/releases/tag/0.6.5
[0.6.4]: https://github.com/mtzgroup/bigchem/releases/tag/0.6.4
[0.6.3]: https://github.com/mtzgroup/bigchem/releases/tag/0.6.3
[0.6.2]: https://github.com/mtzgroup/bigchem/releases/tag/0.6.2
[0.6.1]: https://github.com/mtzgroup/bigchem/releases/tag/0.6.1
[0.6.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.6.0
[0.5.4]: https://github.com/mtzgroup/bigchem/releases/tag/0.5.4
[0.5.3]: https://github.com/mtzgroup/bigchem/releases/tag/0.5.3
[0.5.2]: https://github.com/mtzgroup/bigchem/releases/tag/0.5.2
[0.5.1]: https://github.com/mtzgroup/bigchem/releases/tag/0.5.1
[0.5.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.5.0
[0.4.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.4.0
[0.3.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.3.0
[0.2.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.2.0
[0.1.3]: https://github.com/mtzgroup/bigchem/releases/tag/0.1.3
[0.1.2]: https://github.com/mtzgroup/bigchem/releases/tag/0.1.2
[0.1.1]: https://github.com/mtzgroup/bigchem/releases/tag/0.1.1
[0.1.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.1.0
