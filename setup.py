from setuptools import setup, find_packages

setup(
    name='ac9s',
    version='0.5.0',
    description='Apple Container TUI (AC9s) for macOS 15+ native containers',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'textual==0.52.0',
    ],
    entry_points={
        'console_scripts': [
            'ac9s = ac9s.app:main',
        ],
    },
    python_requires='>=3.10',
)