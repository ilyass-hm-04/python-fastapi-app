# TP 8 – Stratégies GitHub Actions : Réponses

Workflow : `.github/workflows/tp-strategies.yml` – branche `feature/tp-strategies`.

> Remarque : en plus de `workflow_dispatch`, le workflow se déclenche sur `push` vers
> `feature/tp-strategies`. Le bouton « Run workflow » n'apparaît que pour les workflows
> présents sur la branche par défaut (`main`) ; ce déclencheur permet donc d'exécuter
> le workflow depuis la branche du TP. L'étape d'installation installe aussi
> `requirements.txt`, sinon les tests ne trouvent pas FastAPI.

## Q1 – Matrice de base

**6 jobs** (2 OS × 3 versions de Python) :

| OS             | Python |
|----------------|--------|
| ubuntu-latest  | 3.11   |
| ubuntu-latest  | 3.12   |
| ubuntu-latest  | 3.13   |
| windows-latest | 3.11   |
| windows-latest | 3.12   |
| windows-latest | 3.13   |

## Q2 – exclude et include

**6 jobs au total** : 6 (matrice de base) − 1 (`exclude` windows-latest / 3.11)
+ 1 (`include` ubuntu-latest / 3.14, `experimental: true`) = 6.

- ubuntu-latest : 3.11, 3.12, 3.13, 3.14 (expérimental)
- windows-latest : 3.12, 3.13

Grâce à `continue-on-error: ${{ matrix.experimental == true }}`, un échec du job 3.14
ne fait pas échouer le workflow.

## Q3 – Exclure la combinaison 3.14 ?

Cela n'aurait **aucun effet** : le job ubuntu-latest / 3.14 serait toujours créé.
`exclude` est appliqué **avant** `include` et ne porte que sur les combinaisons de la
matrice de base (produit cartésien de `os` × `python-version`). La version 3.14 n'en
fait pas partie : l'`exclude` ne trouve rien à retirer, puis l'`include` ajoute la
combinaison ensuite. Pour supprimer ce job, il faut retirer l'entrée de `include`.

## Q4 – fail-fast

Test volontairement cassé (`tests/test_break.py`) : il échoue uniquement sur Windows.

- **`fail-fast: true`** (par défaut) : dès que le premier job Windows échoue, GitHub
  **annule** tous les jobs de la matrice encore en cours ou en attente. On obtient
  un mélange de jobs réussis (les jobs Ubuntu déjà terminés), d'un ou deux jobs échoués
  (Windows) et de jobs annulés. Le résultat est incomplet.
- **`fail-fast: false`** : tous les jobs vont jusqu'au bout. Résultat complet : les
  4 jobs Ubuntu réussissent, les 2 jobs Windows (3.12, 3.13) échouent, aucun job
  annulé. On voit précisément que le problème est lié à Windows.

**Choix :**
- `true` : quand un seul échec suffit à rejeter le changement (CI sur une pull request,
  retour rapide), pour économiser les minutes de runner.
- `false` : pour un diagnostic ou des tests de compatibilité, quand on veut connaître
  toutes les combinaisons OS/version qui échouent (avant une release, matrice de
  support).

## Q5 – max-parallel

Avec `max-parallel: 2`, seuls 2 jobs tournent en même temps ; les autres restent en
attente (*queued*) et démarrent quand une place se libère.

Deux raisons de l'utiliser en entreprise :
1. **Maîtriser les ressources et les coûts** : nombre limité de runners self-hosted,
   quota de minutes CI, éviter qu'un seul workflow monopolise tous les runners de
   l'organisation au détriment des autres équipes.
2. **Protéger des ressources partagées** : base de données de test, API externe avec
   limite de débit (rate limit), environnement de staging ou licences logicielles qui
   ne supportent qu'un nombre restreint d'accès simultanés.
