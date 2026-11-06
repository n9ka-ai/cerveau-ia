# Cerveau IA

Donne une mémoire à tes IA. Claude, Codex ou un agent qui tourne sur ton serveur : elles lisent **le même cerveau**, savent qui tu es, où en est chaque projet et ce qui a été décidé. Tu changes d'IA, la mémoire reste.

Deux skills, en français, pour Claude Code et Codex :

| Skill | Ce qu'il fait | Comment le lancer |
| --- | --- | --- |
| [`creer-cerveau`](skills/creer-cerveau/SKILL.md) | Te pose quelques questions, puis monte ton cerveau au niveau que tu choisis (1, 2 ou 3). Relance-le plus tard pour monter d'un niveau. | « Crée mon cerveau », « passe mon cerveau au niveau 2 » |
| [`cerveau`](skills/cerveau/SKILL.md) | Les gestes du quotidien : charger un projet, sauver, ingérer un document, ranger, sortir un projet dans son dossier de travail, adopter un dossier existant. | « Charge le projet X », « sauve », « ingère ce PDF », « range le cerveau » |

## L'idée en une phrase

**Le cerveau**, c'est ce que tes IA *savent* : un dossier de notes, léger, rangé par projet. **Le dossier de travail**, c'est là où elles *fabriquent* : le code d'un site, des vidéos, un gros projet. Le cerveau garde une fiche par projet et un lien vers son dossier de travail.

```text
cerveau/
├── AGENTS.md        le guide que toutes les IA lisent
├── moi.md           qui tu es
├── index.md         le sommaire : tous les projets, où ils sont
├── journal.md       ce qui s'est passé, qui l'a fait
├── projets/
│   ├── mon-site/
│   │   ├── fiche.md     état, décisions, prochaines étapes
│   │   └── travail  →   lien vers le dossier du code (reste sur ta machine)
│   └── une-idee/
│       └── fiche.md     un projet sans code vit entièrement ici
├── notes/           idées, choses à faire
└── skills/          tes skills à toi, reliés dans toutes tes IA
```

Et quand tu fermes une conversation, ton IA **rêve** : elle relit ce qui s'est dit et range dans le cerveau ce qu'il faut retenir, toute seule. Ça marche avec Claude Code et Codex.

Tes skills perso vivent aussi dans le cerveau : tu en améliores un, toutes tes IA ont la nouvelle version, même celle de ton serveur.

## Les 3 niveaux

| Niveau | Ce que tu montes | Pour qui |
| --- | --- | --- |
| **1. Local** | Le cerveau dans un dossier de ton ordi. Toutes tes IA le lisent. | Tu débutes, tu veux que ça marche ce soir. |
| **2. Obsidian + sauvegarde** | Tu ouvres le cerveau dans Obsidian pour le lire comme un wiki, il est sauvegardé sur GitHub (privé), et tes projets qui grossissent ont leur dossier de travail. | Tu as de vrais projets : un site, du code, des vidéos. |
| **3. Synchronisé** | Le cerveau est partagé par git avec un agent qui tourne seul sur un serveur ou un Raspberry Pi. Il lit, écrit, et range le cerveau chaque nuit. | Tu veux un assistant qui travaille 24 h/24. |

On commence au niveau 1, on monte quand on en a besoin : relance `creer-cerveau`, il ne refait que ce qui manque.

## Installer

Dans Claude Code (ou Codex), envoie :

```text
Installe ces skills : https://github.com/n9ka-ai/cerveau-ia
```

Ou, si tu as Node.js :

```bash
npx skills add n9ka-ai/cerveau-ia -g -s '*' -y
```

Puis crée un dossier vide, ouvre-le dans ton IA, et dis : **« Crée mon cerveau »**.

## Ce qui ne va jamais dans le cerveau

- Tes clés, mots de passe et jetons : ils restent dans les variables d'environnement de ta machine.
- Le code, les vidéos, les gros fichiers : ils restent dans leur dossier de travail.
- Les méthodes que tu refais souvent : elles deviennent des skills, pas des notes.

## D'où ça vient

- Andrej Karpathy, [« LLM Wiki »](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) : l'IA tient elle-même un wiki, avec un sommaire, un journal, et trois gestes (ingérer, interroger, ranger).
- Melvyn, [ai-sprint-skills](https://github.com/Melvynx/ai-sprint-skills) : le cerveau rangé par projet et les règles uniques pour toutes les IA.

Ce dépôt reprend ces deux idées et ajoute les dossiers de travail, l'adoption de projets qui existent déjà, et la synchronisation avec un agent distant.

## Licence

[MIT](LICENSE). Utilise, modifie, partage.

Fait par [Techonnecte](https://techonnecte.fr).
