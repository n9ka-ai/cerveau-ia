Modèle du fichier d'accueil à poser dans le dossier qui contient tous les projets de l'utilisateur (par exemple `~/Projets/AGENTS.md`, plus un `CLAUDE.md` d'une seule ligne `@AGENTS.md` pour Claude). Une IA ouverte là sert d'aiguilleur : l'utilisateur dit ce qu'il veut faire, elle trouve le projet et lance le travail au bon endroit. Remplace les `<…>` ; garde les exemples propres à l'utilisateur (ses sous-projets, ses projets sans dossier).

```markdown
# Accueil — Projets de <prénom>

Ce dossier contient tous mes projets. Une IA ouverte **ici** ne travaille pas ici : elle m'aiguille vers le bon projet (geste « aiguiller » du skill `cerveau`).

## Quand j'écris ma demande

1. Récupère les nouveautés du cerveau (`git pull` dans `<chemin du cerveau>`, s'il a un dépôt), puis lis son `index.md`.
2. Trouve le projet qui correspond à ma demande, d'après son sujet et pas seulement mes mots. <Exemples : « une vidéo sur X » → tel dossier.>
3. Si tu hésites entre deux projets, demande-moi en une question, avec les choix.
4. Ensuite :
   - une question rapide (où en est X, qu'avait-on décidé) : réponds ici, à partir du cerveau ;
   - du travail sur un projet qui a un dossier : si tu peux ouvrir une nouvelle session (application Claude), lance-la dans ce dossier avec le brief « Charge le projet <nom> (skill cerveau), puis : <ma demande> » ; sinon dis-moi quel dossier ouvrir ;
   - un projet sans dossier : travaille depuis le dossier du cerveau ;
   - plusieurs projets à la fois : reste ici et travaille à partir du cerveau.
5. Un dossier présent ici mais absent de l'index : dis-le et propose de l'adopter dans le cerveau.

## Règles
- Ne crée et ne modifie rien à la racine de ce dossier, sauf ce fichier sur ma demande.
- <Dossiers d'archives où ne jamais travailler.>
```
