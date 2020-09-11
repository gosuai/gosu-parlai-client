import setuptools

setuptools.setup(
    name='gosu-parlai-client',
    packages=['gosu_parlai_client'],
    version='0.1.0',
    license='MIT',
    description='Library to work with parlai server',
    author='Gosu developers',
    author_email='support@gosu.ai',
    url='https://github.com/gosuai/gosu-parlai-client',
    keywords=['grpc', 'gosu'],
    install_requires=[
        'aiohttp>=3.6.2,<4.0',
    ],
    classifiers=[
        'Development Status :: Production',
        'Intended Audience :: Gosu Fellows',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    include_package_data=True,
)
