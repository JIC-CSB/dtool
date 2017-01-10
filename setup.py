from setuptools import setup


version = "0.5.0"
readme = open("README.rst").read()
url = "https://github.com/JIC-CSB/dtool"

setup(name="dtool",
      packages=["dtool"],
      version=version,
      description="Tools for managing scientific data",
      include_package_data=True,
      long_description=readme,
      url=url,
      download_url="{}/tarball/{}".format(url, version),
      install_requires=["cookiecutter",
                        "click",
                        "fluent-logger",
                        "jinja2",
                        "pyyaml",
                        "python-magic"],
      entry_points={
            'console_scripts': ['arctool=dtool.arctool.cli:cli']
      },
      license="MIT")
