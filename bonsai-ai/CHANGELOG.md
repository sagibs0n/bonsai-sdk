# Changelog

## 2.2.6
- Pin async_timeout version to 2.0.1
- #13277: Update AuthenticationError when requesting AAD workspace
- #13312: Update AAD authority to support MSA accounts

## 2.2.5
- #12658: Stop storing workspace in .aadcache, use only .bonsai
- #12704: Print helpful error messages on 403 errors in SDK
- #12503: Ripped out vendored Aria code

## 2.2.4
- Added a network log message after pong is sent
- #12423: Config class no longer accepts plane and workspace parameters

## 2.2.3
- #12310: Add check for closed websocket on pongs

## 2.2.2
- IcM/141829256: fix to prevent bonsai cli from writing .aadcache file to a local directory

## 2.2.1
- #12421: Remove ability to connect simulators using AAD (should use access keys)

## 2.2.0
- #12347: Map workspaces to API url in token cache

## 2.1.6
- #11688: Add RequestId header to all requests
- #11815  Aria telemetry
- #11930: Update sdk network logs
- #12116: Move telemetry blacklist logic into AriaWriter class
- #11945: Add support for AAD authentication

## 2.1.5
- #10269: Create and Push Inkling added to BrainAPI
- #10770: Config will not break sims when users have no permissions to write to HOME
- #11035: Update bonsai-ai to reflect new SLA
- #11096: Cleanup Simulator resources on SIGINT
- #10715: Added BrainController class
- #11352,#11281: Add Simulator.sim_id

## 2.1.4
- #10731: Added internal BrainAPI class
- #10855: Added Delete and Sims Info API to BrainAPI
- #10739: Refactor Brain to use new BrainAPI class
- #10659: Logs can be programatically disabled using bonsai_ai.logger.Logger.set_enable
- #10999: Predictor bug fix initial null state

## 2.1.3
- #10584: Bug fix for sdk writer outputting all null rows
- Changes as a result of static type checking

## 2.1.2
- #10599: Fix pongs
- #10268: Metrics + status + sample_rate API in bonsai_ai.Brain

## 2.1.1
- #10531: EofStream websocket message bug fix

## 2.1.0
- #10065: Rate counter is reset on first episode start
- #10405: Discontinue support for Python 2
- #10405: Migrate to aiohttp internals

## 2.0.20
- #9524: Fix WS read timeout log
- #8355: Fix for Config object to print clean JSON
- #9658: Config update should not fail if profile does not exist in .bonsai
- #1049: Addressed some issues in Python code that were uncovered by static analysis

## 2.0.19
- #7652 Remove redundant close code check from bonsai-ai reconnect policy
- #7801 - Add `--access-key` as an alias for `--accesskey`
- #7328: Network logs in bonsai-ai
- #7729: Added keep-alive pongs on a separate thread

## 2.0.18
- #7653: Braind service closes websocket with 1001, 3000-3099 or 4000-4099 when the Sim should not reconnect.
- #7746: Do not reconnect on ws close code 1000-1099. This is a permanent change.
- #7666: Fix bonsai-ai unit tests for Windows
- #6694: Remove warning spam in config
- #7650: Accept websocket close codes 4000-4099 to mean Do Not Reconnect
- #7648: ThreadPoolExecutor's shutdown method should not be called in OSX

## 2.0.17
- #7587 Turn PINGs on by default in bonsai-ai
- #7247: HTTP 401 and 404 should not initiate retries
- #7289: Add network timeout to brain http requests
- #7359: Fix a predictor test
- #7347: write "safe" accepted for `use_color` in config
- #7283: Add strict to tests marked with xfail

## 2.0.16
- Hotfix: `None` check in disconnect handler

## 2.0.15
- Bug fix in reconnect logic
- Add `Brain.sim_exists`
- Add guards for sim name existence/matching
- Add threading on sim calls in run loop for Unix/Windows
- Add configurable network timeout (websocket handshake)

## 2.0.14
- Improved loading of proxy settings.
- ping_interval parameters in Config
- sim_connection sends pings over specified interval
- change default retry timeout from 3000 seconds to 300 seconds.
- Added `file_path` to config
- Added input validation around ping-intervals

## 2.0.13
- Add reconnect parameters to config
- Add reconnect behavior with exponetial backoff
- Add Brain.exists and Brain.ready

## 2.0.12
- Fix bug related to default url not being set on the Config object

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
