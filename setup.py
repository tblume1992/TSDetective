# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TSDetective",
    version="0.0.1",
    author="Tyler Blume",
    url="https://github.com/tblume1992/TSDetective",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description = "Investigating TS Foundation Models.",
    author_email = 't-blume@hotmail.com', 
    keywords = ['forecasting', 'time series', 'ai', 'deep learning'],
      install_requires=[           
                        'numpy',
                        'pandas',
                        'statsmodels',
                        'scikit-learn',
                        'scipy',
                        'statsforecast'
                        ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


