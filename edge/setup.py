from setuptools import setup, find_packages

setup(
    name="intellidr_edge",
    version="1.0.0",
    description="IntelliDR - AI-ML Based Intelligent Dead Reckoning Engine",
    author="Team Logic Legend2 (SIH26168 - ISRO)",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "intellidr-edge=intellidr_edge.cli.main:main",
        ],
    },
    python_requires=">=3.8",
)
