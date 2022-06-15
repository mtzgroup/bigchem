# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Changed

### Added

### Removed

## [0.1.1]

### Changed

- Separated out dependencies only required for the worker.
- Cleaned up root of project by moving files to `docker` directory
- Cleaned up `docker-compose.xstream.yaml` stack specification

### Added

- `docker-compose.web.yaml` to specify middleware services for a deployment behind `traefik` reverse proxy.

### Removed

## [0.1.0]

### Added

- Initial release of core BigQC feature set. Tasks for `compute` (single point energy, gradient, hessian, and properties calculations) and `compute_procedure` (geometry optimization routine). Algorithms for distributed hessian and normal mode analysis with their associated tasks.

[unreleased]: https://github.com/coltonbh/bigqc/compare/0.1.1...HEAD
[0.1.1]: https://github.com/coltonbh/bigqc/releases/tag/0.1.1
[0.1.0]: https://github.com/coltonbh/bigqc/releases/tag/0.1.0
