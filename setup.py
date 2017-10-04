from setuptools import setup
import json

with open(os.path.join(PROJECT_LOCATION, 'rambo/settings.json'), 'r') as f:
    SETTINGS = json.load(f)
PROJECT_NAME = SETTINGS['PROJECT_NAME']

setup(
    name='rambo-vagrant',
    version='0.2.1.dev',
    description=PROJECT_NAME,
    url='https://github.com/terminal-labs/' + PROJECT_NAME,
    author='Terminal Labs',
    author_email='solutions@terminallabs.com',
    license=license,
    packages=[PROJECT_NAME],
    zip_safe=False,
    install_requires=[
        'bash',
        'click'
    ],
    entry_points={
          'console_scripts': [
              "%s=%s.__main__:main" % [PROJECT_NAME, PROJECT_NAME]
          ]
      },
    )

