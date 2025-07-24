# Git Fork Workflow

## Remote Setup

Dieses Projekt nutzt einen Fork-Workflow mit zwei Remotes:
- `origin`: Dein persönlicher Fork auf GitHub
- `upstream`: Das Original-Repository von disler

## Initial Setup (bereits erledigt)

```bash
# Original remote zu upstream umbenennen
git remote rename origin upstream

# Deinen Fork als origin hinzufügen
git remote add origin https://github.com/USERNAME/claude-code-hooks-multi-agent-observability.git
```

## Workflow für Updates vom Original

### 1. Updates vom Original holen
```bash
# Hole die neuesten Changes vom Original
git fetch upstream

# Wechsle zu deinem main branch
git checkout main

# Merge die Updates vom Original
git merge upstream/main

# ODER für einen sauberen History (empfohlen):
git rebase upstream/main
```

### 2. Deine Änderungen pushen
```bash
# Push zu deinem Fork
git push origin main
```

### 3. Bei Konflikten
```bash
# Bei Merge-Konflikten:
# 1. Löse die Konflikte in den betroffenen Dateien
# 2. Markiere als gelöst:
git add <konflikt-dateien>
git merge --continue

# Bei Rebase-Konflikten:
# 1. Löse die Konflikte
# 2. Markiere als gelöst:
git add <konflikt-dateien>
git rebase --continue
```

## Feature-Branch Workflow

### 1. Neuen Feature-Branch erstellen
```bash
# Stelle sicher, dass main aktuell ist
git checkout main
git pull upstream main

# Erstelle neuen Branch
git checkout -b feature/iterm2-integration
```

### 2. Änderungen committen
```bash
git add .
git commit -m "feat: Add iTerm2 integration"
```

### 3. Feature-Branch pushen
```bash
git push origin feature/iterm2-integration
```

### 4. Pull Request erstellen
- Gehe zu deinem Fork auf GitHub
- Erstelle Pull Request von deinem Feature-Branch zu deinem main
- Optional: Erstelle Pull Request zum Original-Repository

## iTerm2 Integration Branch

Für die iTerm2-Integration sollten wir einen separaten Branch verwenden:

```bash
# Feature-Branch für iTerm2 erstellen
git checkout -b feature/iterm2-integration

# Arbeite an der Integration...
# Commits machen...

# Push zu deinem Fork
git push origin feature/iterm2-integration
```

## Architektur-Überlegungen für iTerm2

Da wir mit einem Fork arbeiten:

1. **Modulare Struktur**: iTerm2-Integration als optionales Modul
   - Separate Ordner für iTerm2-spezifischen Code
   - Konfigurierbare Feature-Flags

2. **Minimal invasive Änderungen**:
   - Neue Dateien statt Änderungen an Core-Files
   - Plugin-artige Architektur

3. **Dokumentation**:
   - Eigene README für iTerm2-Features
   - Setup-Anleitung für optionale Features

4. **Upstream-Kompatibilität**:
   - Änderungen so gestalten, dass Merges einfach bleiben
   - Core-Funktionalität nicht brechen