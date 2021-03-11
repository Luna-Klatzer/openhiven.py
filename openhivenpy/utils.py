import functools
import logging
import sys
import traceback
from operator import attrgetter
from functools import cache
import inspect
import typing

from openhivenpy.exceptions import ExpectedAsyncFunction, UnknownEventError

logger = logging.getLogger(__name__)


async def dispatch_func_if_exists(obj: object,
                                  func_name: str,
                                  func_args: typing.Optional[typing.Union[list, tuple]] = (),
                                  func_kwargs: typing.Optional[dict] = {}) -> typing.Any:
    """
    Dispatches the passed functions if it can be found in the passed object instance!

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
                log_traceback(
                    level='error',
                    msg=f'Function {func.__name__} encountered an exception:',
                    suffix=f"{sys.exc_info()[0].__name__}: {e}"
                )

        else:
            raise TypeError(f"{obj.__class__.__name__} is not callable!")
    else:
        logger.debug(f"{func_name} not found! Returning")
        return


def log_traceback(level: typing.Union[str, None] = 'error',
                  msg: str = 'Traceback: ',
                  suffix: typing.Optional[str] = None):
    """
    Logs the traceback of the current exception

    :param msg: Message for the logging. Only gets printed out if logging level was correctly set
    :param level: Logger level for the exception. If '' or None it will not log any additional message
    :param suffix: Suffix message that will be appended at the end of the message. Defaults to None
    """
    tb = traceback.format_tb(sys.exc_info()[2])
    if level is not None and level != '':
        log_level = getattr(logger, level)
        if callable(log_level):
            tb_str = "".join(frame for frame in tb)
            # Fetches and prints the current traceback with the passed message
            log_level(f"{msg}\n{tb_str} {suffix if suffix else ''}\n")
    else:
        traceback.print_tb(tb)


def get(iterable, **attrs) -> typing.Any:
    """
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
        # if the elem is included!
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

    # Returns None if nothing is true
    return None


def log_validation_traceback(cls: typing.Any, data: dict, e: Exception):
    """
    Logger for a Validation Error in the module types

    :param cls: The class that failed to be created with the passed data
    :param data: Data that failed to be validated
    :param e: The Exception Instance
    """
    log_traceback(
        msg=f"Traceback of Initialisation of 'types.{cls.__name__}'",
        suffix=f" {e.__class__.__name__}: Encountered errors while validating data: \n{e}\n\nData: {data}"
    )


def convert_value(dtype: typing.Any,
                  value: typing.Any,
                  default: typing.Any = 'raise_exc') -> typing.Union[typing.Any, None]:
    """
    Return the passed value in the specified value if it is not None and does not raise an Exception
    while converting. Returns the passed default if the conversion failed

    :param dtype: The datatype the value should be returned
    :param value: The value that should be converted
    :param default: The default value that should be returned if the conversion failed, else it will raise an exception.
    :return: The converted value or the default passed value
    """
    try:
        if value is None:
            if default != 'raise_exc':
                return default
            else:
                return None
        return dtype(value)

    except Exception:
        if default == 'raise_exc':
            raise
        else:
            return default


def convertible(dtype: typing.Any, value: typing.Any) -> bool:
    """
    Returns whether the value can be converted into the specified datatype

    :param dtype: The datatype the value should be tested with
    :param value: The passed value that should be checked
    :return: True if it is convertible else False
    """
    try:
        dtype(value)
    except Exception:
        return False
    else:
        return True


def update_and_return(dictionary: dict, data: dict) -> dict:
    """
    Utilises the standard dictionary .update function but instead of
    returning None it will return the updated dictionary.

    :param dictionary: The dictionary that should be updated
    :param data: The data in dict format that should be used for the update
    :return: The updated dictionary
    """
    dictionary.update(data)
    return dictionary


@cache
def wrap_with_logging(coro: typing.Union[typing.Callable, typing.Coroutine] = None) -> typing.Callable:
    """
    Wraps a Event Listener Task and adds traceback logging and simple caching to it

    :param coro: Function that should be wrapped
    """
    def decorator(coro: typing.Union[typing.Callable, typing.Coroutine]):
        @functools.wraps(coro)
        async def wrapper(*args, **kwargs):
            try:
                return await coro(*args, **kwargs)
            except Exception as e:
                log_traceback(
                    msg=f"Traceback in function {coro.__name__}:", suffix=f"{sys.exc_info()[0].__name__}: {e}"
                )

        return wrapper  # func can still be used normally outside the event listening process

    if coro is None:
        return decorator
    else:
        return decorator(coro)
