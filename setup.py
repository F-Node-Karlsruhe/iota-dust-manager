from setuptools import setup

setup(
    name='iota-dust-manager',
    version='0.1.5',    
    description='A thread safe, stateless python package that manages your receiving dust address',
    url='https://github.com/F-Node-Karlsruhe/iota-dust-manager',
    author='F-Node-Karlsruhe',
    author_email='contact@f-node.de',
    license='MIT License',
    packages=['iota_dust_manager'],
    install_requires=['iota-client>=0.2.0a8',                    
                      ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3.9',
    ],
)