# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    relance_ids = fields.One2many(
        comodel_name="account.relance",
        inverse_name="partner_id",
        string="Relances",
    )
    relance_count = fields.Integer(
        string="Relances en cours", compute="_compute_relance_indicators"
    )
    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Devise société",
        compute="_compute_company_currency_id",
    )
    amount_overdue = fields.Monetary(
        string="Encours échu",
        currency_field="company_currency_id",
        compute="_compute_relance_indicators",
        help="Total des factures clients échues, converti en devise de la société.",
    )

    def _compute_company_currency_id(self):
        currency = self.env.company.currency_id
        for partner in self:
            partner.company_currency_id = currency

    @api.depends("relance_ids.state")
    def _compute_relance_indicators(self):
        today = fields.Date.context_today(self)
        Move = self.env["account.move"]
        for partner in self:
            partner.relance_count = len(
                partner.relance_ids.filtered(lambda r: r.state in ("draft", "sent"))
            )
            moves = Move.search(
                [
                    ("partner_id", "=", partner.id),
                    ("move_type", "=", "out_invoice"),
                    ("state", "=", "posted"),
                    ("payment_state", "in", ("not_paid", "partial")),
                    ("invoice_date_due", "!=", False),
                    ("invoice_date_due", "<", today),
                ]
            )
            # amount_residual_signed est exprimé en devise de la société,
            # ce qui permet d'additionner des factures de devises différentes.
            partner.amount_overdue = sum(moves.mapped("amount_residual_signed"))

    def action_view_partner_relances(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Relances"),
            "res_model": "account.relance",
            "view_mode": "tree,form",
            "domain": [("partner_id", "=", self.id)],
        }
