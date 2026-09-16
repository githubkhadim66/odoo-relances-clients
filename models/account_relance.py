# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountRelance(models.Model):
    """Une relance = une facture client échue, à un niveau de relance donné."""

    _name = "account.relance"
    _description = "Relance client"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_relance desc, id desc"

    name = fields.Char(
        string="Référence",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("Nouveau"),
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Facture",
        required=True,
        ondelete="cascade",
        domain=[
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("payment_state", "in", ("not_paid", "partial")),
        ],
        tracking=True,
    )
    level_id = fields.Many2one(
        comodel_name="account.relance.level",
        string="Niveau",
        required=True,
        tracking=True,
    )
    partner_id = fields.Many2one(
        related="move_id.partner_id", string="Client", store=True, readonly=True
    )
    date_relance = fields.Date(
        string="Date de relance",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    date_due = fields.Date(
        related="move_id.invoice_date_due", string="Échéance", store=True, readonly=True
    )
    currency_id = fields.Many2one(related="move_id.currency_id", readonly=True)
    amount_residual = fields.Monetary(
        related="move_id.amount_residual",
        string="Reste dû",
        currency_field="currency_id",
        store=True,
        readonly=True,
    )
    days_overdue = fields.Integer(
        string="Retard (jours)", compute="_compute_days_overdue"
    )
    state = fields.Selection(
        selection=[
            ("draft", "Brouillon"),
            ("sent", "Envoyée"),
            ("done", "Réglée"),
            ("cancel", "Annulée"),
        ],
        string="État",
        default="draft",
        required=True,
        tracking=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsable",
        default=lambda self: self.env.user,
        tracking=True,
    )
    note = fields.Text(string="Notes")
    company_id = fields.Many2one(
        related="move_id.company_id", string="Société", store=True, readonly=True
    )

    _sql_constraints = [
        (
            "move_level_uniq",
            "UNIQUE(move_id, level_id)",
            "Cette facture a déjà une relance à ce niveau.",
        ),
    ]

    # ------------------------------------------------------------------
    # Compute
    # ------------------------------------------------------------------
    @api.depends("date_due")
    def _compute_days_overdue(self):
        """Non stocké : la valeur change tous les jours, la stocker obligerait
        à tout recalculer chaque nuit. Les filtres de retard s'appuient donc
        sur date_due, pas sur ce champ."""
        today = fields.Date.context_today(self)
        for relance in self:
            if relance.date_due and relance.date_due < today:
                relance.days_overdue = (today - relance.date_due).days
            else:
                relance.days_overdue = 0

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == _("Nouveau"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "account.relance"
                ) or _("Nouveau")
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_send(self):
        """Envoie l'email du niveau de relance et passe la relance en 'Envoyée'."""
        for relance in self:
            if relance.state != "draft":
                raise UserError(
                    _("Seule une relance en brouillon peut être envoyée.")
                )
            template = relance.level_id.mail_template_id
            if not template:
                raise UserError(
                    _("Aucun modèle d'email n'est configuré sur le niveau « %s ».")
                    % relance.level_id.name
                )
            if not relance.partner_id.email:
                raise UserError(
                    _("Le client « %s » n'a pas d'adresse email.")
                    % relance.partner_id.display_name
                )
            template.send_mail(relance.id, force_send=False)
            relance.write({"state": "sent"})
            relance.message_post(
                body=_("Relance envoyée à %s.") % relance.partner_id.email
            )
        return True

    def action_done(self):
        return self.write({"state": "done"})

    def action_cancel(self):
        return self.write({"state": "cancel"})

    def action_draft(self):
        return self.write({"state": "draft"})

    def action_open_move(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": self.move_id.id,
            "view_mode": "form",
        }

    # ------------------------------------------------------------------
    # Tâche planifiée
    # ------------------------------------------------------------------
    @api.model
    def _cron_generate_relances(self):
        """Crée les relances manquantes pour les factures échues.

        Pour chaque facture on retient le niveau le plus élevé atteint, et on
        ne recrée pas une relance déjà existante pour ce couple facture/niveau.
        """
        today = fields.Date.context_today(self)
        levels = self.env["account.relance.level"].search([], order="delay_days desc")
        if not levels:
            return self.browse()

        moves = self.env["account.move"].search(
            [
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
                ("payment_state", "in", ("not_paid", "partial")),
                ("invoice_date_due", "!=", False),
                ("invoice_date_due", "<", today),
            ]
        )

        created = self.browse()
        for move in moves:
            overdue = (today - move.invoice_date_due).days
            level = next(
                (
                    lvl
                    for lvl in levels
                    if lvl.company_id == move.company_id and overdue >= lvl.delay_days
                ),
                False,
            )
            if not level:
                continue
            already = self.search_count(
                [
                    ("move_id", "=", move.id),
                    ("level_id", "=", level.id),
                    ("state", "!=", "cancel"),
                ]
            )
            if already:
                continue
            created |= self.create(
                {
                    "move_id": move.id,
                    "level_id": level.id,
                    "date_relance": today,
                }
            )
        return created
