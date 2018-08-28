# Changelog

## 2.0.11
- Flush record buffer on every call to `run`
- Improved config file error reporting
- Generate `FinishedEvent` in response to server errors
- Log Sim ID to the console immediately after registration
- Fix Config bug involving `DEFAULT` profile
- Added `use_color` flag to Config
- Fix bug where default url was getting assigned before config is parsed
- Fix Config tests
- Added `Brain.exists` and `Brain.state` for better status checking

## 2.0.10
- Fix sequencing bug in predict mode

## 2.0.9
- Make testing logs quieter
- update http to https for all setup.py

## 2.0.8
- Event pump API (feature parity with libbonsai)

## 2.0.7
- Fixed sequencing in prediction mode after terminal conditions.
- Fixed IOLoop collision when running in Jupyter
- Reliability improvements in analytics recorder

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
