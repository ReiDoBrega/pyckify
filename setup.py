from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyckify",
    version="0.1.2",
    author="ReiDoBrega",
    author_email="pedro94782079@gmail.com",
    description="A modern interactive terminal picker for creating interactive command-line selection interfaces",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ReiDoBrega/pyckify",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0.0",
        "windows-curses>=2.2.0; platform_system=='Windows'",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "terminal", "gui", "pick", "pyckify", "selection", "ui", "rich", "curses"
    ],
    project_urls={
        "Homepage": "https://github.com/ReiDoBrega/pyckify",
        "Repository": "https://github.com/ReiDoBrega/pyckify",
    },
)