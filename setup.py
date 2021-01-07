from setuptools import setup, find_packages


setup(
    name='geecomp',
    version='0.0.1',
    description='Create nice composites from Google Earth Engine',
    packages=find_packages(),
    setup_requires=['setuptools>=50'],
    install_requires=[
        'geemap>=0.8.7'
    ],
    entry_points={
        'console_scripts': [
            'geecomp = geecomp.run:main'
        ]
    }
)

