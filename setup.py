from setuptools import setup, find_packages

from gli_flow.version import VERSION

setup(
    name="gli-flow",
    version=VERSION.lstrip("v"),
    description="Reproducible RTL-to-GDS silicon pipeline — Green Lantern Industries",
    long_description="Execution intelligence and orchestration infrastructure for open-source ASIC design workflows.",
    long_description_content_type="text/plain",
    author="Green Lantern Industries",
    author_email="team@gatelevel.io",
    url="https://github.com/Jegadiswar-SM/gli-flow-asic",
    license="Apache-2.0",
    license_files=("LICENSE",),
    packages=find_packages() + [
        "provenance", "failure_atlas",
        "gli_flow.provenance", "gli_flow.regression",
        "gli_flow.telemetry", "gli_flow.backends",
        "gli_flow.database", "gli_flow.runtime",
        "gli_flow.analytics", "gli_flow.cli",
        "gli_flow.pdk", "gli_flow.installer",
        "gli_flow.scheduler", "gli_flow.models",
        "gli_flow.cloud", "gli_flow.ci",
        "gli_flow.testing",
    ],
    package_data={
        "failure_atlas": ["*.json"],
        "provenance": ["*.py"],
        "gli_flow": ["py.typed"],
    },
    include_package_data=True,
    extras_require={
        "install": [
            "distro>=1.8.0",
            "volare>=0.18.0",
        ],
        "cloud": [
            "boto3>=1.28.0",
            "google-cloud-storage>=2.10.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "httpx>=0.27.0",
            "ruff>=0.1.0",
        ],
        "dashboard": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.0.0",
            "httpx>=0.27.0",
        ],
        "investigation": [
            "httpx>=0.27.0",
        ],
    },
    install_requires=[
        "rich>=13.7.0",
        "pyyaml>=6.0.0",
        "jinja2>=3.1.0",
        "tabulate>=0.9.0",
        "httpx>=0.27.0",
    ],
    entry_points={
        "console_scripts": [
            "gli-flow=gli_flow.cli.main:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
)
