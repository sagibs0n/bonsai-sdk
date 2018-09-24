# Brain Class

Manages a BRAIN instance, talks with the server backend, and contains
information about the BRAIN state. In future versions will be used to upload
and download Inkling to and from the BRAIN on the server.

Requires a configuration and a BRAIN name. The BRAIN name can be set in
several places, and there is an order of what takes precedence over the other as follows:

Brain() >> --brain >> .brains >> .bonsai[profile] >> .bonsai[DEFAULT] >> env[BONSAI_TRAIN_BRAIN]

such that ">>" indicates a decreasing order of precedence. Note that failure to set
BRAIN name in at least one of these places will result in a friendly error.

## Brain(config, name)

```python
config = bonsai_ai.Config(sys.argv)
brain = bonsai_ai.Brain(config)
print(brain)
```

Creates a local object for interacting with an existing BRAIN on the server.

| Argument | Description |
| ---      | ---         |
| `config` | Object returned by previously created `bonsai_ai.Config`. |
| `name`   | BRAIN name as specified on the server. If name is empty, the BRAIN name in `config` is used instead. |

## update()

```python
brain.update()
```

Refreshes description, status, and other information with the current state of the BRAIN on the server.
Called by default when constructing a new Brain object.

## name

```python
print(brain.name)
```

Returns the name of the BRAIN as specified when it was created.

## description

```python
print(brain.description)
```

Returns the user-provided description for the BRAIN.

## exists

```python
if brain.exists:
    ...
```

Returns a boolean indicating whether a BRAIN with this name exists for
this user. In predict mode, also checks whether the configured BRAIN
version exists.

## ready

```python
if brain.exists and brain.ready:
    ...
```

Returns a boolean indicating whether this BRAIN is ready for training.

## state

```python
print(brain.state)
```

Returns the server-side state of this BRAIN.

## version

```python
print(brain.version)
```

Returns the current version number of the BRAIN.

## latest_version

```python
print(brain.latest_version)
```

Returns latest version number of the BRAIN.

## Config config

```python
print(brain.config)
```

Returns the configuration used to locate this BRAIN.

