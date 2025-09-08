# trading-platform
An end to end trading platform :)

1. the order placed by a user will be cleared when the user is deleted. this can be changed or fixed in the future
2. If you run Alembic inside a container or in a service that’s networked with the DB container, DB_HOST might be db (the Docker service name). For local host-based runs, localhost is correct because you mapped the port.
3. while defining the schema for stocks, i used float. decimal would have been a better option for enhanced precision
4. for the matching engine, improvements could be made by using kafka or any messaging queues so that matching is deterministic
