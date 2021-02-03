import logging
import sys
import traceback
from operator import attrgetter
from functools import lru_cache
import inspect
from typing import Optional, Union, Any

# This is a surprise tool that will help us later

logger = logging.getLogger(__name__)


async def dispatch_func_if_exists(obj: object,
                                  func_name: str,
                                  func_args: Optional[Union[list, tuple]] = (),
                                  func_kwargs: Optional[dict] = {}) -> Any:
    r"""`openhivenpy.utils.dispatch_func_if_exists()`
    
    Dispatches functions if they exist in the passed object!
    
    :type func_kwargs: object
    :param obj: Object where to search for the function
    :param func_name: Name of the function
    
    :param func_args: *args of the function

    :param func_kwargs: **kwargs of the function

    :return: Returns the data of the function if it returns data and is callable else None
    
    """
    func = getattr(obj, func_name, None)
    if func is not None:
        # Checking if the func is callable:
        if callable(func):
            logger.debug(f"Dispatching '{func_name}'")
            try:
                # If the function is a coroutine it will be called as an async function
                if inspect.iscoroutinefunction(func):
                    return await func(*func_args, **func_kwargs)
                # If it's a regular function it will be called normally
                else:
                    return func(*func_args, **func_kwargs)

            except Exception as e:
                log_traceback(level='error',
                              msg=f'Function {func.__name__} encountered an exception:',
                              suffix=f"{sys.exc_info()[0].__name__}: {e}")

        else:
            raise TypeError(f"{obj.__class__.__name__} is not callable!")
    else:
        logger.debug(f"{func_name} not found! Returning")
        return


def raise_value_to_type(val: Any, data_type: type) -> Any:
    r"""`openhivenpy.utils.raise_value_to_type()`

    Returns the value if the value is not None else returns the empty value in the specified data type

    :param val: Value that should be checked

    :param data_type: Data Type

    :return: The passed value if it's not None else creates a new object with the passed datatype

    """
    if val is None:
        return data_type()
    else:
        return val


def log_traceback(level: Union[str, None] = 'error', msg: str = 'Traceback: ', suffix: str = None):
    r"""
    Logs the traceback of the current exception

    :param msg: Message for the logging. Only gets printed out if logging level was correctly set
    :param level: Logger level for the exception. If '' or None it will not use the logger module
    :param suffix: Suffix message that will be appended at the end of the message. Defaults to None
    :return: None
    """
    tb = traceback.format_tb(sys.exc_info()[2])
    if level is not None and level != '':
        log_level = getattr(logger, level)
        if callable(log_level):
            # Creating the string that will be printed out
            tb_str = "".join(frame for frame in tb)
            # Fetches and prints the current traceback with the passed message
            log_level(f"{msg}\n{tb_str} \n{suffix if suffix else ''}\n")
    else:
        traceback.print_tb(tb)


def get(iterable, **attrs) -> Any:
    r"""`openhivenpy.utils.get()`

    Fetches an object in the passed iterable if the passed attribute align!

    :param iterable: Object that should be used to search for the attrs

    :param attrs: Kwargs parameter that should align with the object

    :return: The object if it's found else None
    """
    _all = all

    # There is only one element in the dict attrs
    if len(attrs) == 1:
        # Returns the key and the val at the first index
        key, val = attrs.popitem()

        # Returns callable that returns for the passed object
        # the set attribute => passed_object.key
        pred = attrgetter(key.replace('__', '.'))

        # Checking all elements in the iterable / object
        for elem in iterable:
            if pred(elem) == val:
                return elem

        return None

    converted = [
        (attrgetter(attr.replace('__', '.')), value)
        for attr, value in attrs.items()
    ]

    for elem in iterable:
        # Returns the elem if all attrs are true => the same
        if _all(pred(elem) == value for pred, value in converted):
            return elem

    # Returns if nothing is true
    return None
