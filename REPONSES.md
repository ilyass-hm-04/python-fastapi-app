# TP 6 – Variables d'environnement, Inputs et Outputs

Branche : `feature/tp-env` — workflows : `.github/workflows/tp-env.yml` et `.github/workflows/greeting.yml`.

## Partie 1 – Variables d'environnement avec GITHUB_ENV

### Q1. Pourquoi la variable n'est-elle pas disponible dans la step qui l'a définie, mais seulement dans les suivantes ?

`GITHUB_ENV` désigne un fichier. La commande `echo "APP_NAME=my-app" >> $GITHUB_ENV` ne modifie pas l'environnement du processus en cours : elle ajoute seulement une ligne à ce fichier. Le runner lit ce fichier une fois la step terminée et injecte les variables dans l'environnement des steps suivantes du même job. Le shell de la step qui écrit a déjà été lancé avec son environnement figé ; dans cette même step, il faut utiliser une variable shell locale pour réutiliser la valeur.

### Q2. Job `verify-env` : que constatez-vous ? Quelle est la portée de GITHUB_ENV ?

Dans le run #3, la step « Print APP_NAME » du job `verify-env` affiche `APP_NAME in verify-env is ''` : la variable est vide. Chaque job s'exécute sur son propre runner, une machine virtuelle neuve, qui ne partage ni fichiers ni variables avec les autres jobs. La portée de `GITHUB_ENV` est donc limitée aux steps suivantes du **même job**.

## Partie 3 – Outputs : passer des données entre deux jobs

### Q3. Que se passe-t-il avec `>` au lieu de `>>` dans GITHUB_OUTPUT si deux outputs sont définis dans la même step ?

L'opérateur `>` écrase le contenu du fichier à chaque écriture, alors que `>>` ajoute à la suite. Avec `>`, la deuxième commande `echo` remplace la première : seul le dernier output est conservé et le premier est perdu. Les jobs qui lisent le premier output via `needs` obtiendraient alors une valeur vide. Il faut donc toujours utiliser `>>` pour `GITHUB_OUTPUT` (comportement documenté, non exécuté dans ce TP).

### Q4. Pourquoi GITHUB_ENV ne suffit-il pas ici, alors que GITHUB_OUTPUT fonctionne entre jobs ?

`GITHUB_ENV` ne vit que sur le runner du job qui l'écrit (voir Q2) : un autre job ne peut pas la voir. Les outputs, eux, sont déclarés explicitement au niveau du job (`outputs:` associé à `steps.<id>.outputs.<nom>`) et transmis par le service GitHub Actions aux jobs dépendants. Le job `deploy` les lit ensuite grâce à `needs.build.outputs.full_version`. Dans le run #2, `deploy` a bien affiché `Deploying version 1.0.0-2026-11-20` et `Target environment: staging`.

### Q5. Que se passe-t-il si on retire `needs: build` du job deploy ?

Sans `needs: build`, le job `deploy` n'attend plus `build` : les deux jobs démarrent en parallèle. Le contexte `needs` ne contient que les jobs listés dans `needs:`, donc `needs.build.outputs.full_version` est vide au lieu de contenir la version calculée (comportement documenté, non exécuté dans ce TP). `needs` sert donc à la fois à ordonner les jobs et à donner accès à leurs outputs.

## Exécutions

| Run | Commit | Contenu | Résultat |
|-----|--------|---------|----------|
| #1 | d206da0 | Parties 1 et 2 (inputs, environnement staging) | Succès |
| #2 | 2847cd8 | Partie 3 (output full_version, job deploy) | Succès |
| #3 | c7b81c9 | Partie 4 (workflow réutilisable greeting) | Succès |

La capture d'écran du run #3 (jobs `build` et `deploy`) est dans `screenshots/tp-env-run-success.png`.
