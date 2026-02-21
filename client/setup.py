from setuptools import setup, find_packages

setup(
    name="federx-client",
    version="1.0.0",
    description="FederX Federated Learning Client SDK",
    author="FederX Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.32.0",
        "numpy>=1.26.0",
        "torch>=2.5.0",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
