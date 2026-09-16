# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountRelanceLevel(models.Model):
    """Niveau de relance : au bout de combien de jours de retard on relance,
    et avec quel modèle d'email."""

    _name = "account.relance.level"
    _description = "Niveau de relance client"
    _order = "delay_days, sequence, id"

    name = fields.Char(string="Niveau", required=True, translate=True)
    sequence = fields.Integer(string="Séquence", default=10)
    delay_days = fields.Integer(
        string="Retard (jours)",
        required=True,
        default=7,
        help="Nombre de jours de retard à partir duquel ce niveau s'applique.",
    )
    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Modèle d'email",
        domain="[('model', '=', 'account.relance')]",
    )
    description = fields.Text(string="Consigne interne")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Société",
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(string="Actif", default=True)

    _sql_constraints = [
        (
            "delay_days_positive",
            "CHECK(delay_days >= 0)",
            "Le nombre de jours de retard doit être positif ou nul.",
        ),
    ]
