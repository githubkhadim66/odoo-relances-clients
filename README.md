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
- **Lettre de relance PDF** : rapport QWeb imprimable depuis la relance, avec
  l'en-tête de la société, le détail de la facture et un paragraphe
  supplémentaire au-delà de 30 jours de retard.
- **Tableau de bord** : composant OWL affichant l'encours échu total, sa
  répartition par ancienneté (1-30, 31-60, plus de 60 jours) et le nombre de
  relances à envoyer ou en attente. Chaque carte ouvre la liste
  correspondante.

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

## Le rapport QWeb

Fichier `report/relance_report.xml`. Deux éléments :

- l'action `ir.actions.report`, qui déclare le PDF et, grâce à
  `binding_model_id`, le fait apparaître dans le menu Imprimer ;
- le template, qui appelle `web.html_container` puis `web.external_layout`
  pour hériter de l'en-tête et du pied de page de la société.

`t-field` affiche un champ avec le formatage d'Odoo (date dans la langue de
l'utilisateur, montant avec sa devise) ; `t-out` affiche une valeur brute ;
`t-if` conditionne un bloc ; `t-foreach` boucle sur les enregistrements.

## Le composant OWL

Fichiers dans `static/src/components/relance_dashboard/`, chargés via la clé
`assets` du manifeste dans le bundle `web.assets_backend`.

Le composant utilise `useService("orm")` pour appeler la méthode Python
`get_dashboard_data`, `useState` pour l'état réactif et `onWillStart` pour
charger les données avant le premier affichage. Il est enregistré dans le
registre `actions`, puis déclaré côté serveur par un `ir.actions.client` dont
le `tag` correspond. Les montants sont formatés côté serveur avec
`format_amount` pour respecter devise et langue sans dupliquer la logique.

## Compatibilité

Écrit et testé pour **Odoo 17**. Pour les autres versions :

- **Odoo 16** : remplacer les attributs `invisible="condition"` des vues par
  la syntaxe `attrs="{'invisible': [(...)]}"`, supprimée en 17.
- **Odoo 18** : remplacer les balises `<tree>` par `<list>` et le bloc
  `<div class="oe_chatter">` par la balise `<chatter/>`.

## Licence

LGPL-3
