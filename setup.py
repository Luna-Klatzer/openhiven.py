import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

with open("requirements.txt") as file:
    requirements = file.read()

setuptools.setup(
    name="openhivenpy",
    version="0.1.2.0",
    author="FrostbyteSpace",
    author_email="nicolas.klatzer@gmail.com",
    description="The OpenSource Python API Wrapper for Hiven!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FrostbyteSpace/openhiven.py",
    license="MIT",
    project_urls={
        "homepage": "https://github.com/FrostbyteSpace/openhiven.py",
        "documentation(old)": "https://openhivenpy.readthedocs.io/",
        "docs-rewrite": "https://openhivenpy.readthedocs.io/en/mkdocs-material-rewrite/"
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=requirements
)
