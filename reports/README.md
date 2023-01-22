# Reports API

## Development

Install everything using poetry:
```commandline
poetry install
```

To run unit tests:
```commandline
poetry run pytest tests/unittest
```

To run integration tests:
```commandline
poetry run pytest tests/integration
```

In order to run the API locally, first you need to have
a MongoDB instance to connect to. It is possible to use the same 
database used for running the integration tests by running:
```commandline
docker compose -f tests/docker-compose.yml up -d
```
If the MongoDB image is up, it won't be possible to run the integration 
tests. To stop the container, run:
```commandline
docker compose -f tests/docker-compose.yml down
```
When running the container, the database already comes with a few
mock reports already inserted.

Afterwards, you can run the API using:
```commandline
uvicorn reports.main:app --reload
```
The `--reload` option allows for changes done in the source code to
be detected and restart the API to reflect those changes automatically.
When running the API in this way, it will use the values in `.env.test`
to initialize the database connection. In a standard run, it should use 
proper environmental variables to define the settings.

The environmental variables required are:
* `MONGODB_HOST`: IP or host name for MongoDB
* `MONGODB_PORT`: Port used by MongoDB
* `MONGODB_USERNAME`: Username to connect to the database
* `MONGODB_PASSWORD`: Password for the given user
* `MONGODB_DATABASE`: Name of the database the contains the collections of interest

**Note:** The docker image must be built from the root of the monorepo, 
not from the location of the `Dockerfile`.

### Structure

#### `reports.database`

Inside `models`, the document models for the collections used 
within the API should be defined. These *must* follow the instructions 
for model creation defined in the library `db_handler`, so that the 
collections are properly initialized by the database connection.
If the collection already exists, it won't be overwritten. This step
mostly ensures that the proper indexes are created.

The `_getters` module has simple functions to get the 
database settings and connections on demand. Note that, by using the cache,
only the first call will be considered, even if settings might have changed
in the middle of the run.

#### `reports.schemas`

Here the input and/or output schemas are defined.
All these should be subclasses of `BaseModel` from `pydantic`. To create
schemas derived directly from the database models, follow the instructions 
provided by the `db_handler` library.

The submodules are organized according to the type of basic model contained.

#### `reports.filters`

Here the general query parameters are defined. These 
should inherit from the `query` library whenever possible, particularly 
if they'll be used for directly querying the database. Thus, most
filters should be `pydantic` dataclasses.

#### `reports.routes`

This module defines the API routes, most commonly using the database
connection to extrac the data of interest.

#### `reports.settings`

Any settings that require the reading of environmental variables or files
must be defined here. It is recommended to subclass `BaseSettings` from 
`pydantic` if more specific settings are needed.

#### `reports.main`

Here is where the app proper is defined. Mainly, it attaches the route and
defines actions for startup or shutdown. Also includes some general error 
handling.
