Niveau 2 : lire le cerveau dans Obsidian et le sauvegarder sur GitHub. Fais ce qui manque seulement.

## Obsidian

1. Si Obsidian n'est pas installé, envoie l'utilisateur sur https://obsidian.md (c'est gratuit) et attends qu'il l'ait.
2. Dis-lui : « Ouvre Obsidian, choisis "Ouvrir un dossier comme coffre" et prends `<chemin du cerveau>`. » Il voit ses fiches comme un wiki, avec les liens entre elles.
3. Les liens `travail` mènent à des dossiers parfois énormes (code, vidéos). Pour qu'Obsidian ne les fouille pas, écris dans `.obsidian/app.json` la clé `userIgnoreFilters` avec chaque chemin `projets/<nom>/travail/` (fusionne avec le contenu existant du fichier, ne l'écrase pas). Obsidian les montre toujours dans l'arborescence, mais ne les met plus dans sa recherche ni son graphe. Si un dossier de travail contient des notes utiles (un tableau de bord, un journal), l'utilisateur peut quand même les ouvrir d'un clic.
4. Ajoute au `.gitignore` du cerveau : `.obsidian/workspace*.json`, `.trash/`.

## Le journal ne se dispute jamais

Vérifie que `.gitattributes` (créé avec le squelette) contient ces deux lignes :

```text
* text=auto eol=lf
journal.md merge=union
```

La seconde : quand deux machines ont ajouté des lignes au journal en même temps, git garde les deux au lieu de bloquer. La première est indispensable pour que ça marche entre Windows et Linux : sans elle, les fins de ligne différentes font croire à git que tout le fichier a changé, et le journal se retrouve en double.

## GitHub, toujours privé

1. Demande : « Je mets une copie privée de ton cerveau sur GitHub pour ne jamais la perdre ? » Ne fais rien sans un oui.
2. S'il n'a pas de compte GitHub, envoie-le sur https://github.com/signup et attends.
3. Avec l'outil `gh` connecté : `gh repo create <nom> --private --source . --push`. Sinon, demande-lui de créer un dépôt **privé** vide sur github.com et de te donner son adresse, puis `git remote add origin <adresse>` et `git push -u origin main`.
4. Vérifie que le dépôt est bien privé (`gh repo view --json visibility`) avant de dire que c'est fait.

## Sauvegarde automatique

Dis à l'utilisateur, étape par étape : dans Obsidian, Paramètres → Extensions de la communauté → activer → Parcourir → chercher « Git » (de Vinzent) → Installer → Activer. Puis dans les réglages de l'extension : sauvegarde et synchronisation automatiques toutes les 10 minutes, récupération au démarrage activée. Désormais, ce qu'il écrit dans Obsidian et ce que ses IA écrivent est sauvegardé seul.

Termine en vérifiant : `git status` propre, `git log origin/main -1` montre la dernière sauvegarde, dépôt privé.
