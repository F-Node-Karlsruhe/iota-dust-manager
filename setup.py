from setuptools import setup

setup(
    name='iota-dust-manager',
    version='0.1.0',    
    description='A python package that manages your receiving dust addresses',
    url='https://github.com/F-Node-Karlsruhe/iota-dust-manager',
    author='F-Node-Karlsruhe',
    author_email='contact@f-node.de',
    license='MIT License',
    packages=['iota-dust-manager'],
    install_requires=['iota-client>=0.2.0a8',                    
                      ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3.9',
    ],
)