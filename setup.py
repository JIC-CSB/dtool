from setuptools import setup

from dtool import __version__


version = __version__
readme = open("README.rst").read()
url = "https://github.com/JIC-CSB/dtool"

setup(name="dtool",
      packages=["dtool"],
      version=version,
      description="Tools for managing scientific data",
      scripts=["bin/arctool"],
      include_package_data=True,
      long_description=readme,
      url=url,
      download_url="{}/tarball/{}".format(url, version),
      install_requires=["cookiecutter",
                        "click",
                        "fluent-logger",
                        "jinja2",
                        "pyyaml"],
      license="MIT")
