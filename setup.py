from setuptools import setup

setup(name='sepy',
      version='0.2',
      description=' Client-side libraries for the SEPA platform (Python3) ',
      url='https://github.com/arces-wot/SEPA-python3-APIs',
      author='Fabio Viola',
      author_email='fabio.viola@unibo.it',
      license='GPLv3',
      packages=['sepy'],
      install_requires=[
          "websocket-client"
      ],
      zip_safe=False)
