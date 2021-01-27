import logging
from operator import attrgetter
from functools import lru_cache
import inspect
from typing import Optional, Union, Any

# This is a surprise tool that will help us later

logger = logging.getLogger(__name__)


async def dispatch_func_if_exists(obj: object,
                                  func_name: str,
                                  *args: Optional[Union[list, tuple]],
                                  **kwargs: Optional[dict]):
    r"""`openhivenpy.utils.dispatch_func_if_exists()`
    
    Dispatches functions if they exist in the passed object!
    
    :param obj: Object where to search for the function
    
    :param func_name: Name of the function
    
    :param args: *args of the function

    :param kwargs: **kwargs of the function

    :return: Returns the data of the function if it returns data and is callable else None
    
    """
    func = getattr(obj, func_name, None)
    if func is not None:
        # Checking if the func is callable:
        if callable(func):
            logger.debug(f"Dispatching '{func_name}'")

            # If the function is a coroutine it will be called as an async function
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)

            # If it's a regular function it will be called normally
            else:
                return func(*args, **kwargs)
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


def get(iterable, **attrs) -> Any:
    r"""

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
