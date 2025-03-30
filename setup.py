from setuptools import setup, find_packages

setup(
    name="rclonetray",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "PyQt6>=6.5.0",
        "PyQt6-Qt6>=6.5.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "rclonetray=rclonetray.__main__:main",
        ],
    },
    python_requires=">=3.8",
)
