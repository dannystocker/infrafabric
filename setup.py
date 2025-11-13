"""
InfraFabric Setup Configuration

Installs the `if` command-line tool.
"""

from setuptools import setup, find_packages

setup(
    name='infrafabric',
    version='0.1.0',
    description='Swarm of Swarms (S²) Infrastructure Orchestration',
    author='InfraFabric Team',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'pyyaml>=6.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'if=src.cli.if_main:cli',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
