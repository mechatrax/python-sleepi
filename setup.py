from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='sleepi',
    version='1.1.0',
    description='Python module to control the slee-Pi family',
    long_description=readme(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: System :: Hardware',
    ],
    keywords='sleepi raspberrypi',
    url='https://github.com/mechatraix/python-sleepi',
    author='Masahiro Honda',
    author_email='honda@mechatrax.com',
    license='MIT',
    packages=['sleepi'],
    install_requires=[
        'smbus',
    ],
    include_package_data=True,
    zip_safe=False,
)

