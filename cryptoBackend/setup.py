from setuptools import setup

setup(
    name='cryptoBackend',
    packages=['cryptoBackend'],
    include_package_data=True,
    install_requires=[
        'flask',
        'numpy',
        'requests',
        'xmltodict',
        'web3',
        'simplejson'
    ],
)