Comment rendre les règles globales uniques pour toutes les IA, puis y écrire les deux sections du cerveau.

## Un seul fichier, des liens

La source est `~/.agents/AGENTS.md`. Les autres IA la lisent par un lien :

| IA | Fichier qu'elle lit | Devient |
| --- | --- | --- |
| Claude Code | `~/.claude/CLAUDE.md` | lien vers `~/.agents/AGENTS.md` |
| Codex | `~/.codex/AGENTS.md` (seulement si `~/.codex` existe) | lien vers `~/.agents/AGENTS.md` |

1. Crée `~/.agents/AGENTS.md` s'il n'existe pas.
2. Pour chaque fichier du tableau qui existe et n'est pas déjà un lien vers la source : ajoute à la source chacune de ses sections qu'elle n'a pas encore (une seule fois chacune), suis aussi ses imports (`@chemin`) pour ne rien perdre, puis mets l'ancien fichier à la corbeille ou dans `~/.agents/anciens/` et remplace-le par le lien.
3. Crée le lien :
   - macOS, Linux : `ln -sfn ~/.agents/AGENTS.md ~/.claude/CLAUDE.md` (et pareil pour Codex).
   - Windows (Git Bash) : `cmd //c mklink "$(cygpath -w ~/.claude/CLAUDE.md)" "$(cygpath -w ~/.agents/AGENTS.md)"`. Ça demande le mode développeur de Windows ou une session admin. Si ça échoue : pour Claude, écris dans `~/.claude/CLAUDE.md` la seule ligne `@~/.agents/AGENTS.md` (Claude suit l'import) ; pour Codex, fais un lien dur `cmd //c mklink /H …` (pas besoin d'admin). Un lien dur peut se casser si un éditeur réécrit le fichier : le geste « ranger » du skill `cerveau` vérifie que les deux contenus sont identiques.
4. Vérifie en relisant `~/.claude/CLAUDE.md` : il doit afficher le contenu de la source.

## Section `## Ma façon de travailler`

Construis-la depuis les réponses 2, 3, 4 et 7, en moins de 15 lignes, sans chemin ni projet : seulement comment parler à cette personne et ce qu'elle laisse faire seule. Si la section existe déjà, remplace-la jusqu'au titre `## ` suivant ; sinon ajoute-la à la fin. Pas d'autre titre `## ` dedans. Prends une série de lignes par réponse et adapte les mots.

Niveau en informatique :
- Ne code pas : « Je ne suis pas technique. Ne me pose jamais de question technique : fais les choix toi-même et dis-moi en une phrase simple ce que tu as choisi. » « Pas de jargon ; si un mot technique est inévitable, explique-le en mots de tous les jours. »
- Bricole : « Je connais les bases mais je ne suis pas développeur. Fais les choix techniques et explique chacun en une ligne. Donne-moi une commande seulement si je dois vraiment la lancer, prête à copier. »
- Développeur : « Je suis développeur (<langages, outils>). Le détail technique est bienvenu, court. Demande avant un gros choix d'architecture ou une nouvelle dépendance. »

Façon de bosser :
- Autonome : « Fais les choses directement, le plus seul possible. Arrête-toi seulement pour ce qui a vraiment besoin de moi : me connecter, payer, un choix que moi seul peux faire, ou ce qui ne se rattrape pas. Une question à la fois. »
- Étape par étape : « Montre-moi le plan en quelques lignes, attends mon accord, puis fais-le. Dis-moi ce que chaque étape a changé. »

Réponses : « Réponds en <langue>, <court et direct | détaillé>. Termine par ce qui est fait, et ce que je dois faire s'il y a quelque chose. »

Jamais (seulement ce qu'il a dit) : « Ne <règle> jamais sans me le montrer avant. »

## Section `## Cerveau`

Même règle : remplace-la si elle existe, sinon ajoute-la.

```markdown
## Cerveau

Mon cerveau est `<chemin complet>` : toutes mes IA partagent cette mémoire, rangée par projet.
- Avant de travailler sur un projet, lis `AGENTS.md` et `index.md` du cerveau, puis la fiche du projet. Si tu es ouvert dans un dossier de travail, `index.md` dit à quel projet il appartient.
- Le code, les vidéos et les gros fichiers restent dans le dossier de travail ; le cerveau garde ce qu'il faut *savoir* : état, décisions et leur raison, prochaines étapes.
- Au début d'une session de travail, lance `python <skills>/cerveau/scripts/rattraper.py etat` ; s'il y a des conversations triées à ranger, propose-le en une ligne (geste « rattraper »), sans le faire d'office.
- En fin de session, sauve : mets la fiche à jour et ajoute une ligne signée dans `journal.md`.
- Mes skills à moi vivent dans `<cerveau>/skills/` et sont reliés dans `~/.agents/skills` et `~/.claude/skills`. Un skill que je crée ou modifie va là (skill `cerveau`, geste « sauver un skill »). Les skills installés depuis le dépôt de quelqu'un d'autre restent dans `~/.agents/skills` ; un skill propre à une seule IA reste dans son dossier à elle.
```
