from setuptools import setup, find_packages

setup(
    name='mirageml',
    version='0.0.11',
    author='Mirage ML Inc',
    author_email='support@mirageml.com',
    description='A basic pip package with basic commands like help and hello world',
    packages=find_packages(),
    install_requires=[
        # List your package's dependencies here
        "chardet==5.2.0",
        "qdrant-client==1.6.0",
        "langchain==0.0.314",
        "playwright==1.38.0",
        "beautifulsoup4==4.12.2",
        "transformers==4.34.0",
        "sentence_transformers==2.2.2",
        "torch==2.0.1",
    ],
    entry_points={
        'console_scripts': [
            'mirageml=mirageml.__main__:main'
        ]
    }
)
