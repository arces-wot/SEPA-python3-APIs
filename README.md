# SEPA-python3-APIs
Client-side libraries for the SEPA platform (Python3)

## Installation

Go to the folder named `dist`, uncompress the archive using `tar`, then type the usual:

```python setup.py build```

and

```python setup.py install```

(this one as root).


## SEPAClient

These APIs allows to develop a client for the SEPA platform using a simple interface. First of all the class SEPAClient must be initialized. Then the standard methods to interact with the broker are available.

### Creating a SEPAClient

```python
sc = SEPAClient()
```

(optional parameters are the path for a JPAR file to exploit security mechanisms or the log level that defaults to 40). Then the query, update, subscribe and unsubscribe methods are available. 

### Query and Update

These two methods (`query` and `update`) expect the SEPA URI, a SPARQL query/update and a boolean specifying whether security mechanisms should be used or not. When a new query/update is issued, it may be preferrable to catch the `RegistrationFailedExceptions`, `TokenExpiredException` and `TokenRequestFailedException`errors.

### Subscribe and Unsubscribe

The `subscribe` primitive requires a SPARQL query, an alias for the subscription, an handler class (containing the handle method) and the boolean referred to security. The `unsubscribe` primitive only needs to know the ID of the subscription.

## YSAPObject and JSAPObject

This package supports both Semantic Application Profiles encoded with YAML or JSON. Simply create an instance of the desired class and exploits the methods to get a query/update with the provided forced bindings.

## Something else?

Yes, (almost) all the code is documented through pydoc, so if you want, you can get the full documentation of attributes and methods. For example with:

```
pydoc sepy.YSAPObject
```

Stay Tuned!
