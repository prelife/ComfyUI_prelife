# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-01-02

### Added
- Migration to ComfyUI V3 API
  - Schema-based node definitions using `io.Schema`
  - Type-safe inputs and outputs with `io.ImageInput`, `io.IntOutput`
  - Input validation via `validate_inputs()` method
  - Proper batch processing support returning lists for each image
  - V3 entry point with `comfy_entrypoint()` function
- Enhanced documentation and tooltips for node inputs/outputs
- Dependencies specification in pyproject.toml (torch, numpy)
- Python 3.12 support

### Changed
- Updated minimum Python version from 3.8 to 3.10
- Node now returns lists instead of single values to support batch processing
- Improved error handling with ValidationError for invalid inputs
- Updated README with V3 API features and usage examples

### Deprecated
- Legacy V1 API implementation (NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS)

## [0.1.0] - 2024-01-01

### Added
- Initial release of ComfyUI_prelife custom nodes
- ImageSizeAnalyzer node for analyzing image dimensions
  - Returns longer and shorter side sizes as integers
  - Category: prelife/analysis
- Project versioning infrastructure
  - `__version__` variable in package
  - `pyproject.toml` for package metadata
  - CHANGELOG.md for tracking changes
- Comprehensive README with installation instructions and documentation

