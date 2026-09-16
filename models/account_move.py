# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    relance_ids = fields.One2many(
        comodel_name="account.relance",
        inverse_name="move_id",
        string="Relances",
    )
    relance_count = fields.Integer(
        string="Nombre de relances", compute="_compute_relance_count"
    )
    days_overdue = fields.Integer(
        string="Retard (jours)", compute="_compute_days_overdue"
    )

    @api.depends("relance_ids")
    def _compute_relance_count(self):
        for move in self:
            move.relance_count = len(move.relance_ids)

    @api.depends("invoice_date_due", "payment_state", "state")
    def _compute_days_overdue(self):
        today = fields.Date.context_today(self)
        for move in self:
            overdue = 0
            if (
                move.move_type == "out_invoice"
                and move.state == "posted"
                and move.payment_state in ("not_paid", "partial")
                and move.invoice_date_due
                and move.invoice_date_due < today
            ):
                overdue = (today - move.invoice_date_due).days
            move.days_overdue = overdue

    def action_view_relances(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Relances"),
            "res_model": "account.relance",
            "view_mode": "tree,form",
            "domain": [("move_id", "=", self.id)],
            "context": {"default_move_id": self.id},
        }
