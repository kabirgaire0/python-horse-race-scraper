from setuptools import setup, find_packages

setup(
    name="horse-race-scraper",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",  # For web scraping with BeautifulSoup
        "pandas",          # For data manipulation
        "selenium",        # For automating web browsers
        "lxml",            # For faster XML and HTML parsing in BeautifulSoup
    ],
    entry_points={
        "console_scripts": [
            "horse-race-scraper=main:main",  # Change as per your actual entry point
        ]
    },
    author="Kabir Gaire",
    author_email="kabir.gaire123@gmail.com",
    description="A horse race data scraper",
    url="https://github.com/kabirgaire0/horse-race-scraper",  # Replace with your repository URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
