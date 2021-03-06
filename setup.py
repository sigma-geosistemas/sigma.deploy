# coding: utf-8
import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
	README = readme

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='sigma.deploy',
    version='0.1',
    packages=['deploy'],
    include_package_data=True,
    license='MIT',  # example license
    description='Aplicação padrão da SIGMA Geosistemas para deploy de servidores django.',
    long_description=README,
    url='http://www.sigmageosistemas.com.br',
    author='George Silva',
    author_email='george@consultoriasigma.com.br',
    install_requires=["fabric", "fabtools", "jinja2"],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Fabric',
        'Intended Audience :: Developers',
        'License :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)