# User microservices for ALeRCE

Monorepo containing the APIs and related libraries for user interactions in ALeRCE.

Dependencies are managed using [poetry](https://python-poetry.org/).

## Structure

The folder `libs` contains internal libraries that can be used inside the
APIs. As with the projects, they should contain their own `pyproject.toml` 
file and tests. Projects and libraries can depend on any library.

All other folders contain the code for its respective API. 
Each of them acts as its own Python app, with its own `pyproject.toml` file
detailing metadata and requirements. It should also contain its own 
tests. Each API is independent of each other and should *never* depend
on other APIs.
