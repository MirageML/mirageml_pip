# My Pip Package

This is a basic Python pip package with two commands: `hello` and `help`.

## Test locally
```
pip3 install .
```

## Build the package
```
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<token from PyPI>

# Make sure to change the version
rm -rf build/ dist/ mirageml.egg-info
python3 setup.py sdist bdist_wheel 
twine upload --repository testpypi dist/* # For Testing
twine upload dist/*                       # For Production
```

## Installation

To install the package, run the following command:

```
pip3 install -U --index-url https://test.pypi.org/simple/ mirageml
pip3 install -U mirageml
```

## Usage

### Hello Command

To use the `hello` command, run the following command:

```
mirageml hello [name]
```

Prints "Hello World"

## Dependencies

```
chardet
```
