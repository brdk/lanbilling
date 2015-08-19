LANBilling
--------

To use, simply do::

    >>> from lanbilling import LANBilling
    >>> lbapi = LANBilling(manager='admin', password='', host='127.0.0.1', port=1502)
    >>> account = lbapi.getAccount({'uid': 1})

To show all possible methods::

    >>> lbapi.help()

To get help for method usage::

    >>> lbapi.help('getAccount')

