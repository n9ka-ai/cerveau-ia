#!/usr/bin/env bash
# Teste les scripts du dépôt sur un faux cerveau, dans un dossier temporaire.
# Usage : bash tests/tout.sh   (macOS, Linux, ou Git Bash sous Windows)
set -u
racine="$(cd "$(dirname "$0")/.." && pwd)"
scripts="$racine/skills/cerveau/scripts"
synchro="$racine/skills/creer-cerveau/scripts/synchro.sh"
py=""
for c in python3 python py; do   # sous Windows, « python3 » peut être un faux raccourci du Microsoft Store
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys" >/dev/null 2>&1; then py="$c"; break; fi
done
[ -n "$py" ] || { echo "Python introuvable"; exit 1; }
t="$(mktemp -d 2>/dev/null || mktemp -d -t cerveau)"
ok=0; ko=0
verifie() { if eval "$2"; then echo "ok    $1"; ok=$((ok+1)); else echo "ÉCHEC $1"; ko=$((ko+1)); fi; }
g() { git -c user.name=test -c user.email=test@test -c init.defaultBranch=main "$@"; }

# Un faux cerveau sous git
mkdir -p "$t/cerveau/projets" "$t/Projets/mon-site/src" && echo x > "$t/Projets/mon-site/src/a.txt"
cd "$t/cerveau" && g init -q && printf '* text=auto eol=lf\njournal.md merge=union\n' > .gitattributes \
  && printf '# Cerveau\n' > AGENTS.md && printf '# Journal\n\n- début\n' > journal.md && g add -A && g commit -qm init

# lier.sh
mkdir -p "$t/cerveau/projets/mon-site" "$t/Projets/mon site (v2)"
printf -- '---
etat: actif
travail:
---

# Mon site

Le site vitrine.
' > "$t/cerveau/projets/mon-site/fiche.md"
fiche="$t/cerveau/projets/mon-site/fiche.md"
bash "$scripts/lier.sh" "$t/Projets/mon-site" "$t/cerveau/projets/mon-site" >/dev/null
verifie "lier : chemin écrit dans la fiche" 'grep -q "^travail: .*/Projets/mon-site$" "$fiche"'
verifie "lier : bouton sous le titre" '[ "$(sed -n 6,8p "$fiche" | tr "
" "|")" = "# Mon site||📂 [Ouvrir le dossier de travail](file:///$(grep "^travail:" "$fiche" | sed "s|^travail: /*||"))|" ]'
verifie "lier : aucun lien créé dans le cerveau" '[ ! -e "$t/cerveau/projets/mon-site/travail" ]'
avant="$(cat "$fiche")"
bash "$scripts/lier.sh" "$t/Projets/mon-site" "$t/cerveau/projets/mon-site" >/dev/null
verifie "lier : relancer ne change rien" '[ "$(cat "$fiche")" = "$avant" ]'
bash "$scripts/lier.sh" "$t/Projets/mon site (v2)" "$t/cerveau/projets/mon-site" >/dev/null
verifie "lier : nouveau dossier, un seul bouton, adresse encodée" '[ "$(grep -c "Ouvrir le dossier" "$fiche")" = 1 ] && grep -q "mon%20site%20%28v2%29)" "$fiche"'
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) MSYS_NO_PATHCONV=1 cmd /c mklink /J "$(cygpath -w "$t/cerveau/projets/mon-site/travail")" "$(cygpath -w "$t/Projets/mon-site")" >/dev/null ;;
  *) ln -s "$t/Projets/mon-site" "$t/cerveau/projets/mon-site/travail" ;;
esac
bash "$scripts/lier.sh" "$t/Projets/mon-site" "$t/cerveau/projets/mon-site" >/dev/null
verifie "lier : ancien lien retiré, dossier de travail intact" '[ ! -e "$t/cerveau/projets/mon-site/travail" ] && [ -f "$t/Projets/mon-site/src/a.txt" ]'
verifie "lier : refuse un dossier introuvable" '! bash "$scripts/lier.sh" "$t/nulle-part" "$t/cerveau/projets/mon-site" >/dev/null'

# relier-skills.sh
mkdir -p "$t/cerveau/skills/rediger" "$t/agents" && echo "---" > "$t/cerveau/skills/rediger/SKILL.md"
mkdir -p "$t/claude/rediger" && echo vrai > "$t/claude/rediger/SKILL.md"
bash "$scripts/relier-skills.sh" "$t/cerveau" "$t/agents" >/dev/null
verifie "skills : skill relié" '[ -f "$t/agents/rediger/SKILL.md" ]'
verifie "skills : refuse d'écraser un vrai dossier" '! bash "$scripts/relier-skills.sh" "$t/cerveau" "$t/claude" >/dev/null && grep -q vrai "$t/claude/rediger/SKILL.md"'

# synchro.sh : deux machines écrivent le journal en même temps
g add -A && g commit -qm skills
g init -q --bare "$t/depot.git" && g remote add origin "$t/depot.git" && g push -qu origin main
g clone -q "$t/depot.git" "$t/pi" 2>/dev/null
(cd "$t/pi" && printf -- '- pi\n' >> journal.md && bash "$synchro" . pi >/dev/null)
printf -- '- pc\n' >> journal.md
verifie "synchro : envoi après écriture simultanée" 'bash "$synchro" . pc >/dev/null'
verifie "synchro : le journal garde les deux lignes, sans doublon" '[ "$(grep -c "^- " journal.md)" = 3 ] && grep -q "^- pi" journal.md && grep -q "^- pc" journal.md'
echo pc > f.md && bash "$synchro" . pc >/dev/null
(cd "$t/pi" && g pull -q && echo pi > f.md && bash "$synchro" . pi >/dev/null)
echo autre > f.md
bash "$synchro" . pc >/dev/null 2>&1; code=$?
verifie "synchro : conflit sur une fiche = arrêt sans perte" '[ $code = 2 ] && [ "$(cat f.md)" = autre ] && [ ! -d .git/rebase-merge ]'

# rever.py
cat > "$t/conv.jsonl" <<'EOF'
{"type":"user","message":{"role":"user","content":"On choisit boulangerie-martin.fr. <system-reminder>bruit</system-reminder>"}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"thinking","thinking":"secret"},{"type":"text","text":"Noté, domaine retenu."},{"type":"tool_use","name":"Read","input":{}}]}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"contenu de fichier énorme"}]}}
{"type":"response_item","payload":{"type":"message","role":"user","content":[{"type":"input_text","text":"Et Astro, pas WordPress."}]}}
EOF
d="$("$py" -I "$scripts/rever.py" extraire "$t/conv.jsonl")"
verifie "rêve : garde le dialogue" 'echo "$d" | grep -q "boulangerie-martin.fr" && echo "$d" | grep -q "Astro"'
verifie "rêve : retire outils, fichiers, réflexion et rappels" '! echo "$d" | grep -qE "secret|énorme|bruit"'
mkdir -p "$t/home/.claude" "$t/home/.codex" && echo '{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"autre"}]}]}}' > "$t/home/.claude/settings.json"
HOME="$t/home" USERPROFILE="$t/home" "$py" -I "$scripts/rever.py" installer >/dev/null
HOME="$t/home" USERPROFILE="$t/home" "$py" -I "$scripts/rever.py" installer >/dev/null
verifie "rêve : hook branché une seule fois, sans toucher aux autres" '[ "$(grep -c rever.py "$t/home/.claude/settings.json")" = 1 ] && grep -q autre "$t/home/.claude/settings.json" && grep -q rever.py "$t/home/.codex/hooks.json"'
HOME="$t/home" USERPROFILE="$t/home" "$py" -I "$scripts/rever.py" desinstaller >/dev/null
verifie "rêve : désinstallation propre" '! grep -q rever.py "$t/home/.claude/settings.json" && grep -q autre "$t/home/.claude/settings.json"'

# rattraper.py (sans Ollama : dialogues préparés pour un petit modèle)
s="$t/home/.codex/sessions/2026/10/01"; mkdir -p "$s"
long="$(printf 'Le site de la boulangerie doit sortir avant Noël. %.0s' $(seq 1 40))"
printf '{"type":"session_meta","payload":{"cwd":"/x/boulangerie"}}\n{"type":"response_item","payload":{"type":"message","role":"user","content":[{"type":"input_text","text":"%s"}]}}\n' "$long" > "$s/rollout-a.jsonl"
printf '{"type":"response_item","payload":{"type":"message","role":"user","content":[{"type":"input_text","text":"Mode rêve. %s"}]}}\n' "$long" > "$s/rollout-reve.jsonl"
touch -t 202610011200 "$s"/*.jsonl
rat() { HOME="$t/home" USERPROFILE="$t/home" CERVEAU="$t/cerveau" OLLAMA_HOST=127.0.0.1:9 "$py" -I "$scripts/rattraper.py" "$@" 2>/dev/null; }
rat trier --depuis 2026-09-01 >/dev/null
verifie "rattraper : trouve la conversation, ignore les rêves" '[ "$(rat rapport | grep -c "\"id\"")" = 1 ] && rat rapport | grep -q "/x/boulangerie"'
verifie "rattraper : dialogue préparé sans modèle local" 'grep -q "boulangerie" "$t/home/.agents/reves/rattrapage/"*.md'
rat trier --depuis 2026-09-01 >/dev/null
verifie "rattraper : ne relit pas une conversation déjà vue" '[ "$(rat rapport | grep -c "\"id\"")" = 1 ]'
rat marquer >/dev/null
verifie "rattraper : marquer vide le rapport" '[ "$(rat rapport | tr -d "[:space:]")" = "[]" ] && ! ls "$t/home/.agents/reves/rattrapage/"*.md >/dev/null 2>&1'

# ranger.py
c="$t/cerveau"; mkdir -p "$c/projets/vieux" "$c/projets/neuf"
printf -- '---\netat: actif\nmis-a-jour: 2020-01-01\n---\n\n# Vieux projet\n' > "$c/projets/vieux/fiche.md"
printf -- '---\netat: en pause\n---\n\n# Projet neuf\n' > "$c/projets/neuf/fiche.md"
printf '# Index\n\n| Projet | Fiche | Dossier de travail | État |\n|---|---|---|---|\n| Vieux | [[projets/vieux/fiche]] | — | actif |\n| Parti | [[projets/parti/fiche]] | — | fini |\n\n## Ailleurs\n' > "$c/index.md"
printf '# Journal\n\n- 2020-01-05 · test · vieux : ancien\n- %s · test · neuf : récent\n' "$(date +%Y-%m-%d)" > "$c/journal.md"
avant="$(cat "$c/index.md")"; "$py" -I "$scripts/ranger.py" "$c" --essai >/dev/null
verifie "ranger : --essai n'écrit rien" '[ "$(cat "$c/index.md")" = "$avant" ]'
"$py" -I "$scripts/ranger.py" "$c" >/dev/null
verifie "ranger : index complété et nettoyé" 'grep -q "\[\[projets/neuf/fiche\]\] | — | en pause |" "$c/index.md" && ! grep -q "projets/parti" "$c/index.md" && grep -q "## Ailleurs" "$c/index.md"'
verifie "ranger : journal des mois clos archivé" 'grep -q "ancien" "$c/_archive/journal-2020-01.md" && ! grep -q "ancien" "$c/journal.md" && grep -q "récent" "$c/journal.md"'
verifie "ranger : fiche oubliée signalée" 'grep -q "projets/vieux/fiche" "$c/notes/a-ranger.md"'
verifie "ranger : relancer ne change rien" '[ "$("$py" -I "$scripts/ranger.py" "$c" | cut -d" " -f3-)" = "rien à ranger" ]'

echo; echo "$ok réussis, $ko échoués ($(uname -s))"
rm -rf "$t" 2>/dev/null
[ $ko = 0 ]
