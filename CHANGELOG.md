# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Changed

- Updated `qcop` version from `0.9.8 -> 0.10.0` for more consistent error handling.

## [0.10.5] - 2025-02-28

### Changed

- Bumped `qcop` version from `0.9.7 -> 0.9.8`.

## [0.10.4] - 2025-02-25

### Changed

- Updated `pyproject.toml` dependencies, specifically `qcop` to fix the bug with the `CRESTAdapter` using the outdated `qcio` API for `Structure.add_identifiers()`.
- Updated `env.lock` conda dependencies and added `redis-server` to simplify deploy process for SLURM clusters.
- Deploy process overview in `README.md` updated to use the easy installer.
- Updated `install.sh` to never used a cached version of BigChem so that it always checks `pypi.org` for the latest version.

## [0.10.3] - 2025-02-08

### Changed

- Updated `qcparse` from `0.7.2` to `0.7.3` to address parsing bug of normal mode cartesian coordinates from CREST's output.

## [0.10.2] - 2025-02-07

### Added

- GitHub actions for building tagged Docker images and pushing them to Docker Hub.

### Changed

- Updated all dependencies for `conda/micromamba` `env.lock` file.

### Removed

- Removed `xtb` from `pyproject.toml`. The `xtb-python` library is no longer under active development. `tblite` has been created to power the Fortran implementation of `xtb` and `dftb+`. There is a python wrapper for `tblite` available on `conda-forge` at `tblite-python`.

## [0.10.1] - 2025-02-05

### Changed

- More flexibly defined `qcop` dependency from `^0.9.1` to `>=0.9.1`.
- Upgraded dependencies in `poetry.lock` file to use latest `qcop`, `qcio` and `qcparse` libraries for fuller CREST support in docker images.

## [0.10.0] - 2024-09-12

### Changed

- 🚨 Bumped minimum python version from 3.8 -> 3.9.
- Updated all conda dependencies in `env.lock`.
- Removed Intel's `openmp` from `env.yaml` since they seem to have removed their channel. Replaced it with `llvm-openmp`.
- Updated to `qcelemental 0.28.0` as this is required for `psi4 1.9`.
- Upgraded all python package dependencies.
- Dropped `black` and `isort` in favor of `ruff`.
- Updated typing syntax to python 3.9.
- Updated base image from `mambaorg/micromamba:1.4-jammy` -> `mambaorg/micromamba:1.5-jammy`.

### Added

- Support for CREST conformer searches (interface support via new `qcop`. Binary via conda).

## [0.9.0] - 2024-07-19

### Changed

- Updated to [qcop ^0.8.0](https://github.com/coltonbh/qcop/blob/master/CHANGELOG.md#080---2024-07-19) and [qcio ^0.11.0](https://github.com/coltonbh/qcop/blob/master/CHANGELOG.md#080---2024-07-19).

## [0.8.1] - 2024-07-12

### Added

- `release.py` script.

### Changed

- Updated `qcop` and `qcio`. Reverts back to `Structure.identifiers` over `Structure.ids`. Adds 10x performance gain to `xtb` by solving their overthreading issue.

## [0.8.0] - 2024-07-10

### Changed

- 🚨 Updated `qcio` and `qcop` to use new `Structure` instead of `Molecule`

## [0.7.2] - 2024-06-13

### Changed

- Updated to `qcio 0.9.3` which properly registers all concrete classes of `ProgramOutput[InputType, ResultsType` on `output.py` module for celery serializers.
- Updated to `qcop 0.6.2` which properly sets `exc.program_output` on all exception classes.
- Updated all packages with `poetry lock`.
- Updated syntax in `examples` scripts to be more comprehensive.

## [0.7.1] - 2024-06-10

### Changed

- Updated `qcio` `0.6.0` -> `0.6.1` to fix `AdapterError` subclasses not passing the `.program_output` argument correctly to parent classes so `celery` was failing to serialize this attribute on the exception object.
- Updated all dependencies to the latest versions in `poetry.lock`. (`poetry lock`)

## [0.7.0] - 2024-04-23

### Changed

- Updated to `qcop=^0.6.0` and `qcio=^0.9.0` to use latest Generic data structures including `ProgramOutput[InputType, ResultsType]` as a replacement for all other output models.

## [0.6.9] - 2024-04-12

### Changed

- Updated `qcop=^0.5.5` to capture `exception.program_failure` more comprehensively on `adapter.compute(...)` calls.
- Updated `qcop` also has native `xtb` adapter now to avoid >1s overhead associated with `qcengine`.

## [0.6.8] - 2024-04-05

### Changed

- Updated `celery` from buggy `5.3.1` that would feed gradients to `parallel_hessian` in random orders causing the wrong gradients to be applied to the wrong atoms. Now using `^5.3.4` which fixes this issue.
- Tightened many `>=` package dependencies to more tight `^` dependencies to avoid breaking changes in the future.
- Changed tests for `parallel_hessian` and `parallel_frequency_analysis` to test for correctness of the results rather than just that the function runs without error. This would capture a future regression where `celery` returns results in the wrong order.
- Updated all dependencies to the latest versions. (`poetry update`)

## [0.6.7] - 2024-03-29

### Changed

- - Upgraded to `qcop>=0.5.1` and `qcio>=0.8.1` to fix QCElemental behavior that auto-rotates Molecules without user consent.

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

[unreleased]: https://github.com/mtzgroup/bigchem/compare/0.10.5...HEAD
[0.10.5]: https://github.com/mtzgroup/bigchem/releases/tag/0.10.5
[0.10.4]: https://github.com/mtzgroup/bigchem/releases/tag/0.10.4
[0.10.3]: https://github.com/mtzgroup/bigchem/releases/tag/0.10.3
[0.10.2]: https://github.com/mtzgroup/bigchem/releases/tag/0.10.2
[0.10.1]: https://github.com/mtzgroup/bigchem/releases/tag/0.10.1
[0.10.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.10.0
[0.9.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.9.0
[0.8.1]: https://github.com/mtzgroup/bigchem/releases/tag/0.8.1
[0.8.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.8.0
[0.7.2]: https://github.com/mtzgroup/bigchem/releases/tag/0.7.2
[0.7.1]: https://github.com/mtzgroup/bigchem/releases/tag/0.7.1
[0.7.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.7.0
[0.6.9]: https://github.com/mtzgroup/bigchem/releases/tag/0.6.9
[0.6.8]: https://github.com/mtzgroup/bigchem/releases/tag/0.6.8
[0.6.7]: https://github.com/mtzgroup/bigchem/releases/tag/0.6.7
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
