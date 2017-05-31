# SEPA-python3-APIs
Client-side libraries for the SEPA platform (Python3)

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

The `subscribe` primitive requires a SPARQL query, an alias for the subscription, an handler class (containing the handle method) and the boolean referred to security. The unsubscribe primitive only needs to know the ID of the subscription.

## High-level APIs

Not yet available.
