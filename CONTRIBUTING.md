# Contributing to MirageML

Thank you for your interest in contributing to MirageML! This document will provide you with all the necessary information to get started.

## Setting Up Your Environment

First, clone the repository and navigate into it:

```
git clone https://github.com/MirageML/mirageml_pip.git
cd mirageml
```

Then, install the package locally for development:

```
pip3 install -e .
```

<!-- ## Running Tests

To ensure that your changes do not break existing functionality, please run the tests before submitting a pull request. You can run the tests with the following command:

```
pytest
``` -->

## Submitting a Pull Request

Once you have made your changes and all tests pass, you can submit a pull request. Please provide a clear and concise description of your changes in the pull request description.

Before creating a pull request, make sure to format your code using Black and ruff. You can do this with the following commands:

```
black .
ruff . --fix
```

## Dependencies

Use `requirements.dev.txt` to install all dependencies for development. You can do this with the following command:

```
pip3 install -r requirements.dev.txt
```

For a complete list of dependencies, please refer to the [setup.cfg](https://github.com/MirageML/mirageml_pip/blob/main/setup.cfg) file.


Please make sure to update this list if you add or remove any dependencies in your pull request.

Thank you again for your contribution!
