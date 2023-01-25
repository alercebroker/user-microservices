# DB Handler

Library to handle database transactions.

Uses `motor` as a MongoDB client. Note that this that most
transactions are asynchronous.

## Connections

Connection to the database are mediated by `MongoConnection`.
This must be initialized with a configuration dictionary which requires
the following keys (it is case-insensitive):
* `username`: Username used when connecting to the database.
* `password`: Corresponding password for the user.
* `host`: IP address or hostname where the MongoDB instance is running.
* `port`: Port where the MongoDB instance is listening (as integer).
* `database`: Database name where reading/writing will take place

Missing one of the above keys will automatically fail, but additional 
keys may be passed along which will be used when connecting. These can
be any argument accepted by 
[MongoClient](https://pymongo.readthedocs.io/en/4.3.2/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient).

Note that the connection is not established during construction, but must
be explicitly established using the `connect` method.

## Models

Most transactions expect a model as their first argument. These are
special `pydantic` models, which include a `__tablename__` attribute which 
in turn corresponds to the collection associated with that model.

Although any model with the `__tablename__` attribute can work in this
regard, it is recommended to use `ModelMetaclass` as their metaclass.
This is so that the method `create_db` can ensure their creation (if 
they do not exist) and the creation of indexes defined in the attribute
`__indexes__`.
