from setuptools import find_packages, setup
from typing import List


def get_requirements() -> List[str]:
    with open("requirements.txt") as f:
        return f.readlines()


setup(
    name="WindowsDowndate",
    version="1.0",
    description="Windows Downdate: Craft any downgrading Windows Updates",
    author="Alon Leviev",
    python_requires=">=3.9.0",
    url="https://github.com/SafeBreach-Labs/WindowsDowndate",
    packages=find_packages(),
    install_requires=get_requirements())
