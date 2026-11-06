Modèle du `AGENTS.md` du cerveau. Adapte-le, reste sous 100 lignes. Retire la partie « Agents distants » tant qu'il n'y a pas de niveau 3.

```markdown
# Cerveau de <prénom>

La mémoire commune de toutes mes IA (Claude, Codex, et tout agent sur mes serveurs). Rangée par **projet**, jamais par IA : celle qui reprend un sujet lit la même fiche que celle qui l'a commencé. Qui je suis : `moi.md`. Comment me parler : la section « Ma façon de travailler » de mes règles globales, à suivre ici aussi.

## Rangement

- `AGENTS.md` : ce guide. `moi.md` : qui je suis. `index.md` : le sommaire. `journal.md` : ce qui s'est passé.
- `projets/<nom>/fiche.md` : un dossier par projet, toujours avec sa fiche.
- `projets/<nom>/travail` : lien vers le dossier de travail du projet quand il en a un (code, vidéos, son propre git). Le lien n'existe que sur la machine où est ce dossier, et il est exclu de git.
- `notes/idees/` : idées pas encore lancées. `notes/a-faire.md` : choses à faire sans projet.
- `sources/` : documents bruts à ingérer (article, PDF, transcription). On ne les modifie jamais.
- `infra/` : machines, comptes, outils (jamais de clé ni de mot de passe).
- `skills/<nom>/` : mes skills à moi (créés ou adaptés par moi). Ils sont reliés dans le dossier de skills de chaque IA, sur chaque machine, par `relier-skills.sh` du skill `cerveau` : je corrige une fois, toutes mes IA en profitent. Les skills installés depuis le dépôt de quelqu'un d'autre restent dans `~/.agents/skills` ; ceux d'un seul projet restent dans son dossier de travail.
- `agents/<nom>/` : le dossier d'un agent qui travaille seul (sa personnalité, ses tâches programmées).
- `_archive/` : projets terminés et notes mortes, lisibles mais plus prioritaires.

Rien d'autre à la racine. Un dossier naît avec son premier fichier, jamais vide.

## Cerveau ou dossier de travail ?

- Ce qu'une autre IA ou une autre session doit savoir (état, décisions, ce qui reste) : dans la fiche.
- Comment on travaille dans le dossier (commandes, build, conventions de code) : dans l'`AGENTS.md` du dossier de travail.
- Le code, les médias, les fichiers produits : dans le dossier de travail, jamais dans le cerveau.
- Un projet sans code ni gros fichiers vit entièrement dans `projets/<nom>/`.

## Règles

- Une info, un seul endroit : on met à jour la fiche existante plutôt que créer un fichier.
- Chaque décision s'écrit dans la fiche (`## Décisions`) avec sa raison, et aussi chaque option écartée, pour qu'aucune IA ne la repropose. Lis ces lignes avant de proposer un changement.
- Pas de rapports d'étape ni de `final-v2.md` : le résultat utile va dans la fiche, le reste à la corbeille.
- Une méthode à refaire devient un skill dans `skills/`, pas une note.
- Jamais de clé, mot de passe ou jeton dans le cerveau.
- Tout fichier ajouté ou supprimé à la racine d'un projet ou dans `index.md` : mettre `index.md` à jour.
- On archive plutôt que supprimer.
- Un dossier alimenté par une machine (un export, une synchro automatique, par exemple `projets/<nom>/catalogue/`) est en lecture seule pour les IA : on le lit, on ne l'écrit jamais, le rangement et les rêves n'y touchent pas. Sa fiche dit qui l'alimente et à quel rythme.

## Journal

`journal.md` : une ligne par action utile, la plus récente en bas, signée.
`- AAAA-MM-JJ · <IA> (<machine>) · <projet> : ce qui a été fait.`
Au premier ajout d'un nouveau mois, déplace les lignes du mois clos dans `_archive/journal-AAAA-MM.md`.

## Gestes

Le skill `cerveau` les détaille : charger un projet, nouveau projet, sauver, ingérer, interroger, ranger, sortir en dossier de travail, adopter un dossier existant, archiver.

## Agents distants

<nom> tourne sur <machine> et partage ce cerveau par git. Il tire avant de lire, pousse après avoir écrit. Il lit `AGENTS.md`, `moi.md`, `agents/<nom>/` et la fin de `journal.md` ; il n'a pas accès aux dossiers de travail de mon ordinateur. Une seule IA à la fois sur un même sujet : le journal sert de passage de relais.
```
