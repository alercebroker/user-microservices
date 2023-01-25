# User microservices for ALeRCE

Monorepo containing the APIs and related libraries for user interactions in ALeRCE.

Dependencies are managed using [poetry](https://python-poetry.org/).

## Structure

The folder `libs` contains internal libraries that can be used inside the
APIs. They should contain their own `pyproject.toml` 
file, defining their requirements and other metadata, and tests. APIs 
and libraries can depend on any library.

All other folders contain the code for its respective API. 
Each of them acts as its own Python app, with its own `pyproject.toml` file. 
It should also contain its own tests. APIs are independent of each 
other and should *never* depend on other APIs.

All packages (libraries and APIs) should have their tests in a `tests` 
folder. Unittests must be included in a subfolder called `unittests` even
if they are the only tests (this is so that the workflows can work properly).
If relevant, integration tests can be added inside a subfolder called
`integration`.

### Workflows

The GitHub workflows for this monorepo are designed to detect changes to
specific paths to limit testing and building to the relevant libraries or
APIs.

When adding a new library/API, make sure to include the paths in the 
`detect-changes.yml` filters. These should include the folder of the new
package proper, as well as all of its local dependencies (follow the 
existing examples). It is important to explicitly include the outputs, 
both at the job and workflow level, so that these variables are available
in other workflows that use them.

Inside `tests.yml`, jobs can be added for new packages, which use  
`test-template.yml` as a template. Make sure to include an `if` statement
for the corresponding filter. There are several possible inputs:
* `package` (required): Package name. It is assumed that the base folder 
  and source folder have the same name.
* `prefix` (optional): If there are extra folders between the monorepo 
  root and the base of the package, they must be included here. Note that 
  the prefix *must* end in `/` for the workflow to work. 
* `integration` (optional): Whether there are integration tests to run.
  It is `true` by default.
