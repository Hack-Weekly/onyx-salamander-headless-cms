# Onyx Settings
An Onyx Settings files contains all of the configuration of your Onyx installation. This document explains how settings work and which settings are available.

## The Basics
A settings file is just a Python module with module-level variables. Here are a couple of example settings:
``` py
ALLOWED_HOSTS = ["www.example.com"]
DEBUG = False
```
Because a settings file is a Python module, your settings file must be syntactically correct, and can be used to assign settings dynamically. Also, it can import settings from other files

## Accessing Settings
You can access Onyx Settings in your app and add custom settings to the file.

In order to access Onyx Settings in a custom module, it's recommended you use the relative import:

```python
from onyx import settings
```

Then, you can access your 
setting like so:

```python
settings.YOUR_SETTING
```
