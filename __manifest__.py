{
    "name": "Relances clients",
    "version": "17.0.1.0.0",
    "summary": "Suivi et relance des factures clients échues",
    "description": """
Relances clients
================

Ajoute un suivi structuré des factures clients échues :

* niveaux de relance paramétrables (retard en jours, modèle d'email) ;
* génération manuelle depuis la liste des factures ou automatique par tâche planifiée ;
* envoi de l'email de relance et suivi de l'état de chaque relance ;
* indicateurs de retard sur la facture et encours échu par client.
* lettre de relance PDF et tableau de bord de l'encours échu.
""",
    "author": "Khadim Touré",
    "website": "https://portfolio-eta-eight-fwjsx0wxie.vercel.app/",
    "license": "LGPL-3",
    "category": "Accounting/Accounting",
    "depends": ["account", "mail"],
    "data": [
        "security/relance_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/mail_template_data.xml",
        "data/relance_level_data.xml",
        "data/ir_cron_data.xml",
        "report/relance_report.xml",
        "views/relance_dashboard_views.xml",
        "views/account_relance_level_views.xml",
        "views/account_relance_views.xml",
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "wizard/relance_wizard_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_relance_client/static/src/components/relance_dashboard/relance_dashboard.scss",
            "account_relance_client/static/src/components/relance_dashboard/relance_dashboard.js",
            "account_relance_client/static/src/components/relance_dashboard/relance_dashboard.xml",
        ],
    },
    "installable": True,
    "application": False,
}
