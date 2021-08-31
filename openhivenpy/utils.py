import inspect
import logging
import sys
import traceback
import warnings
from functools import wraps
from operator import attrgetter
from types import TracebackType
from typing import (Union, Awaitable, Callable, Any, Optional, NoReturn, Type,
                    Tuple, Iterable)

from .exceptions import InitializationError

logger = logging.getLogger(__name__)


def log_type_exception(obj_type=None):
    """ Logs an exception when received during type initialisation """
    def _actual_decorator(func):
        @wraps(func)
        def _decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_traceback(
                    brief=f"Failed to initialise {obj_type}:",
                    exc_info=sys.exc_info()
                )
                raise InitializationError(
                    f"Failed to initialise {obj_type}"
                ) from e

        return _decorated

    return _actual_decorator


def deprecated(instead=None):
    """
    Warns the user about a function or tool that is deprecated and shouldn't
    be used anymore
    """

    def _actual_decorator(func):
        @wraps(func)
        def _decorated(*args, **kwargs):
            # turn off filter
            warnings.simplefilter('always', DeprecationWarning)
            if instead:
                fmt = "{0.__name__} is deprecated, use {1} instead."
            else:
                fmt = '{0.__name__} is deprecated.'

            warnings.warn(
                fmt.format(func, instead),
                stacklevel=3,
                category=DeprecationWarning
            )
            # reset filter
            warnings.simplefilter('default', DeprecationWarning)
            return func(*args, **kwargs)

        return _decorated

    return _actual_decorator


def fetch_func(obj: object, func_name: str) -> Union[Awaitable, Callable, None]:
    """
    Fetches a function inside an object and will return the callable. If the
    object is not a function it will raise an exception

    :param obj: Object where to search for the function
    :param func_name: Name of the function
    :return: Returns the function/coro itself
    """
    func = getattr(obj, func_name, None)
    if func:
        if callable(func):
            return func
        else:
            raise TypeError(f"{obj.__class__.__name__} is not callable!")
    else:
        logger.debug(f"{func_name} not found! Returning")
        return None


async def dispatch_coro_if_exists(
        obj: object,
        func_name: str,
        func_args: Optional[Union[list, tuple]] = None,
        func_kwargs: Optional[dict] = None
) -> Any:
    """
    Dispatches the passed functions if it can be found in the passed object
    instance!

    If the function is not async it will still call it and return the
    function data if any are returned

    :param obj: Object where to search for the function
    :param func_name: Name of the function
    :param func_args: *args of the function
    :param func_kwargs: **kwargs of the function
    :return: Returns the data of the function if it returns data and is
     callable else None
    """
    if func_args is None:
        func_args = ()
    if func_kwargs is None:
        func_kwargs = {}

    func = fetch_func(obj, func_name)
    if func:
        if inspect.iscoroutinefunction(func):
            return await wrap_with_logging(func)(*func_args, **func_kwargs)
        else:
            return wrap_with_logging(func)(*func_args, **func_kwargs)
    else:
        return None


def dispatch_func_if_exists(
        obj: object,
        func_name: str,
        func_args: Optional[Union[list, tuple]] = None,
        func_kwargs: Optional[dict] = None
) -> Any:
    """
    Dispatches the passed functions if it can be found in the passed object
    instance!

    :param obj: Object where to search for the function
    :param func_name: Name of the function
    :param func_args: *args of the function
    :param func_kwargs: **kwargs of the function
    :return: Returns the data of the function if it returns data and is
     callable else None
    """
    if func_args is None:
        func_args = ()
    if func_kwargs is None:
        func_kwargs = {}
    func = fetch_func(obj, func_name)
    if func:
        return wrap_with_logging(func)(*func_args, **func_kwargs)
    else:
        return None


def log_traceback(
        level: Optional[str] = 'error',
        brief: Optional[str] = None,
        exc_info: Tuple[Type[BaseException], BaseException, TracebackType] = sys.exc_info()
) -> None:
    """
    Logs the traceback of the latest exception

    :param level: Logger level for the exception
    :param brief: Small message that will be logged before the traceback
    :param exc_info: The exc_info containing the exception and the traceback
    """
    tb = traceback.format_exception(
        etype=exc_info[0],
        value=exc_info[1],
        tb=exc_info[2]
    )

    log_level: Callable = getattr(logger, level, None)
    if log_level is None and not callable(log_level):
        raise ValueError("The passed level does not exist in the logging module!")

    tb_str = "".join(frame for frame in tb)
    brief = brief if brief is not None else ""

    # Fetches and prints the current traceback with the passed message
    log_level(f"{brief}\n\n{tb_str}\n")


def get(iterable: Iterable, **attrs) -> Any:
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


def log_validation_traceback(
        cls: Any,
        data: dict,
        exc_info: Tuple[Type[BaseException], BaseException, TracebackType] = sys.exc_info()
) -> None:
    """
    Logger for a Validation Error in the module types

    :param cls: The class that failed to be created with the passed data
    :param data: Data that failed to be validated
    :param exc_info: The exc_info provided by sys.exc_info(). This will be used
     to log the traceback and information about the exception
    """
    log_traceback(
        brief=f"Ignoring Exception in Validation of 'types.{cls.__name__}'",
        exc_info=exc_info
    )
    logger.error(f"\nData: {data}")


MISSING = object()


def safe_convert(
        dtype: Any, value: Any, default: Optional[Any] = MISSING
) -> Union[Any, None]:
    """
    Converts the passed value. If the conversion fails or the value is None
    it will simply return the default if it not (the default) MISSING. If
    that's the case:
    - if it failed due to conversion error it will reraise the Exception.
    - else if the value was None it will return None as well.

    :param dtype: The datatype the value should be returned
    :param value: The value that should be converted
    :param default: The default value that should be returned if the conversion
     failed
    :return: The converted value or the default passed value
    :raises Exception: If default is MISSING and the conversion raised an
     exception.
    """
    try:
        if value is None:
            if default is not MISSING:
                return default
            else:
                return None

        return dtype(value)

    except Exception:
        if default == MISSING:
            raise
        else:
            return default


def convertible(dtype: Any, value: Any) -> bool:
    """
    Returns whether the value can be converted into the specified datatype

    :param dtype: The datatype the value should be tested with
    :param value: The passed value that should be checked
    :return: True if it is convertible else False
    """
    try:
        dtype(value)
    except (ValueError, TypeError):
        return False
    else:
        return True


def update_and_return(dictionary: dict, **kwargs) -> dict:
    """
    Utilises the standard dictionary update() function but instead of
    returning None it will return the updated dictionary.

    :param dictionary: The dictionary that should be updated
    :param kwargs: Kwargs of the update method
    :return: The updated dictionary
    """
    dictionary.update(**kwargs)
    return dictionary


def wrap_with_logging(
        func: Union[Callable, Awaitable] = None,
        return_exception: bool = False
) -> Union[Callable, Awaitable]:
    """
    Wraps a function and adds traceback logging

    :param func: Function that should be wrapped
    :param return_exception: If set to True the exception will be reraised
    """

    def decorator(func: Union[Callable, Awaitable]) -> Callable:
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Union[Any, NoReturn]:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    log_traceback(
                        brief=f"{'' if return_exception else 'Ignoring'} "
                              f"Exception in coroutine {func.__name__}:",
                        exc_info=sys.exc_info()
                    )
                    if return_exception:
                        raise RuntimeError(
                            f"Failed to execute coroutine {func.__name__}"
                        ) from e
        else:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Union[Any, NoReturn]:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    log_traceback(
                        brief=f"{'' if return_exception else 'Ignoring'} "
                              f"Exception in function {func.__name__}:",
                        exc_info=sys.exc_info()
                    )
                    if return_exception:
                        raise RuntimeError(
                            f"Failed to execute function {func.__name__}"
                        ) from e

        return wrapper  # func can still be used normally

    if func is None:
        return decorator
    else:
        return decorator(func)
