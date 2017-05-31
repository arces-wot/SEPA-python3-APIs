# SEPA-python3-APIs
Client-side libraries for the SEPA platform (Python3)

## Low-level APIs

These APIs allows to develop a client for the SEPA platform using a low-level but simple interface. First of all the class LowLevel must be initialized.
Mandatory parameters are the host, the paths (to update/query the broker, to register a client, to request a token), the ports (for http, https, ws and wss), then the username and the log level.
Then the query, update, subscribe and unsubscribe methods are available. The first two methods expects a SPARQL query/update and a boolean specifying whether security mechanisms should be used or not.
The subscribe primitive requires a SPARQL query, an alias for the subscription, an handler class (containing the handle method) and the boolean referred to security.
The unsubscribe primitive only needs to know the ID of the subscription.

## High-level APIs

Not yet available.
