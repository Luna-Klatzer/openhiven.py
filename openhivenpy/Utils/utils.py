from operator import attrgetter

def get(iterable, **attrs):
    _all = all

    # There is only one element in the dict attrs
    if len(attrs) == 1:
        key, val = attrs.popitem()
        pred = attrgetter(key.replace('__', '.'))
        for elem in iterable:
            if pred(elem) == val:
                return elem
            
        # Returns if nothing is true
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