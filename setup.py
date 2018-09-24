import setuptools


setuptools.setup(
    name = 'ByHelpers',
    packages = find_namespace_packages(), # this must be the same as the name above
    version = '0.0.0',
    description = 'Library used by ByPrice scrapers',
    author = 'Kevin B. Garcia Alonso',
    author_email = 'kevangy@hotmail.com',
    url = 'https://github.com/ByPrice/ByHelpers', # use the URL to the github repo
    download_url = 'https://github.com/ByPrice/ByHelpers/tarball/0.0.0',
    keywords = ['ByPrice'],
    install_requires=[
        'pika==0.10.0'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ),
)
