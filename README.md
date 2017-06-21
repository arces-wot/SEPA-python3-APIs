# SEPA-python3-APIs
Client-side libraries for the SEPA platform (Python3)

## Installation

Go to the folder named `dist`, uncompress the archive using `tar`, then type the usual:

```python setup.py build```

and

```python setup.py install```

(this one as root).


## Low-level APIs

These APIs allows to develop a client for the SEPA platform using a low-level but simple interface. First of all the class LowLevel must be initialized. Then the standard methods to interact with the broker are available.

### Creating a LowLevelKP

Mandatory parameters are:

1. the host
2. the path to update/query the broker
3. the path to register a client
4. the path to request a token
5. the port for http connections
6. the port for https connections
7. the port for ws connections
8. the port for wss connections
9. the username
10. the log level.

Then the query, update, subscribe and unsubscribe methods are available. 

### Query and Update

These two methods (`query` and `update`) expect a SPARQL query/update and a boolean specifying whether security mechanisms should be used or not. When a new query/udpate is issued, it may be preferrable to catch the `RegistrationFailedExceptions`, `TokenExpiredException` and `TokenRequestFailedException`errors.

### Subscribe and Unsubscribe

The `subscribe` primitive requires a SPARQL query, an alias for the subscription, an handler class (containing the handle method) and the boolean referred to security. The `unsubscribe` primitive only needs to know the ID of the subscription.

## High-level APIs

The high-level APIs implement the **PAC programming pattern**. Throught this pattern, an application can be developed with very simple programs named producers, consumers or aggregator depending on their role.

### The class Producer

The class `Producer` implements a Knowledge Processor that only performs updates of the knowledge base. The class `Producer` inherits from the `KP` class. To create an instance of the class Producer:

```
p = Producer(jsapFile, jparFile)
```
The constructor requires a jsap and a jpar file: the first contains the appilcation profile, while the second the profile of the user.

To update the knowledge base we invoke the method `produce` specifying the friendly name of the update (corresponding to a given SPARQL update in the jsap file), the forced bindings in form of a Python dictionary and an optional boolean value to enable/disable the security mechanisms (default = disabled).

```
p.produce(MY_UPDATE, {"ageValue":"30"}, True)
```

### The class Consumer
The class `Consumer` implements a Knowledge Processor that only subscribes to a subgraph of the knowledge base. The class `Consumer` inherits from the `KP` class. To create an instance of the class Consumer:

```
c = Consumer(jsapFile, jparFile)
```
The constructor requires a jsap and a jpar file: the first contains the appilcation profile, while the second the profile of the user.

To start the subscription we invoke the method `consume` specifying the friendly name of the persistent query (corresponding to a given SPARQL query in the jsap file), the forced bindings in form of a Python dictionary, an alias for the final query, the handler class and an optional boolean value to enable/disable the security mechanisms (default = disabled).

```
c.consume("READ_AGE", {}, "age", BasicHandler, False)
```

### The class Aggregator

Stay Tuned!
