# Config Class

> Example `~/.bonsai` file

```ini
[DEFAULT]
username = admin
accesskey = None
profile = dev

[dev]
url = http://localhost:5000
username = admin
accesskey = 00000000-1111-2222-3333-000000000001
```

Manages Bonsai configuration environments.
Config files can be specified in the user home directory, `~/.bonsai`,
or in a local directory. Configuration parameters can also be parsed from
the command line.

The `profile` key can be used to switch between different profiles in
one configuration file.

## Config(profile)

```python
import sys, bonsai_ai
if __name__ == "__main__":
    config = bonsai_ai.Config()
    print(config)
```

Constructs a default configuration.

| Argument | Description |
| ---      | ---         |
|`profile` | Optional `.bonsai` profile name. Will use the DEFAULT profile if not specified. |

Configurations are stored in `~/.bonsai` and `./.bonsai` configuration files.
The local configuration file overrides settings in the configuration file in the user home directory.

## Config(argv, profile)

```python
import sys, bonsai_ai
if __name__ == "__main__":
    config = bonsai_ai.Config(sys.argv)
    print(config)
```

Constructs a config by looking in the configuration files and parsing the command line arguments.
To see the list of command line arguments, pass in the `--help` flag.

| Argument  | Description |
| ---       | ---         |
| `argv`    | As passed to main(). |
| `profile` | Optional `.bonsai` profile name. Will use the DEFAULT profile if not specified. |

Unrecognized arguments will be ignored.

## accesskey

```python
my_config.accesskey == '00000000-1111-2222-3333-000000000001'
my_config.accesskey = '00000000-1111-2222-3333-000000000001'
```

Server authentication token.
Obtained from the bonsai server. You need to set it in your config.

## username

```python
my_config.username == 'alice'
my_config.username = 'alice'
```

Account user name.
The account you signed up with.

## url

```python
my_config.url == 'https://api.bons.ai'
my_config.url = 'https://api.bons.ai'
```

Server URL.
Address and port number of the bonsai server. Normally you should not need to change this.

## proxy

```python
my_config.proxy == 'myproxy:5000'
my_config.proxy = 'myproxy:5000'
```

Proxy Server.
Address and port number of the proxy server to connect through.

## brain

```python
my_config.brain == 'scarecrow'
my_config.brain = 'scarecrow'
```

BRAIN name.
Name of the BRAIN on the server.

## predict

```python
my_config.predict == True
my_config.brain = True
```

Simulator mode.
The mode in which simulators will run. True if running for prediction, false for training.

## brain_version

```python
my_config.brain_version == 0
my_config.brain_version = 0
```

BRAIN version.
The version of the brain to use when running for prediction. Set to 0 to use latest version.

## record_file

```python
my_config.record_file == "foobar.json"
my_config.record_file = "foobar.json"
```

This property defines the destination for log recording. Additionally, the format for log recording is inferred from the file extension. Currently supported options are `json` and `csv`. Missing file extension or use of an unsupported extension will result in runtime errors.

## record_enabled

```python
my_config.record_enabled == True
my_config.record_enabled = True
```

## record_format

```python
my_config.record_file == "foobar.json"
my_config.record_format == "json";
```

**Note:** This property cannot be set directly. It reflects the file extension of the currently configured `record_file`. `json` or `csv` are valid.
