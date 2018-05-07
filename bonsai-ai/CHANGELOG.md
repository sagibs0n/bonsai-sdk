# Changelog

## 2.0.6
- Recording file controllable on a per-Sim basis
- Adds a mechanism to uniformly record simulation data to a file
- change README files to use reStructuredText instead of Markdown, per pip standards

## 2.0.5
- `Predictor` added to bonsai-ai
- `bonsai-cli` is now a requirement for bonsai-ai
- Add statistics collection and introduce an `episode_finish()` callback
- Added `wheel` as a requirement for bonsai-ai
- `Predictor` context manager bug fix
- Add mechanisms (library, config, command line) to record simulation data to a file.

## 2.0.4
- `Config.verbose` field to enable/disable verbose logging
- Updated Config to be used in the cli

## 2.0.3
- User-Agent added to bonsai-ai requests
- Adds logging module

## 2.0.2
- Fix for objective_name returning None

## 2.0.1
- Updated doc strings
- Added missing Simulator properties

## 2.0.0
- Initial release
