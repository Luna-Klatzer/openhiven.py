class HivenObject:
    """
    Base Class for all Hiven Objects
    """
    _client = None

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        # Automatically creating a list of tuples for all values
        info = [
            (attribute.replace('_', ''), value) if attribute != '_http' else None
            for attribute, value in self.__dict__.items()
        ]

        return '<{} {}>'.format(self.__class__.__name__, ' '.join('%s=%s' % t if t is not None else '' for t in info))
