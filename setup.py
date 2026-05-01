from setuptools import setup, find_packages

setup(
    name="camc",
    version="0.1.0",
    description="Chaotic Associative Memory Cryptography - Research PoC",
    author="YOUR_NAME",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.26.0",
        "scipy>=1.14.0",
        "numba>=0.60.0",
    ],
    python_requires=">=3.10",
)