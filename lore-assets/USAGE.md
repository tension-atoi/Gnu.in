# LORE Assets Repository - Usage Guide

## Overview
This LORE repository is dedicated to storing **large binary assets** for the Gnu.in project ecosystem.

## When to Use LORE vs Git

### ✅ Use LORE for:
- **Large binaries** (>10MB): Compiled executables, libraries
- **Datasets**: Training data, test data
- **Models**: ML models, weights
- **Build artifacts**: Compilation outputs, caches
- **Media files**: Large images, videos, audio
- **Log files**: Build logs, test outputs

### ❌ Use Git for:
- **Source code**: .cpp, .h, .py, .rs, etc.
- **Configuration files**: .json, .yaml, .toml (small)
- **Documentation**: .md, .txt
- **Scripts**: .sh, .py (small)

## Basic Commands

### Add new assets
```bash
cd /home/tension_atoi/Projects/Gnu.in/lore-assets

# Add a single file
lore stage path/to/asset.bin

# Add multiple files
lore stage asset1.bin asset2.bin directory/

# Commit with identity
lore commit --identity "tension_atoi <tension_atoi@localhost>" "Add new assets"
```

### Check status
```bash
lore status
```

### View history
```bash
lore history 10  # Show last 10 commits
```

### View changes
```bash
lore diff  # Show unstaged changes
```

### Revert/Reset
```bash
# Unstage a file
lore unstage path/to/file

# Reset a file to last committed version
lore reset path/to/file
```

## Directory Structure

```
Gnu.in/lore-assets/
├── .lore/                    # LORE metadata (do not touch)
├── README.md                 # This file
├── USAGE.md                  # Usage instructions
├── builds/                   # Compiled binaries
│   ├── gnu.in-os/            # OS builds
│   ├── gnu.in-shell/         # Shell builds
│   └── ...
├── datasets/                 # Datasets
│   ├── training/             # Training data
│   └── test/                # Test data
├── models/                   # ML models
│   └── ...
├── cache/                    # Build caches
└── media/                    # Large media files
```

## Example Workflow

### Adding a new build
```bash
# 1. Build your project (outputs to builds/gnu.in-os/v1.0.0/)
cd /home/tension_atoi/Projects/Gnu.in/gnu.in-os
make release

# 2. Copy build artifacts to lore-assets
cp -r output/* /home/tension_atoi/Projects/Gnu.in/lore-assets/builds/gnu.in-os/$(date +%Y-%m-%d)/

# 3. Stage and commit
cd /home/tension_atoi/Projects/Gnu.in/lore-assets
lore stage builds/gnu.in-os/
lore commit --identity "tension_atoi <tension_atoi@localhost>" "Add gnu.in-os build $(date +%Y-%m-%d)"
```

### Adding a dataset
```bash
# 1. Download or generate dataset
wget https://example.com/dataset.tar.gz -O /tmp/dataset.tar.gz

# 2. Extract to lore-assets
tar -xzf /tmp/dataset.tar.gz -C /home/tension_atoi/Projects/Gnu.in/lore-assets/datasets/

# 3. Stage and commit
cd /home/tension_atoi/Projects/Gnu.in/lore-assets
lore stage datasets/
lore commit --identity "tension_atoi <tension_atoi@localhost>" "Add training dataset"
```

## Important Notes

1. **Identity**: Always use `--identity` flag when committing until we configure a default.

2. **Large Files**: LORE handles large files better than Git, but still be mindful of repository size.

3. **No .git**: Do NOT initialize Git in this directory. This is a pure LORE repository.

4. **Backup**: This repository is local-only. Consider setting up a LORE server for remote backup.

5. **Cleanup**: Regularly clean up old builds and caches to manage disk space.

## Repository Info

- **Repository ID**: `019ed7a0bb31781382dbda074fe51bc7`
- **Location**: `/home/tension_atoi/Projects/Gnu.in/lore-assets/`
- **Purpose**: Asset storage for Gnu.in projects
- **Created**: 2026-06-17

## Need Help?

```bash
# Full command reference
lore --help

# Repository commands
lore repository --help

# File commands
lore file --help
```
