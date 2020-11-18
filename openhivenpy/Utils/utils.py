import logging

from operator import attrgetter
from functools import lru_cache
# This is a surprise tool that will help us later

logger = logging.getLogger(__name__) 

async def dispatch_func_if_exists(obj: object, func_name: str, *args, **kwargs):
    """`openhivenpy.utils.dispatch_func_if_exists()`
    
    Dispatches functions if they exist in the passed object else they will be ignored
    
    Parameter:
    ----------
    
    obj: `object` - Object where to search for the function
    
    func_name: `str` - Name of the function
    
    *args: `list` - *args of the function
    
    **kwargs: `dictionary` - **kwargs of the function
    
    """
    func = getattr(obj, func_name, None)
    if func != None:
        if callable(func):
            logger.debug(f"Dispatching {func_name}")
            await func(*args, **kwargs)
    else:
        logger.debug(f"{func_name} not found. Returning")
        return

def raise_value_to_type(val, data_type):
    """`openhivenpy.utils.raise_value_to_type()`
    
    Returns the value if not None else returns the empty value in the specified data type instead of None
    
    (Raises None values to the empty Type Value)
    
    Parameter:
    ----------
    
    val: `any` - Value that should be checked
    
    """
    if val == None:
        return data_type()
    else:
        return val
    

def get(iterable, **attrs):
    _all = all

    # There is only one element in the dict attrs
    if len(attrs) == 1:
        key, val = attrs.popitem()
        pred = attrgetter(key.replace('__', '.'))
         # Checks if the element exists with the same value
        for elem in iterable:
            if pred(elem) == val:
                return elem

        # Returns if it does not already exist
        return None

    converted = [
        (attrgetter(attr.replace('__', '.')), value)
        for attr, value in attrs.items()
    ]

    for elem in iterable:
        # Checks if the element exists with the same value
        if _all(pred(elem) == value for pred, value in converted):
            return elem
    # Returns if nothing is true
    return None
