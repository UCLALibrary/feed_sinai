# feed_sinai

Command line tool to load JSON content into a Solr index for the [Sinai Manuscripts Digital Library](https://digital.library.ucla.edu/) site.

## Using feed_sinai

For basic use, you can install feed_sinai as a systemwide command directly from pypi, without having to first clone the repository.

### Installation

We recommend installing with [pipx](https://pipx.pypa.io/). On MacOS, you can install pipx (and python!) with [homebrew](https://brew.sh):

```
brew install pipx pyenv
pipx ensurepath
```

Then:

```
pipx install feed_sinai
```

Pipx will install feed_sinai in its own virtualenv, but make the command accessible from anywhere so you don't need to active the virtualenv yourself.

For JSON data to load, clone [https://github.com/uclalibrary/sinaiportal_data](https://github.com/uclalibrary/sinaiportal_data):
```
git clone git@github.com:UCLALibrary/feed_ursus.git
```

### Export JSON

The [https://github.com/uclalibrary/sinaiportal_data](https://github.com/uclalibrary/sinaiportal_data) document data is spread across many files of different types. To merge these into a single nested JSON file per manuscript:
```
sinai export [path/to/repo/sinaiportal_data]
```

### Load to Solr

This repo includes a docker-compose.yml file that will run local instances of solr and the sinaimanuscripts site for use in testing this script. To use them, first install [docker](https://docs.docker.com/install/) and [docker compose](https://docs.docker.com/compose/install/). Then run:

```
docker-compose up --detach
docker-compose run web bundle exec rails db:setup
```

It might take a minute or so for solr to get up and running, at which point you should be able to see your new site at http://localhost:3000. Ursus will be empty, because you haven't loaded any data yet.

To load data from a csv:

```
sinai load [path/to/repo/sinaiportal_data]
```

This will use the default URL for a solr instance, you can change this with the `--solr_url` option.
```
sinai load --solr_url=http://localhost:8983/solr/californica [path/to/repo/sinaiportal_data]
```

## Developing feed_sinai

### Installing

For development, clone the repository and use uv to set up the virtualenv:

```
git clone git@github.com:UCLALibrary/feed_sinai.git
cd feed_sinai
pipx install uv
uv sync
```

Then, to activate the virtualenv:

```
source .venv/bin/activate
```

The following will assume the virtualenv is active. You could also run e.g. `uv run -- sinai [...]`

### Using the development version

Same as when installed with pipx, once you've activated the virtualenv:
```
sinai load [path/to/repo/sinaiportal_data]
```

### Running the tests

Tests are written for [pytest](https://docs.pytest.org/en/latest/):

```
pytest
```

### Running the formatter and linters:

black (formatter) will run in check mode in ci, so make sure you run it before committing:

```
black .
```

flake8 (linter) isn't currently running in ci, but should be put back in soon:

```
flake8
```

pylint (linter) isn't currently running in ci, but should be put back in soon:

```
pylint
```

mypy (static type checker) isn't currently running in ci, but should be put back in soon:

```
mypy
```

### VSCode Debugger Configuration

To debug with VSCode, make sure the .venv folder was created within the project directory (I think this is the uv default).

Add an appropriate `.vscode/launch.json`, this assumes you have the python debugger extension installed.

```
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Run the feed_ursus module",
            "type": "debugpy",
            "request": "launch",
            "cwd": "${workspaceFolder}",
            "console": "integratedTerminal",
            "module": "feed_ursus.feed_ursus",
            "justMyCode": true,
        }
    ]
}
```

# Caveats

## IIIF Manifests

When importing a work, the script will always assume that a IIIF manifest exists at https://iiif.library.ucla.edu/[ark]/manifest, where [ark] is the URL-encoded Archival Resource Key of the work. This link should work, as long as a manifest has been pushed to that location by importing the work into [Fester](https://github.com/UCLALibrary/fester) or [Californica](https://github.com/UCLALibrary/californica). If you haven't done one of those, obviously, the link will fail and the image won't be visible, but metadata will import and be visible. A manifest can then be created and pushed to the expected location without re-running feed_ursus.py.
