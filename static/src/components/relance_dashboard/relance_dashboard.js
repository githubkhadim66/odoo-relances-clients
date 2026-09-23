/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Tableau de bord des relances.
 *
 * Le composant ne calcule rien : il affiche ce que renvoie
 * account.relance.get_dashboard_data, y compris les montants déjà formatés
 * et le domaine de la liste que chaque carte ouvre.
 */
export class RelanceDashboard extends Component {
    static template = "account_relance_client.RelanceDashboard";
    static props = { "*": true };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ data: null });

        // onWillStart : les données sont là avant le premier rendu, ce qui
        // évite d'afficher des cartes vides puis de les remplir.
        onWillStart(async () => {
            this.state.data = await this.orm.call(
                "account.relance",
                "get_dashboard_data",
                []
            );
        });
    }

    openCard(card) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: card.label,
            res_model: card.res_model,
            domain: card.domain,
            views: [
                [false, "list"],
                [false, "form"],
            ],
            target: "current",
        });
    }
}

registry
    .category("actions")
    .add("account_relance_client.relance_dashboard", RelanceDashboard);
