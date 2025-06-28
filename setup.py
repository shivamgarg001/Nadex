from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='nadex-cli',
    version='2.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'python-dotenv',
        'requests',
        'websockets',
    ],
    entry_points={
        "console_scripts":[
            "nadex_dashboard = nadex_dashboard:cli_entry"
        ]
    },
    long_description=description,
    long_description_content_type="text/markdown",
    keywords=('nadex ', 'nadex-binary-options ', 'nadex-forex ', 'nadex-real-time ', 'nadex-market-data ', 'nadex-cli ', 'nadex-dashboard ', 'nadex-websocket ', 'nadex-trading ', 'nadex-finance ', 'nadex-python ', 'nadex-pip-install ', 'nadex-automation ', 'nadex-order-book', 'binary-options ', 'forex ', 'real-time ', 'market-data ', 'cli ', 'dashboard ', 'websocket ', 'trading ', 'finance ', 'python ', 'pip-install ', 'automation ', 'order-book', 'nadex pypi ', 'pypi nadex ', 'pip nadex ', 'pip i nadex-cli ', 'pypi nadex-cli ', 'pip nadex '),
)