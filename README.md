# ComfyUI_prelife

A collection of custom nodes for ComfyUI focused on image analysis and preprocessing, built with the modern V3 API.

## Version

Current version: **0.2.0** (V3 API)

## Features

- ✅ Modern V3 API implementation
- ✅ Type-safe node definitions with schema validation
- ✅ Batch processing support
- ✅ Input validation
- ✅ Comprehensive documentation and tooltips

## Installation

### Manual Installation

1. Clone this repository into your ComfyUI `custom_nodes` directory:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/prelife/ComfyUI_prelife.git
   ```

2. Install dependencies:
   ```bash
   pip install -e ComfyUI/custom_nodes/ComfyUI_prelife
   ```

3. Restart ComfyUI

### Using Comfy CLI

```bash
comfy node install ComfyUI_prelife
```

## Nodes

### ImageSizeAnalyzer

Analyzes image dimensions and returns the longer and shorter side sizes for each image in a batch.

- **Category**: prelife/analysis
- **Inputs**: 
  - `image` (IMAGE): Input image tensor with shape [B, H, W, C]
- **Outputs**: 
  - `longer_side` (INT): The longer dimension (max of height and width) for each image in the batch
  - `shorter_side` (INT): The shorter dimension (min of height and width) for each image in the batch

#### Example Usage

The node processes images in batches and returns a list of dimensions:

```python
# Input: image tensor with shape [2, 512, 768, 3] (batch of 2 images)
# Output: 
#   longer_side: [768, 768]
#   shorter_side: [512, 512]
```

## Requirements

- Python >= 3.10
- ComfyUI (with V3 API support)
- torch >= 2.0.0
- numpy >= 1.20.0

## Development

This project uses the modern ComfyUI V3 API for node development. Key features:

- Schema-based node definitions using `io.Schema`
- Type-safe inputs and outputs
- Built-in input validation via `validate_inputs()`
- Proper batch processing support

See [doc/for_llm.md](doc/for_llm.md) for detailed development guidelines.

This project follows semantic versioning. See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.