from setuptools import setup, find_packages

setup(
    name="verigov",
    version="1.0.0",
    description="Government Information Verification System",
    author="VeriGov Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "groq>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "pylint>=2.17.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "verigov=verigov.main:main",
        ],
    },
)
