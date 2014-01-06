#!/usr/bin/env python

from reviewboard.extensions.packaging import setup


PACKAGE = 'rbsocialauth'
VERSION = '0.1'

setup(
    name=PACKAGE,
    version=VERSION,
    description='Social authentication support for Review Board',
    url='http://www.beanbaginc.com/',
    author='Beanbag, Inc.',
    author_email='support@beanbaginc.com',
    maintainer='Beanbag, Inc.',
    maintainer_email='support@beanbaginc.com',
    packages=['rbsocialauth'],
    install_requires=[
        'ReviewBoard>=2.0beta2.dev',
        'python-social-auth',
    ],
    entry_points={
        'reviewboard.extensions': [
            'rbsocialauth = rbsocialauth.extension:SocialAuthExtension',
        ],
    },
    package_data={
    },
)
