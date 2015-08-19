from setuptools import setup

setup(name='lanbilling',
      version='0.0.1',
      description='The API wrapper for LANBilling',
      url='http://github.com/storborg/funniest',
      author='Andrey Madiev',
      author_email='madiev@lanbilling.ru',
      license='GPL2',
      packages=['lanbilling'],
      install_requires=[
          'simplejson'
      ],
      zip_safe=False
      )
