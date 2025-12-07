from setuptools import setup, find_packages

setup(
    name="codemem",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "requests",
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "codemem=codemem.cli:cli"
        ]
    }
)
