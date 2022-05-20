# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Debrand',
    'category': 'Cryptocurrency',
    'summary': 'Debran for Bot',
    'version': '1.0',
    'description': """
        This module provides the multiple factor bot.
        """,
    'depends': [ ],
    'data': [
    ],
    'assets': {
        'web.assets_qweb': [
        ],
        'web.assets_backend': [
            'debrand/static/src/**/*',
        ],
        'web.tests_assets': [
        ],
        'web.qunit_mobile_suite_tests': [
        ],
    },
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
}
