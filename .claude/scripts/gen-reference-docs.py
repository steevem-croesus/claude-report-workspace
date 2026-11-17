#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerates docs/reference/agents.md and docs/reference/skills.md from the frontmatter of
.claude/agents/*.md and .claude/skills/*/SKILL.md, so the reference pages cannot drift.

Usage (from the workspace root):  python .claude/scripts/gen-reference-docs.py [--check]
--check exits 1 without writing when a page is out of date.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKFLOWS = ["feature", "bug", "refactor", "spike", "explore", "investigate", "learn"]
HEADER = "<!-- Page générée par .claude/scripts/gen-reference-docs.py — ne pas éditer à la main. -->\n\n"


def frontmatter(path):
    with io.open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    meta = {}
    if not lines or lines[0].strip() != "---":
        return meta
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip('"')
    return meta


def cell(text):
    return text.replace("|", "\\|").replace("\n", " ")


def agents_page():
    folder = os.path.join(ROOT, ".claude", "agents")
    out = [HEADER + "# Référence — Agents\n",
           "Un agent par fichier sous [`.claude/agents/`](../../.claude/agents/) ; on le dispatche par son nom "
           "(`subagent_type`). Le fichier de l'agent fait autorité : cette page n'en reprend que l'en-tête.\n",
           "| Agent | Modèle | Écrit du code |", "|---|---|---|"]
    agents = []
    for name in sorted(os.listdir(folder)):
        if name.endswith(".md"):
            meta = frontmatter(os.path.join(folder, name))
            if meta.get("name"):
                agents.append(meta)
    for a in agents:
        tools = [t.strip() for t in a.get("tools", "").split(",")]
        writes = "oui" if "Edit" in tools else "non"
        out.append("| [`%s`](#%s) | %s | %s |" % (a["name"], a["name"], a.get("model", "hérité"), writes))
    out.append("")
    for a in agents:
        tools = ", ".join("`%s`" % t.strip() for t in a.get("tools", "").split(",") if t.strip())
        out += ["## %s" % a["name"], "",
                a.get("description", ""), "",
                "- **Modèle :** %s" % a.get("model", "hérité"),
                "- **Outils :** %s" % (tools or "tous"),
                "- **Définition :** [`.claude/agents/%s.md`](../../.claude/agents/%s.md)" % (a["name"], a["name"]),
                ""]
    return "\n".join(out)


def skills_page():
    folder = os.path.join(ROOT, ".claude", "skills")
    own, linked = [], []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        skill = os.path.join(path, "SKILL.md")
        if not os.path.isfile(skill):
            continue
        meta = frontmatter(skill)
        meta.setdefault("name", name)
        (linked if os.path.islink(path) else own).append(meta)

    def table(items):
        rows = ["| Skill | Rôle |", "|---|---|"]
        for s in items:
            rows.append("| `/%s` | %s |" % (s["name"], cell(s.get("description", ""))))
        return rows

    out = [HEADER + "# Référence — Skills\n",
           "Les skills vivent sous [`.claude/skills/`](../../.claude/skills/) ; chaque `SKILL.md` fait autorité. "
           "La documentation de référence qui n'est pas une procédure (patterns d'implémentation, lecture du C++, "
           "exemples de migration) vit sous [`.claude/conventions/reference/`](../../.claude/conventions/reference/).\n",
           "## Workflows\n",
           "Sept skills pilotent les workflows décrits dans "
           "[`.claude/conventions/workflows.md`](../../.claude/conventions/workflows.md) ; `feature`, `bug` et "
           "`refactor` sont gatés (voir [gates & protocole](gates-and-protocol.md)).\n"]
    out += table([s for w in WORKFLOWS for s in own if s["name"] == w])
    out += ["", "## Outils du workspace\n"]
    out += table([s for s in own if s["name"] not in WORKFLOWS])
    out += ["", "## Skills du monolithe (liens symboliques)\n",
            "Liens vers `/c/Repos/monolith/.claude/skills/`, propres à chaque machine et ignorés par git "
            "([`.gitignore`](../../.gitignore)). Les (re)créer avec `link-monolith-skills.ps1` ; les modifier dans le "
            "monolithe, jamais ici.\n"]
    out += table(linked) if linked else ["_Aucun lien présent sur cette machine._"]
    out.append("")
    return "\n".join(out)


def main():
    check = "--check" in sys.argv
    stale = False
    for rel, build in (("docs/reference/agents.md", agents_page), ("docs/reference/skills.md", skills_page)):
        path = os.path.join(ROOT, rel)
        new = build()
        old = io.open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        if old != new:
            stale = True
            if check:
                print("out of date: %s" % rel)
            else:
                io.open(path, "w", encoding="utf-8", newline="\n").write(new)
                print("written: %s" % rel)
    if check and stale:
        sys.exit(1)
    if not stale:
        print("reference pages up to date")


if __name__ == "__main__":
    main()
