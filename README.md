# SEPA-python3-APIs
Client-side libraries for the SEPA platform (Python3)

## Installation and usage

Go to the folder named `dist`, uncompress the archive using `tar`, then type the usual:

```python setup.py build```

and

```python setup.py install```

(this one as root).

To use the classes you have to import them in this way:

```
from sepy.<the class you want to import> import *
```

For example, if you want to import the JSAPObject (used to handle JSAP files) you have to write:

```python
from sepy.JSAPObject import *
```

This library consists of 11 modules that can be used for different purposes:

- JPARHandler: An handler class for JPAR files
- JSAPObject: An handler class for JSAP files
- YSAPObject: An handler class for YSAP files
- SEPAClient: A low-level class used to develop a client for SEPA
- ConnectionHandler: A class for connection handling
- Exceptions
- YSparqlObject: A class dealing with the yaml description of SPARQL
- utils: Some methods useful in plenty of situations when dealing with SEPA results
- tablaze: A runnable script (also callable as a function, to nicely print SEPA output)
- SubscriptionHandler: A basic handler to use subscriptions with SEPA
- Sepa: The higher-level class corresponding to SEPAClient

Let's talk about some classes deeply:

## SEPAClient

These APIs allows to develop a client for the SEPA platform using a simple interface. First of all the class SEPAClient must be initialized. Then the standard methods to interact with the broker are available.

### Parameters:
- jparFile :
  A string indicating the name with relative/full path of the JPAR file used to exploit the security mechanism. Default = None
- logLevel :
  A number indicating the desired log level. Default = 40
The parameters are optional. They activate query, update, subscribe, unsubscribe methods.

### Attributes:
- subscriptions :
  A dictionary to keep track of the active subscriptions
- connectionManager :
  The underlying responsible for network connections

### Creating a SEPAClient

```python
sc = SEPAClient()
```

### Query and Update

These two methods (`query` and `update`) expect the SEPA URI, a SPARQL query/update and a boolean specifying whether security mechanisms should be used or not. When a new query/update is issued, it may be preferrable to catch the `RegistrationFailedExceptions`, `TokenExpiredException` and `TokenRequestFailedException`errors.

### Subscribe and Unsubscribe

The `subscribe` primitive requires a SPARQL query, an alias for the subscription, an handler class (containing the handle method) and the boolean referred to security. The `unsubscribe` primitive only needs to know the ID of the subscription.

## YSAPObject and JSAPObject

This package supports both Semantic Application Profiles encoded with YAML or JSON. Simply create an instance of the desired class and exploits the methods to get a query/update with the provided forced bindings.

## Something else?

Yes, (almost) all the code is documented through pydoc, so if you want, you can get the full documentation of attributes and methods. For example from prompt write:

```
python -m pydoc sepy.YSAPObject
```

## Foreseen changes

I will update tests and I will modify YSAPObject class in order to automatically add prefixes to queries/updates!

Stay Tuned!
