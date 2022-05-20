# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'MFBot',
    'category': 'Cryptocurrency',
    'summary': 'Multiple Factor Bot',
    'version': '1.0',
    'description': """
        This module provides the multiple fator bot.
        """,
    'depends': [ 'web', "mail" ],
    'data': [
        'security/mfbot_security.xml',
        'security/ir.model.access.csv',

        'views/kline_views.xml',
        'views/strategy_views.xml',
        'views/fill_views.xml',
        'views/pnl_views.xml',

        'views/pnl_actions.xml',
        'views/fill_actions.xml',
        'views/strategy_actions.xml',
        'views/kline_actions.xml',

        'views/menu.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'mfbot/static/src/xml/**/*',
        ],
        'web.assets_backend': [
            'mfbot/static/src/**/*',
        ],
        'web.tests_assets': [
            'mfbot/static/tests/helpers/**/*',
        ],
        'web.qunit_mobile_suite_tests': [
            'mfbot/static/tests/*_tests.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
}
