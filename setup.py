from setuptools import setup

setup(
    name='rambo-vagrant',
    version='0.2.1.dev',
    description='rambo',
    url='https://github.com/terminal-labs/rambo',
    author='Terminal Labs',
    author_email='solutions@terminallabs.com',
    license=license,
    packages=['rambo'],
    zip_safe=False,
    install_requires=[
        'bash',
        'click'
    ],
    entry_points={
          'console_scripts': [
              "rambo=rambo.__main__:main"
          ]
      },
    )

