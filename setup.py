from setuptools import setup


version = "0.2.0"
readme = open("README.rst").read()
url = "https://github.com/JIC-CSB/dtool"

setup(name="dtool",
      packages=["dtool"],
      version=version,
      description="Tools for managing scientific data",
      scripts=["bin/arctool"],
      long_description=readme,
      url=url,
      download_url="{}/tarball/{}".format(url, version),
      install_requires=["cookiecutter"],
      license='MIT')
