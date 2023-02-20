# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

## [0.4.0] - 2023-02-3

### Added

- `multistep_opt` algorithm and associated `multistep_opt.py` script to demonstrate how multiple QC packages can be used in unison to optimize a molecule.
- `result_to_input` task to transform results from one process (like an optimization) into inputs for the next (perhaps a subsequent optimization step). The enables the easy chaining together of multiple packages in `multistep_opt`.

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

[unreleased]: https://github.com/mtzgroup/bigchem/compare/0.4.0...HEAD
[0.4.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.4.0
[0.3.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.3.0
[0.2.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.2.0
[0.1.3]: https://github.com/mtzgroup/bigchem/releases/tag/0.1.3
[0.1.2]: https://github.com/mtzgroup/bigchem/releases/tag/0.1.2
[0.1.1]: https://github.com/mtzgroup/bigchem/releases/tag/0.1.1
[0.1.0]: https://github.com/mtzgroup/bigchem/releases/tag/0.1.0
