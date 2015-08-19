from setuptools import setup

setup(name='lanbilling',
      version='0.0.1',
      description='The API wrapper for LANBilling',
      url='https://git.lanbilling.ru/madiev/lanbilling',
      author='Andrey Madiev',
      author_email='madiev@lanbilling.ru',
      license='GPL2',
      packages=['lanbilling'],
      install_requires=[
          'simplejson'
      ],
      zip_safe=False
      )
