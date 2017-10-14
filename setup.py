from distutils.core import setup

setup(
    name='Travelmug',
    version='0.0.1',
    description='Python web app on the go',
    url='https://github.com/bperriot/travelmug',
    author='Bruno Perriot',
    author_email='bperriot@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'Framework :: Flask',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='web flask ui',
    packages=['travelmug', ],
    install_requires=['Flask', 'Flask-Bootstrap'],
    package_data={
        'travelmug': [
            'index.html',
            'webfunc.html',
        ],
    },
    long_description=open('README.md').read(),
)
