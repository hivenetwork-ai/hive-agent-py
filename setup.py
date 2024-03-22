from setuptools import setup, find_packages

setup(
    name='hive-agent',
    version='0.0.1',
    author='Tomisin Jenrola',
    description='Hive Network\'s Agent Node & SDK',
    packages=find_packages(include=['hive_agent', 'hive_agent.*']),
    install_requires=[
        'fastapi==0.109.1',
        'uvicorn==0.23.2',
        'python-dotenv==1.0.1',
        'llama-index==0.10.19',
        'web3==6.15.1',
        'py-solc-x==2.0.2',
        'eth-account==0.11.0',
    ],
    python_requires='>=3.11',
)
