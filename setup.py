import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

with open("requirements.txt") as file:
    requirements = file.read()

setuptools.setup(
    name="openhivenpy", 
    version="0.1",
    author="FrostbyteSpace",
    author_email="nicolas.klatzer@gmail.com",
    description="An unofficial Opensource API wrapper for Hiven\n © FrostbyteSpace",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FrostbyteSpace/openhiven.py",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires = requirements 
)
