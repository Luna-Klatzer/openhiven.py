import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

with open("requirements.txt") as file:
    requirements = file.read()

setuptools.setup(
    name="openhiven-py", 
    version="0.0.dev1",
    author="NicolasK",
    author_email="nicolas.klatzer@gmail.com",
    description="An unofficial Opensource API wrapper for Hiven\n © FrostbyteBot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FrostbyteBot/openhiven.py",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 1 - Planning",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires = requirements 
)