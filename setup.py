import setuptools
from setuptools import find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

__version__ = "0.0.0"

REPO_NAME = "risk-copilot"
SRC_REPO = "riskCopilot"
AUTHOR_EMAIL = "syedjunaid.iqbal@randstaddigital.com"

setuptools.setup(
    name=SRC_REPO,
    version=__version__,
    author_email=AUTHOR_EMAIL,
    description="risk copilot using documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juanidiqbalsyed/risk-copilot",
    project_urls={
        "Bug Tracker": "https://github.com/juanidiqbalsyed/risk-copilot/issues",
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        line
        for line in open("requirements.txt").read().splitlines()
        if line.strip() != "-e ."
    ],
)


"""
Automating the Setup
# Clone the project
git clone https://github.com/username/my_project.git
cd my_project

# Set up a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate

# Install the package and dependencies
python setup.py install

"""
