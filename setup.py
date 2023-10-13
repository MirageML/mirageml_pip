from setuptools import setup, find_packages

setup(
    name='mirageml',
    version='0.0.11',
    author='Aman Kishore',
    author_email='aman@mirageml.com',
    description='A basic pip package with basic commands like help and hello world',
    packages=find_packages(),
    install_requires=[
        # List your package's dependencies here
        "chardet==5.2.0",
    ],
    entry_points={
        'console_scripts': [
            'mirageml=mirageml_pip.__main__:main'
        ]
    }
)