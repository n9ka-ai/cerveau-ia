Modèle de `projets/<nom>/fiche.md`, pour tous les projets.

```markdown
---
etat: actif        # actif | en pause | fini
mis-a-jour: <AAAA-MM-JJ>
travail: <chemin du dossier de travail, ou rien>
---

# <Nom du projet>

<Un paragraphe : ce que c'est et le but.>

## Repères
- Liens, identifiants, comptes utilisés (jamais de mot de passe).
- Mémoire propre au dossier de travail, s'il en a une : <fichiers à lire là-bas>.

## Où on en est
- Ce qui est fait, ce qui est en cours (court).

## Prochaines étapes
- [ ] <la prochaine action concrète>

## Décisions
- <AAAA-MM-JJ> <ce qui est décidé>, parce que <raison>.
- <AAAA-MM-JJ> Pas <option écartée>, parce que <raison>.
```

Laisse `## Décisions` de côté tant qu'il n'y a pas de première décision avec sa raison. Le champ `travail` donne le chemin même sur les machines où le lien n'existe pas : un agent distant sait ainsi que ce projet a un dossier ailleurs.
