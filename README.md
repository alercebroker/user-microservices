# User microservices for ALeRCE

Monorepo containing the APIs and related libraries for user interactions in ALeRCE.

Dependencies are managed using [poetry](https://python-poetry.org/).

## Structure

The folder `projects` contains folders for each API in this monorepo. 
Each of them acts as its own Python app, with its own `pyproject.toml` file
detailing metadata and requirements among others. It should also contain its own 
tests. Each project is independent of each other and should *never* depend
on other projects.

The folder `libs` contains internal libraries that can be used inside the
projects. As with the projects, they should contain their own `pyproject.toml` 
file and tests. Projects and libraries can depend on any library.
