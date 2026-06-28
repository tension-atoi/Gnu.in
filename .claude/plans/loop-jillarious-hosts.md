# Runbook — Boucle « jillarious-hosts-rust »

> Plan de boucle autonome managée généré par `/loop-start`.
> Emplacement volontairement **hors du dépôt `gnu.in-os`** (`.claude/` y est suivi
> par git ; écrire dedans violerait « Do NOT leave untracked source files in
> gnu.in-os »). Ce runbook vit au niveau workspace.

## 1. Identité de la boucle

| Champ | Valeur |
|-------|--------|
| Motif (`pattern`) | **sequential** |
| Mode (`--mode`) | **safe** (gates stricts, checkpoint à chaque hôte) |
| Branche de travail | `feat/jillarious-hosts-rust` |
| Dépôt | `gnu.in-os/` (autorité source) |
| Mandat `/loop` | `approuvé. mise en chantier d'écriture 100% + rapport d'état + couverture prospective` |
| Langue des rapports | français (orthographe complète, accents) |
| Niveau d'agent | Level 2 — écrire sur branche de feature + lancer les commandes verify ; **jamais** toucher `main`/tags/promote sans instruction humaine explicite (Level 3) |

## 2. Stratégie de branche

- **Un commit par hôte** (granularité « chunk committable cohérent », pas de crate à
  moitié faite).
- Commits NEUFS uniquement (jamais `--amend`), jamais `--no-verify`, attribution
  désactivée globalement (pas de trailer co-author / Generated-with).
- Convention de message : `feat(<crate>): <résumé> (Phase S1|S3|S5)`.
  - S1 = hôtes wlr-layer-shell ; S3 = launcher ; S5 = specs RTTC.
- `Cargo.lock` suivi par crate (osd/dock/notification le font déjà).

## 3. Roster des surfaces + ordonnancement

Source d'autorité : `docs/jillarious-overhaul/rust-gpui-architecture.rttc.md` (P1→P5).

| Priorité | Surface | État | Note |
|----------|---------|------|------|
| P1 | gnuin-osd | ✅ fait (4bc6784) | |
| P1 | gnuin-notification | ✅ fait (479e72d) | |
| P1 | gnuin-bar | ✅ fait (a5201eb) | promotion : spike monolithique → split lib/bin canonique. **P1 clos.** |
| P2 | gnuin-screen-corners | ✅ fait (bdbb101) | 4 quarts de disque anti-aliasés ; **serde présent** (protocole show/hide/set_*/set_fullscreen), **sans** fontdue ni libc. **P2 ouvert.** |
| P2 | gnuin-background | ✅ fait (d2b7d29) | fond plein-écran (image décodée hors boucle + dim) ; couche `Background` ; **sans** tiny-skia/fontdue/libc/chrome (déps : `image`) ; 27+7 / 31+7 tests |
| P2 | **gnuin-wallpaper-selector** | ⏳ **prochain** | sélecteur de fond (`WallpaperSelectorComposeHost.qml`), couche `Overlay`, liste défilante de vignettes |
| P3 | gnuin-media-controls | ⬜ | |
| P3 | gnuin-cheatsheet | ⬜ | |
| P3 | gnuin-screen-translator | ⬜ | |
| P3 | gnuin-region-tools | ⬜ | IPC-only, pas de surface |
| P3 | gnuin-session-screen | ⬜ | |
| P3 | gnuin-lock | ⬜ | |
| P4 | gnuin-osk | ⬜ | |
| P4 | gnuin-sidebar-left | ⬜ | |
| P4 | gnuin-sidebar-right | ⬜ | |
| P5 | gnuin-overlay | ⬜ | |
| P5 | gnuin-gnosis-app | ⬜ | |
| P5 | gnuin-semantic-overlay | ⬜ | |

Marche : **wallpaper-selector → P3 → P4 → P5**, dans l'ordre du tableau
(P1 clos ; P2 : corners + background faits, reste wallpaper-selector).

### Acquis — gnuin-screen-corners (ouverture P2, commit bdbb101)

- Overlay `wlr-layer-shell` passthrough (région d'entrée vide), **4 surfaces par
  sortie** (une par coin, `exclusive_zone=-1`), remplace `ScreenCorners.qml` +
  `RoundCorner.qml`.
- Renderer : `paint_corner()` remplit le carré (token `bg_tui`) puis efface un
  quart-de-disque anti-aliasé (rayon=taille) à l'angle **intérieur** via
  `BlendMode::Clear` → reste le coin extérieur qui arrondit l'angle carré.
- **Correctif au patron §4** : ce crate **a** la feature `serde` (protocole fil
  `ScreenCornersMessage` : show/hide/set_mode/set_size/set_color/set_fullscreen,
  fire-and-forget sans event), et **n'utilise ni fontdue ni libc**. fontdue/libc
  ne sont donc pas universels — ils sont **par-crate** (présents quand il y a du
  texte / une horloge ; absents ici).

### Acquis — gnuin-background (P2, commit d2b7d29)

- Surface plein-écran sous toutes les autres : couche `wlr-layer-shell`
  **`Background`** (et non `Overlay`), namespace `gnuin-desktop`, une surface par
  sortie, 4 ancres + `set_size(0,0)` = pleine sortie, `exclusive_zone=-1`,
  `KeyboardInteractivity::None`, région d'entrée vide (le fond ne prend jamais le
  focus). Remplace `DesktopBackground.qml` 1:1.
- Modèle display-free `u32` ARGB (`0xAARRGGBB`) de bout en bout : `FillMode`
  (crop=cover défaut / fit=contain / stretch / tile) + `BackgroundState` ; les
  primitives pures = remplissage de repli uni, dim par-pixel (préserve l'alpha
  source), géométrie de placement fit/crop, conversion RGBA→ARGB, et l'écrivain
  wl_shm Argb8888 **endian-safe** (`write_argb8888` empaquette `0xAARRGGBB` en
  `[B,G,R,A]`). Aucun compositeur ni décodeur requis pour les tests.
- **Correctif au patron §4 (suite)** : pas de tiny-skia (pas de rastérisation
  vectorielle), pas de fontdue/libc (pas de texte/horloge), pas de
  gnuin-shell-chrome (son primitif RGBA→BGRA double-swaperait notre ARGB).
  Déviation inverse : ce host **a besoin d'un décodeur d'image** → dépendance
  `image 0.25` (jpeg/png/webp), optionnelle, sous la seule feature `wayland`.
- Décodage **hors boucle d'évènements** : chaque `SetWallpaper` lance un thread
  worker (decode + resize Lanczos3 + compose ARGB + dim) → le résultat
  (`DecodedFrame`) revient par un `calloop::channel` pour un blit bon marché sur
  le thread principal. La boucle ne bloque jamais sur le disque/décodage ;
  re-validation nom+dimensions au blit pour gérer les courses resize/hotplug.
- IPC `serde` : `BackgroundMessage` (set_wallpaper / clear_wallpaper /
  set_enabled), JSON ligne-à-ligne sur `$XDG_RUNTIME_DIR/gnuin/background.sock`,
  fire-and-forget (pas d'event/réponse), avec le test de contrat fil QML.

### Cible immédiate — gnuin-wallpaper-selector (P2, clôt P2)

- Sélecteur de fond d'écran (`WallpaperSelectorComposeHost.qml`) : couche
  `wlr-layer-shell` **`Overlay`** (interactif, au-dessus du fond), liste défilante
  de vignettes de fonds disponibles ; sélection → émet un `SetWallpaper` vers le
  host `gnuin-background` ci-dessus.
- Probable besoin de texte (noms de fichiers/labels) ⇒ réintroduction probable de
  fontdue + gnuin-shell-chrome ; décodage de vignettes ⇒ `image` à nouveau.
  Réévaluer les déps par-crate à l'ouverture (le patron §4 n'est pas universel).
- Interaction pointeur (survol/clic vignette, molette pour défiler) ⇒ région
  d'entrée non vide + handlers `PointerHandler` (contraste avec corners/background
  qui sont passthrough).

## 4. Patron de crate canonique (invariant à respecter)

- `[lib]` build par défaut = modèle Rust pur + renderer (display-free, testé en
  sandbox/CI).
- `[[bin]]` `main.rs` = boucle sctk/calloop derrière la feature `wayland`
  (`required-features = ["wayland"]`).
- tiny-skia + fontdue + gnuin-shell-chrome **non-optionnels** ;
  sctk/wayland-client/calloop/calloop-wayland-source/libc optionnels sous `wayland` ;
  `wayland` active `serde` ; `serde = ["dep:serde","dep:serde_json"]`.
- Renderer : buffer `&mut [u8]` BGRA (4 o/px) → `paint_into_argb` swap R/B.
- IPC : sockets Unix, JSON ligne-à-ligne sous `$XDG_RUNTIME_DIR/gnuin/<svc>.sock`,
  enums `#[serde(tag="type", rename_all="snake_case")]`.

## 5. Checklist de gate (mode safe — par itération)

À exécuter depuis la racine `gnu.in-os/`. **Toute** étape rouge ⇒ halt checkpoint
(pas de commit, rapport l'expliquant).

```sh
# compilation (ajouter --features wayland pour valider le binaire)
cargo check  --manifest-path engine/<crate>/Cargo.toml
cargo check  --manifest-path engine/<crate>/Cargo.toml --features wayland

# lints stricts sur chaque profil pertinent
cargo clippy --manifest-path engine/<crate>/Cargo.toml -- -D warnings
cargo clippy --manifest-path engine/<crate>/Cargo.toml --features serde   -- -D warnings
cargo clippy --manifest-path engine/<crate>/Cargo.toml --features wayland -- -D warnings

# format (crate neuf uniquement ; jamais reformater une crate préexistante)
cargo fmt    --manifest-path engine/<crate>/Cargo.toml

# tests (défaut + serde), inclut les tests d'intégration tests/*.rs
cargo test   --manifest-path engine/<crate>/Cargo.toml
cargo test   --manifest-path engine/<crate>/Cargo.toml --features serde
```

Puis :
- Ajouter l'entrée de gate dans `tools/verify.sh` (bloc `if [[ -f engine/<crate>/Cargo.toml ]]`).
- `bash tools/verify.sh` doit rester **PASS** de bout en bout.
- Commit NEUF (attribution désactivée).
- Rédiger le **rapport d'état** + **couverture prospective** en français.

## 6. Stratégie de palier de modèle

- **Opus** : travail architecturalement nouveau (promotion bar : split lib/bin,
  réconciliation chrome).
- **Sonnet** acceptable : greenfield P2 suivant le patron (screen-corners,
  background…), où le gabarit est déjà fixé.

## 7. Condition d'arrêt explicite

La boucle s'arrête quand **l'une** de ces conditions est vraie :
1. **Roster complet** — toutes les surfaces P1→P5 portées, committées et gated dans
   `verify.sh` (fin nominale).
2. **Gate rouge** — une étape de la checklist §5 échoue ⇒ halt checkpoint, rapport
   décrivant la panne, **pas** de `ScheduleWakeup` tant que non résolu.
3. **Stop utilisateur** — demande explicite d'arrêt.

## 8. Commandes de démarrage / supervision

```sh
# état de l'arbre (depuis gnu.in-os/)
tools/status.sh --strict

# verify source-only (la barre de qualité de la boucle)
bash tools/verify.sh

# progression des commits de la boucle
git log --oneline feat/jillarious-hosts-rust

# diff cumulé depuis le point de divergence avec main
git diff main...feat/jillarious-hosts-rust --stat
```

La boucle elle-même se relance via `ScheduleWakeup` (re-entrée `/loop …`) :
chaque réveil = une itération = un hôte = un commit, suivi du rapport français.

## 9. Cadre de sécurité (non négociable — CLAUDE.md)

- Ne PAS éditer `~/.local/share/gnuin-shell/` directement.
- Ne PAS lancer `tools/promote-latest.sh` sans approbation humaine explicite.
- Ne PAS laisser de fichiers source non suivis dans `gnu.in-os`.
- Ne PAS toucher `main`/tags (Level 3) sans instruction humaine.
