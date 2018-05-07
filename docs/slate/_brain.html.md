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
Creates a local object for interacting with an existing BRAIN on the server.

```cpp
auto config = make_shared<bonsai::Config>(argc, argv);
auto brain = make_shared<bonsai::Brain>(config);
std::cout << brain << std::endl;
```

```python
config = bonsai_ai.Config(sys.argv)
brain = bonsai_ai.Brain(config)
print(brain)
```

| Argument | Description |
| ---      | ---         |
| `config` | Object returned by previously created `Bonsai::Config` (C++) or `bonsai_ai.Config()` (Python). |
| `name`   | BRAIN name as specified on the server. If name is empty, the BRAIN name in `config` is used instead. |

## update()
```cpp
brain.update();
```

```python
brain.update()
```
Refreshes description, status, and other information with the current state of the BRAIN on the server.
Called by default when constructing a new Brain object.

## string name()
```cpp
std::cout << brain.name() << endl;
```

```python
print(brain.name)
```

Returns the name of the BRAIN as specified when it was created.

## string description()
```cpp
std::cout << brain.description() << endl;
```

```python
print(brain.description)
```

Returns the user-provided description for the BRAIN.

## int version()
```cpp
std::cout << brain.version() << endl;
```

```python
print(brain.version)
```

Returns the current version number of the BRAIN.

## int latest_version()
```cpp
std::cout << brain.latest_version() << endl;
```

```python
print(brain.latest_version)
```

Returns latest version number of the BRAIN.

## Config config()
```cpp
std::cout << brain.config() << endl;
```

```python
print(brain.config)
```

Returns the configuration used to locate this BRAIN.

## operator<<(ostream, brain)
Prints out a representation of Brain that is useful for debugging.

**Note:** Used in C++ only. For python use `print(brain)`

| Argument  | Description |
| ---       | ---         |
| `ostream` | A std c++ stream operator. |
| `brain`   | A bonsai::Brain object to print out`. |

