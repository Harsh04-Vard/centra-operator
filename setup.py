from setuptools import setup, find_packages

setup(
    name="centra_operator",
    version="1.0.0",
    description="CentrAlign Autonomous Company Operator - Founding Engineer Core Runtime",
    author="CentrAlign Founding Team",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn>=0.30.0",
        "pydantic>=2.9.0",
        "httpx>=0.28.0",
        "requests>=2.32.0"
    ],
    entry_points={
        "console_scripts": [
            "centra-operator=cli:main",
            "centra-web=main:main"
        ]
    }
)
