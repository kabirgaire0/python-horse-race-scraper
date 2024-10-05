from setuptools import setup, find_packages

setup(
    name="my_program",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'bs4',       # Specify required packages
        'selenium',
        'pandas',
        'scraper',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'my_program=my_program.main:main',  # Optional: define how to run your program
        ],
    },
)
