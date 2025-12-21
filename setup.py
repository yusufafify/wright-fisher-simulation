from setuptools import setup, find_packages

setup(
    name="evolutionary_simulator",
    version="0.1.0",
    description="A Wright-Fisher simulator with Demes support",
    author="Your Team Name",
    packages=find_packages(),
    install_requires=[
        "demes",
        "matplotlib",
        "numpy",
        "yaml"
    ],
    python_requires=">=3.7",
)