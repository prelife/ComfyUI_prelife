# ComfyUI_prelife

A collection of custom nodes for ComfyUI focused on image analysis and preprocessing.

## Version

Current version: **0.1.0**

## Installation

### Manual Installation

1. Clone this repository into your ComfyUI `custom_nodes` directory:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/prelife/ComfyUI_prelife.git
   ```

2. Restart ComfyUI

### Using Comfy CLI

```bash
comfy node install ComfyUI_prelife
```

## Nodes

### ImageSizeAnalyzer

Analyzes image dimensions and returns the longer and shorter side sizes.

- **Category**: prelife/analysis
- **Inputs**: 
  - `image` (IMAGE): Input image tensor
- **Outputs**: 
  - `longer_side` (INT): The longer dimension of the image
  - `shorter_side` (INT): The shorter dimension of the image

## Requirements

- Python >= 3.8
- ComfyUI

## Development

This project follows semantic versioning. See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.