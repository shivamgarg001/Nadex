from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='nadex',
    version='1.0.0',
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
)