# -*- coding: utf-8 -*-
{
    'name': "Terminal",

    'summary': """
        This module is about the terminal""",

    'description': """
        This module is about the terminal
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Sales',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'booking_module', 'mict_finance', 'mict_train'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/gate_in_view.xml',
        'views/gate_in_stage_view.xml',
        'views/gate_out_stage_view.xml',
        'views/gate_out_view.xml',
        'views/container_stacking_stage_view.xml',
        'views/container_stacking_view.xml',
        'views/container_view.xml',
        'views/terminal_view.xml',
        'views/bay_plan_view.xml',
        'views/bay_plan_attribute_view.xml',
        'views/terminal_service_view.xml',
        'reports/report.xml',
        'reports/custom_header_footer.xml',
        'reports/equipment_report_template.xml',
        'reports/equipment_report_template_import.xml',
        'reports/equipment_report_template_export.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
