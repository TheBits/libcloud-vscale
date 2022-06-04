import textwrap

import setuptools

url = "https://github.com/thebits/libcloud-vscale"

long_description = """
[Libcloud](https://libcloud.apache.org/) driver for interacting with [vds.selectel.ru](https://vds.selectel.ru/).

Full list of all methods see at [README at github]({}).
""".format(
    url,
)

setuptools.setup(
    name="vscaledriver",
    version="0.9.0",
    author="Sergey Mezentsev",
    author_email="thebits@yandex.ru",
    description="Libcloud driver for vds.selectel.ru (vscale.io)",
    license="UNLICENSE",
    long_description=textwrap.dedent(long_description),
    long_description_content_type="text/markdown",
    url=url,
    install_requires=["apache-libcloud>=3.0.0"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
