# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountRelanceWizard(models.TransientModel):
    """Crée des relances en lot depuis la liste des factures clients."""

    _name = "account.relance.wizard"
    _description = "Générer des relances clients"

    level_id = fields.Many2one(
        comodel_name="account.relance.level",
        string="Niveau de relance",
        required=True,
    )
    date_relance = fields.Date(
        string="Date de relance",
        required=True,
        default=fields.Date.context_today,
    )
    note = fields.Text(string="Notes")

    def action_generate(self):
        self.ensure_one()
        move_ids = self.env.context.get("active_ids", [])
        moves = self.env["account.move"].browse(move_ids)
        eligible = moves.filtered(
            lambda m: m.move_type == "out_invoice"
            and m.state == "posted"
            and m.payment_state in ("not_paid", "partial")
        )
        if not eligible:
            raise UserError(
                _("Aucune facture client impayée et validée dans la sélection.")
            )

        Relance = self.env["account.relance"]
        created = Relance.browse()
        for move in eligible:
            already = Relance.search_count(
                [
                    ("move_id", "=", move.id),
                    ("level_id", "=", self.level_id.id),
                    ("state", "!=", "cancel"),
                ]
            )
            if already:
                continue
            created |= Relance.create(
                {
                    "move_id": move.id,
                    "level_id": self.level_id.id,
                    "date_relance": self.date_relance,
                    "note": self.note,
                }
            )

        if not created:
            raise UserError(
                _("Toutes les factures sélectionnées ont déjà une relance à ce niveau.")
            )

        return {
            "type": "ir.actions.act_window",
            "name": _("Relances créées"),
            "res_model": "account.relance",
            "view_mode": "tree,form",
            "domain": [("id", "in", created.ids)],
        }
