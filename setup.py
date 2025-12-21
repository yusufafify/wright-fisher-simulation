from setuptools import setup, find_packages

setup(
    name="evolutionary_simulator",
    version="1.0",
    description="A Wright-Fisher simulator with Demes support",
    author="Biomedical Data Engineer Students, CUFE",
    packages=find_packages(),
    install_requires=[
        "demes",
        "matplotlib",
        "numpy",
        "PyYAML"
    ],
    python_requires=">=3.7",
)