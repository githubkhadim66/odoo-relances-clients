# Relances clients (Odoo 17)

Module Odoo de suivi des factures clients échues : niveaux de relance
paramétrables, génération manuelle ou automatique des relances, envoi de
l'email correspondant et suivi de l'état de chaque relance.

## Pourquoi ce module

Odoo Community n'embarque pas de gestion des relances client : la
fonctionnalité `account_followup` est réservée à l'édition Enterprise. Ce
module couvre le besoin de base sur une installation Community.

## Fonctionnalités

- **Niveaux de relance** (`account.relance.level`) : libellé, nombre de jours
  de retard déclencheur, modèle d'email associé, consigne interne. Trois
  niveaux sont créés à l'installation (7, 30 et 60 jours).
- **Relances** (`account.relance`) : une relance par couple facture / niveau,
  avec référence séquencée, montant restant dû, retard calculé, responsable,
  notes et cycle de vie brouillon → envoyée → réglée.
- **Génération en lot** : sélection de factures clients dans la liste, puis
  action contextuelle « Générer des relances ».
- **Tâche planifiée** quotidienne (désactivée par défaut) qui crée les
  relances manquantes en retenant le niveau le plus élevé atteint par chaque
  facture.
- **Indicateurs** : jours de retard sur la facture, nombre de relances en
  cours et encours échu sur la fiche client.
- **Traçabilité** : `mail.thread` et `mail.activity.mixin` sur la relance.

## Installation

```bash
# 1. Copier le module dans un répertoire d'addons
cp -r account_relance_client /chemin/vers/odoo/addons/

# 2. Redémarrer le serveur avec mise à jour de la liste des modules
./odoo-bin -c odoo.conf -u base -d ma_base

# 3. Activer le mode développeur, puis Applications > Mettre à jour la liste
#    des applications > rechercher "Relances clients" > Installer
```

Le module dépend de `account` et `mail`. Il faut donc une base avec la
comptabilité installée.

## Choix techniques

**Le retard n'est pas stocké.** `days_overdue` est un champ calculé non
stocké : sa valeur change chaque jour, la stocker imposerait un recalcul
complet quotidien pour un gain nul. Les filtres et la tâche planifiée
travaillent donc sur `invoice_date_due`, qui est une donnée stable, et non
sur le champ calculé.

**Pas de doublon de relance.** Une contrainte SQL d'unicité sur le couple
`(move_id, level_id)` garantit qu'une facture ne peut pas recevoir deux fois
la même relance, y compris en cas de double exécution du cron.

**Somme multi-devises.** L'encours échu du client additionne
`amount_residual_signed`, exprimé en devise de la société, et non
`amount_residual` qui est en devise de la facture.

**Niveau retenu par le cron.** Les niveaux sont parcourus par retard
décroissant et le premier atteint est retenu, de sorte qu'une facture en
retard de 90 jours reçoive la mise en demeure et non le premier rappel.

## Compatibilité

Écrit et testé pour **Odoo 17**. Pour les autres versions :

- **Odoo 16** : remplacer les attributs `invisible="condition"` des vues par
  la syntaxe `attrs="{'invisible': [(...)]}"`, supprimée en 17.
- **Odoo 18** : remplacer les balises `<tree>` par `<list>` et le bloc
  `<div class="oe_chatter">` par la balise `<chatter/>`.

## Licence

LGPL-3
