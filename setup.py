import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

with open("requirements.txt") as file:
    requirements = file.read()

setuptools.setup(
    name="openhivenpy",
    version="0.2.dev3",
    author="Luna Klatzer",
    author_email="luna.klatzer@gmail.com",
    description="The OpenSource Python API Wrapper and Bot-Framework for Hiven",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/Luna-Klatzer/openhiven.py",
    project_urls={
        "Docs": "https://luna-klatzer.github.io/docs_openhiven.py/latest/",
        "Hiven API Docs": "https://luna-klatzer.github.io/docs_openhiven.py/latest/api_reference/",
        "Issue-Page": "https://github.com/Luna-Klatzer/openhiven.py/issues/",
        "Changelog": "https://luna-klatzer.github.io/docs_openhiven.py/latest/changelog.html"
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=requirements
)
