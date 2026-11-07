Tri local : un modèle sur l'ordinateur lit gratuitement chaque conversation à sa fermeture et prépare des notes courtes. L'IA de la session suivante propose de les ranger dans le cerveau (geste « rattraper » du skill `cerveau`). C'est une option : sans elle, le geste marche quand même, l'IA lit alors les conversations elle-même (le plus économe est une session Haiku ou Luna).

## 1. La machine suit-elle ?

Regarde sans rien demander, puis dis le résultat en une ligne.

| Système | Commande | Assez puissant si |
|---|---|---|
| Windows | PowerShell : `Get-ItemProperty "HKLM:\SYSTEM\ControlSet001\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0*" -ErrorAction SilentlyContinue \| ? { $_."HardwareInformation.qwMemorySize" } \| % { "{0} : {1:N0} Go" -f $_.DriverDesc, ($_."HardwareInformation.qwMemorySize"/1GB) }` | une carte graphique NVIDIA ou AMD avec 12 Go ou plus |
| macOS | `uname -m` et `sysctl -n hw.memsize` | `arm64` (puce M) et 16 Go ou plus |
| Linux | `nvidia-smi --query-gpu=name,memory.total --format=csv` ou `rocm-smi --showmeminfo vram` | 12 Go ou plus |

(La mémoire affichée par `Win32_VideoController` est fausse au-delà de 4 Go : ne t'y fie pas.)

Si la machine ne suit pas, n'en parle plus : dis seulement que le rattrapage passera par l'IA, et passe à la suite.

## 2. Proposer, puis installer

Propose en une question : « Ton ordinateur peut trier tes conversations tout seul, gratuitement, avec un modèle installé chez toi (Gemma 4, environ 8 Go à télécharger). Je l'installe ? » Rien sans un oui.

1. Ollama : si `ollama --version` échoue, envoie l'utilisateur sur https://ollama.com/download (c'est gratuit), attends qu'il l'ait installé.
2. `ollama pull gemma4:12b` (environ 8 Go, plusieurs minutes : lance-le en arrière-plan).
3. Branche la fin de session : `python <skill cerveau>/scripts/rever.py installer` (`py -3` sous Windows). Le même crochet sert au rêve, qui reste coupé tant qu'aucune fiche n'a `reve: auto`. Pour Codex, l'utilisateur approuve le crochet une fois avec `/hooks`.
4. Vérifie : `python <skill cerveau>/scripts/rattraper.py etat` doit afficher « tri local : gemma4:12b (prêt) ».

Propose ensuite de rattraper l'historique : « Je trie aussi tes anciennes conversations ? Ça tourne en fond, gratuitement. » → `rattraper.py trier --depuis <date>` en arrière-plan.

## Bon à savoir

- Si un morceau de conversation prend plus de 3 minutes, `rattraper.py` coupe tout seul le tri local et le dit : la machine est trop lente. `rattraper.py etat --reactiver` le relance (après un changement de matériel, par exemple).
- Un autre modèle se règle avec la variable `CERVEAU_RATTRAPAGE_MODELE`. Essai du 2026-11-07 sur une vraie conversation : `gemma4:12b` a retrouvé toutes les idées et la bonne date ; `gpt-oss:20b`, aucune idée.
- Rien ne sort de la machine : le modèle tourne en local, les notes restent dans `~/.agents/reves/` jusqu'au rangement.
