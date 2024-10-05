from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.rst") as readme_file:
    long_description = readme_file.read()

# Read the LICENSE file for license information
with open("LICENSE.txt") as license_file:
    license_text = license_file.read()

setup(
    name="pulseclient",
    version="0.1.0",  # Replace with your versioning logic or use a versioning package
    description="A Python client for communication between Pulseq interpreter and Pulseq design server.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Matteo Cencini",
    author_email="matteo.cencini@gmail.com",
    license=license_text,
    keywords=["pulseq", "mri", "sequence-design", "pulse-sequences", "mri-sequences"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=2.6",
    install_requires=[],  # Specify any runtime dependencies here
    extras_require={
        "dev": ["black", "isort"],
    },
    entry_points={
        "console_scripts": [
            "start_client = pulseclient.start_client:main",  # Adjust this based on your entry point
        ]
    },
    url="https://github.com/INFN-MRI/pulseclient",
    project_urls={
        "Homepage": "https://github.com/INFN-MRI/pulseclient",
        "Bug Reports": "https://github.com/INFN-MRI/pulseclient/issues",
        "Source": "https://github.com/INFN-MRI/pulseclient",
    },
)
