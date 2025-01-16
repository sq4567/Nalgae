from setuptools import setup, find_packages

setup(
    name="nalgae",
    version="0.1.0",
    description="A customizable on-screen keyboard with advanced accessibility features",
    author="Nalgae Team",
    author_email="nalgae@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PySide6>=6.0.0",
        "pywin32>=300",
        "keyboard>=0.13.5",
        "mouse>=0.7.1",
        "pyautogui>=0.9.53",
        "cryptography>=3.4.7",
    ],
    entry_points={
        "console_scripts": [
            "nalgae=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Desktop Environment :: Accessibility",
    ],
    python_requires=">=3.8",
)
