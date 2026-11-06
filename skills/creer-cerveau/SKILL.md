---
name: creer-cerveau
description: Monte le cerveau de l'utilisateur, un dossier de notes rangé par projet que toutes ses IA partagent, au niveau 1 (local), 2 (Obsidian + sauvegarde GitHub) ou 3 (synchronisé avec un agent distant), après quelques questions. Use when the user says « crée mon cerveau », « second brain », « organise ma mémoire », « passe mon cerveau au niveau 2/3 », or starts from zero.
argument-hint: "[dossier, par défaut ~/cerveau] [niveau 1|2|3]"
---

Tu montes le cerveau de l'utilisateur : un seul dossier de notes où chaque projet a sa fiche, que Claude, Codex et tout autre agent lisent pour savoir qui il est, où en est chaque projet et ce qui a été décidé. Parle-lui dans sa langue, une question courte à la fois, sans jargon : ne dis jamais « symlink », « frontmatter », « repo » ou « commit » à un débutant (dis « lien », « sauvegarde », « dossier »). Écris les fichiers du cerveau dans la langue de l'utilisateur ; garde en anglais seulement les noms que les outils attendent (`AGENTS.md`, `SKILL.md`, `.gitignore`).

Deux notions à garder en tête et à expliquer avec ces mots-là :
- le **cerveau**, c'est ce que les IA *savent* : léger, que du texte, rangé par projet ;
- le **dossier de travail**, c'est là où elles *fabriquent* : le code d'un site, des vidéos, tout ce qui a son propre git ou pèse lourd. Il reste hors du cerveau, et la fiche du projet garde un lien `travail` vers lui.

1. **Dossier et niveau.** Prends le dossier passé en argument, sinon le dossier courant s'il est vide, sinon `~/cerveau` ; confirme-le en une ligne. Demande le niveau visé en expliquant les trois en une ligne chacun (1 : tout sur ton ordi ; 2 : en plus tu le lis dans Obsidian et il est sauvegardé sur GitHub ; 3 : en plus un agent sur un serveur le partage). Par défaut 1. Si le dossier contient déjà un `AGENTS.md` de cerveau, ne repars pas de zéro : lis-le avec `moi.md` et `index.md`, dis ce que tu as trouvé, saute les questions déjà répondues et fais seulement ce qui manque pour le niveau demandé (étape 8 ou 9).

2. **Questions.** Dis en une ligne pourquoi tu demandes (pour que tes IA te connaissent et bossent à ta façon), puis pose une question par message, avec des choix ou un exemple. Utilise ton outil de question à choix pour 2, 3 et 4 si tu en as un. Accepte les réponses courtes, ne redemande jamais ce qu'une réponse a déjà dit, passe si l'utilisateur saute.
   1. Ton prénom, ce que tu fais en une phrase, ta ville ou ton fuseau horaire ?
   2. Ton niveau en informatique : « je ne code pas et n'ouvre jamais de terminal », « je bricole (no-code, tutos, un terminal de temps en temps) » ou « je suis développeur » (alors : tes langages et outils) ?
   3. Comment ton IA doit bosser : « fais tout et ne me demande que l'indispensable » ou « étape par étape, je valide chaque étape » ?
   4. Dans quelle langue elle te répond, et comment : court et direct, ou détaillé ?
   5. Tes projets en cours, 3 à 6, pro ou perso, un nom et une ligne chacun ? Pour chacun : est-ce qu'il a déjà un dossier sur ton ordi (un site, du code, des vidéos) ? Si oui, où ?
   6. Les outils que tu utilises tous les jours (mail, agenda, notes, paiement, réseaux…) ?
   7. Ce que ton IA ne doit jamais faire sans te demander (envoyer un mail en ton nom, payer, publier…) ? « Rien de spécial » est une réponse.
   8. Si ton IA pouvait te retirer une tâche cette semaine, laquelle ?

3. **Vérification.** Résume en 5 lignes courtes (qui, niveau, façon de bosser, projets avec ceux qui ont un dossier de travail, les « jamais ») et demande si c'est juste. Corrige avant d'écrire quoi que ce soit.

4. **Règles globales, un seul fichier pour toutes les IA.** Suis [references/regles-globales.md](references/regles-globales.md) : `~/.agents/AGENTS.md` devient la source unique, `~/.claude/CLAUDE.md` et `~/.codex/AGENTS.md` deviennent des liens vers lui (leur contenu existant est d'abord fusionné dedans, rien ne se perd). Écris-y les sections `## Ma façon de travailler` et `## Cerveau`. Fais-le sans demander, puis dis en une ligne simple ce que ça change (« Toutes tes IA suivent maintenant les mêmes règles et savent où est ton cerveau »).

5. **Le squelette.** Crée seulement ceci, rien de plus :
   ```text
   <cerveau>/
   ├── AGENTS.md     le guide (modèle : references/modele-agents.md)
   ├── moi.md        qui est l'utilisateur (modèle : references/modele-moi.md)
   ├── index.md      le sommaire des projets
   ├── journal.md    ce qui s'est passé, une ligne par action, signée
   ├── .gitignore    projets/*/travail, .tmp/, .env*, .DS_Store, node_modules/
   ├── .gitattributes  « * text=auto eol=lf » et « journal.md merge=union » (voir niveau-2.md)
   └── projets/      une fiche par projet (étape 6)
   ```
   Ne crée jamais un dossier vide « pour plus tard » : `notes/`, `sources/`, `infra/`, `agents/`, `_archive/` naissent avec leur premier fichier. Jamais de `CLAUDE.md` dans le cerveau : `AGENTS.md` est lu par toutes les IA. Pas de dossier par IA (`claude/`, `codex/`) : toutes partagent la même mémoire.

6. **Les projets.** Pour chaque projet de la question 5, crée `projets/<nom-court>/fiche.md` avec [references/modele-fiche.md](references/modele-fiche.md), en n'écrivant que ce que l'utilisateur a dit (« À compléter » plutôt qu'inventer). Quand un projet a déjà un dossier sur l'ordi, applique le geste « adopter un dossier existant » du skill `cerveau` : il crée le lien `travail` et, si ce dossier a déjà sa propre mémoire, demande s'il faut la garder, la fusionner ou la remplacer. Mets la tâche de la question 8 en premier dans `## Prochaines étapes` de la fiche concernée. Remplis `index.md` (un tableau projet | fiche | dossier de travail | état) et écris la première ligne de `journal.md`.

7. **Sauvegarde locale.** `git init`, puis une première sauvegarde « cerveau : création ». Au niveau 1, arrête-toi là pour git : pas de GitHub.

8. **Niveau 2 : Obsidian et GitHub.** Suis [references/niveau-2.md](references/niveau-2.md) : ouvrir le cerveau dans Obsidian, exclure les liens `travail` de sa recherche, créer un dépôt GitHub **privé** (seulement après un oui explicite), sauvegarde automatique avec l'extension Obsidian Git.

9. **Niveau 3 : agent distant.** Suis [references/niveau-3.md](references/niveau-3.md) : le serveur récupère le cerveau par git, l'agent a son dossier `agents/<nom>/`, il tire avant de lire et pousse après avoir écrit, et il range le cerveau chaque nuit.

Termine par une liste de vérification, une coche ou une croix par ligne : questions validées ; `~/.agents/AGENTS.md` contient les deux sections et les fichiers des autres IA pointent vers lui ; squelette exact, sans dossier vide ni `CLAUDE.md` ; une fiche avec un état par projet ; chaque dossier de travail relié et exclu de git ; sauvegarde faite ; niveau 2 ou 3 fait si demandé. Puis dis en 3 lignes où est le cerveau et les phrases à utiliser : « nouveau projet : … », « charge le projet X », « sauve » en fin de session, « ingère ce document », « range le cerveau ». Propose de s'attaquer tout de suite à la tâche de la question 8.
