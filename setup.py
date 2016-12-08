from setuptools import setup


version = "0.2.0"
readme = open("README.rst").read()
url = "https://github.com/JIC-CSB/dtool"

setup(name="dtool",
      packages=["dtool"],
      version=version,
      description="Tools for managing scientific data",
      long_description=readme,
      url=url,
      download_url="{}/tarball/{}".format(url, version),
      license='MIT')
