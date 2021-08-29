# Logging and Debugging

---

openhiven.py uses to log and report issues and problems the built-in
[logging](https://docs.python.org/3/library/logging.html#module-logging) module of Python.
With logging can you can easily specify how  to log errors and customize the output.

## Specifying the Log Level

The module logging is based on multiple levels of importance that specified on the user input will
log issues lower that level. Based on the user input it will log only these errors of its own category
and higher than it. That means if `WARNING` was specified, `ERROR` and `CRITICAL` will also be logged.


The available levels for logging are:

| **Levels** | **Description** |
| ----------- | ----------- |
| `CRITICAL` | Logs only very critical errors | 
| `ERROR` | Logs only errors | 
| `WARNING` | Logs only warnings and errors in the program |
| `INFO` | Logs only vital information about the program |
| `DEBUG` | Logs every output related to the running program |

See [logging levels](https://docs.python.org/3/library/logging.html#logging-levels) for complete docs

## Simple Example of logging

To utilise logging you are only required to import the module and specify the level. That can be done in
less than two levels.

!!! Example

    ```python
    import logging
    
    logging.basicConfig(level=logging.INFO)
    ```

This code snippet will activate all logging in the range of the program. That means imported modules would also log
their information if they have logging used in their module.

The resulting log of the prior example would then look like this:

```
INFO:openhivenpy.gateway.http:[HTTP] Session was successfully created!
INFO:openhivenpy.gateway.ws:[WEBSOCKET] >> Authorizing with token
INFO:openhivenpy.gateway.ws:[WEBSOCKET] << Connection to Hiven Swarm established
INFO:openhivenpy.gateway.ws:[WEBSOCKET] >> Initialization of Client was successful!
INFO:openhivenpy.types.hiven_client:[CLIENT] Client loaded all data and is ready for usage!
```

Here, the initialization was successful, and the HivenClient connected itself to Hiven and logged no errors.

!!! Info

    `DEBUG` is excellent for tracing back issues in the program and also seeing how openhiven.py works in the 
    background. `INFO` is, on the other hand, handy for deployment and usage where the
    HivenClient should log only errors and vital information. We recommend sticking to one of these two, since 
    higher levels can possibly hide very important information that you might need later if a bug occurs!

## Advanced Logging

If you want to customise the entire output and also specify time and date, you can easily do that with the
[logging](https://docs.python.org/3/library/logging.html#module-logging) handlers. These handlers are
shipped directly with logging, and you only require to create instances of them and then pass your customisations.

```python
import logging

logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
```

With this snippet, time, level, and the name of the file would be logged as an addition to the message.
To that with the customised File Handler a log file would be created, which then would be used to save the
logs instead of just logging them onto the console.

For more customization for the [`logging.Formatter`](https://docs.python.org/3/library/logging.html#logging.Formatter)
and [`logging.FileHandler`](https://docs.python.org/3/library/logging.handlers.html#filehandler) classes 
visit the [logging](https://docs.python.org/3/library/logging.html#module-logging) documentation!