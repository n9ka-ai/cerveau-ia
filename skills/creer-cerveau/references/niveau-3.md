Niveau 3 : un agent qui tourne seul sur un serveur ou un Raspberry Pi partage le cerveau par git. Le niveau 2 doit être fait (dépôt GitHub privé, `.gitattributes` du journal).

## Ce que l'agent distant voit, et ce qu'il ne voit pas

Il récupère tout le cerveau, mais pas les dossiers de travail de l'ordinateur : les liens `travail` sont exclus de git. C'est voulu. Il a besoin de savoir qui est l'utilisateur, ce qui se passe et ce qu'on attend de lui, pas de ses fichiers clients ni de ses vidéos. S'il travaille lui-même sur un projet (par exemple publier sur un site), il a son propre dossier de travail sur sa machine, noté dans la fiche du projet et dans son dossier `agents/<nom>/`.

## Mise en place

1. Accès au serveur : demande comment s'y connecter (souvent `ssh <nom>`). Vérifie avec `ssh -o BatchMode=yes <nom> true`. Sans accès, explique ce qu'il faut et arrête-toi.
2. Une clé rien que pour le cerveau, sur le serveur : `ssh <nom> 'ssh-keygen -t ed25519 -N "" -f ~/.ssh/cerveau'`, puis ajoute la clé publique au dépôt avec droit d'écriture : `gh repo deploy-key add <fichier.pub> --repo <dépôt> --allow-write --title <nom>`. Cette clé n'ouvre que ce dépôt, rien d'autre sur son compte.
3. Récupère le cerveau sur le serveur dans `~/cerveau`, en utilisant cette clé (`GIT_SSH_COMMAND="ssh -i ~/.ssh/cerveau"` pour le clone, puis `git config core.sshCommand` dans le dépôt).
4. Copie [../scripts/synchro.sh](../scripts/synchro.sh) sur le serveur en `~/cerveau-synchro.sh` (`chmod +x`) et lance-le une fois à la main avec `~/cerveau-synchro.sh ~/cerveau <nom>` : il doit afficher `synchro ok`.
5. Programme-le toutes les 15 minutes (`crontab -e` : `*/15 * * * * ~/cerveau-synchro.sh ~/cerveau <nom> >> ~/cerveau-synchro.log 2>&1`).

6. Les skills : installe le skill `cerveau` sur le serveur, puis `relier-skills.sh ~/cerveau ~/.agents/skills <dossier de skills de l'agent>` pour que l'agent ait les mêmes skills perso que l'ordinateur. Ajoute cette commande juste après la synchro dans la tâche programmée : un skill amélioré sur l'ordinateur arrive tout seul chez l'agent.

## Le dossier de l'agent

Crée `agents/<nom>/` dans le cerveau avec un `README.md` : qui est cet agent, sur quelle machine, ce qu'il fait seul (ses tâches programmées), ce qu'il ne fait jamais, où sont ses dossiers de travail sur sa machine. Ajoute dans les instructions de démarrage de l'agent (son propre fichier de consignes, selon l'outil qu'il utilise) :

```markdown
Au réveil : lance la synchro du cerveau, puis lis `~/cerveau/AGENTS.md`, `~/cerveau/moi.md`, `~/cerveau/agents/<nom>/` et les 30 dernières lignes de `~/cerveau/journal.md`. Pour un projet, lis sa fiche. Après avoir écrit dans le cerveau, ajoute ta ligne signée au journal et relance la synchro. Ne touche jamais au dossier d'un autre agent, ne force jamais un envoi git.
```

Ajoute la section « Agents distants » à l'`AGENTS.md` du cerveau, et dans la section `## Cerveau` des règles globales de l'ordinateur la ligne : « Le cerveau est partagé avec <nom> : récupère les nouveautés (`git pull`) avant de le lire, sauvegarde et envoie après l'avoir modifié. »

## Le rangement de nuit

C'est ce qui fait qu'un cerveau ne pourrit pas. Programme chez l'agent, chaque nuit, le geste « ranger » du skill `cerveau` (installe le skill sur le serveur, par exemple dans `~/.agents/skills/cerveau/`). Il range ce qui est sûr (journal du mois clos, index à jour, liens cassés), et note le reste dans `notes/a-ranger.md` pour l'utilisateur, sans rien supprimer.

## Règle de cohabitation

Une seule IA à la fois sur un même sujet. Le journal sert de passage de relais : avant de reprendre un projet, chaque IA lit ses dernières lignes. Si deux écritures se croisent quand même, le journal fusionne seul. Pour une fiche modifiée des deux côtés, `synchro.sh` ne choisit pas : il annule, n'envoie rien, garde les changements locaux et l'écrit dans son log. L'agent le signale à l'utilisateur, qui tranche.
