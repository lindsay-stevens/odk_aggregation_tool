from setuptools import setup
from odk_aggregation_tool import __version__

setup(
    name="odk_aggregation_tool",
    version=__version__,
    description="A tool for aggregating ODK XML data.",
    url="https://github.com/lindsay-stevens/",
    author="Lindsay Stevens",
    author_email="lindsay.stevens.au@gmail.com",
    packages=['odk_aggregation_tool'],
    test_suite='tests',
    include_package_data=True,
    license="MIT",
    install_requires=[
        # see requirements.txt
    ],
    keywords="odk",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
    ],
)
