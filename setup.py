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
        "rich==13.5.2",
        "click==8.1.7",
        "chardet==5.2.0",
        "qdrant-client==1.6.0",
        "langchain==0.0.314",
        "playwright==1.38.0",
        "beautifulsoup4==4.12.2",
        "transformers==4.34.0",
        "ctransformers==0.2.27",
        "sentence_transformers==2.2.2",
        "torch==2.0.1",
        "pyjwt==2.8.0",
        "keyring==24.2.0",
        "requests==2.31.0",
        "supabase==1.2.0",
    ],
    entry_points={
        'console_scripts': [
            'mirageml=mirageml.__main__:app'
        ]
    }
)
