# Git & GitHub – muistilista

*Jarin GitHub-opiskelu, osa 1 (syyskuu 2026). Ympäristö: Mac + VS Code.*

---

## 1. Peruskäsitteet

| Käsite | Selitys |
|---|---|
| **Git** | Versionhallintaohjelma **omalla koneella**. Pitää kirjaa kansion muutoksista. Toimii ilman internetiä. |
| **GitHub** | **Verkkopalvelu**, jonne Git-repot lähetetään säilöön ja jaettavaksi. Lisäksi yhteistyötyökalut (PR, Pages, Copilot…). |
| **Repo (repository)** | Projektikansio, jolla on versiohistoria. Historia asuu piilotetussa `.git`-kansiossa. |
| **Commit** | Tallennuspiste historiaan: muutokset + viesti + tekijä + aika. |
| **Branch** | Rinnakkainen työhaara. `main` = virallinen versio. |
| **Pull request (PR)** | Ehdotus yhdistää branch `main`iin – paikka katselmoinnille ja palautteelle. |
| **Remote / origin** | Linkki paikallisesta reposta GitHubiin. `origin` = oletusnimi. |

> Git toimii ilman GitHubia – GitHub ei ilman Gitiä.

---

## 2. Mitä tapahtuu ja missä

```
MACILLA (Git)                                   VERKOSSA (GitHub)

kansio
  │  git init
  ▼
Git-repo
  │  muokkaa + tallenna (Cmd + S)
  │  git add        (stage)
  │  git commit     (tallennuspiste)
  │  git push      ──────────────────────────▶  repo GitHubissa
  │  git pull      ◀──────────────────────────       │
                                                     │  GitHub Pages
                                                     ▼
                                                 verkkosivu
```

**Termit:** *tallenna* = levylle · *commit* = historiaan (vain Mac) · *push* = GitHubiin · *julkaisu* = yleensä Pages-sivu.

---

## 3. Terminaalikomennot

Avaa terminaali VS Codessa: **View → Terminal** (aukeaa valmiiksi projektikansioon).

### Tilanteen tarkistus
```bash
git status          # TÄRKEIN: missä tilassa olen, mitä on muuttunut
git log --oneline   # commit-historia lyhyesti (poistu: q)
git remote -v       # onko repo yhdistetty GitHubiin
git --version       # onko Git asennettu
```

### Päivittäinen työnkulku
```bash
git pull                        # 1. hae uusimmat muutokset GitHubista
                                # 2. muokkaa ja tallenna tiedostot
git add index.html              # 3. stage yksi tiedosto
git add .                       #    …tai kaikki muutokset
git commit -m "Lisää footer"    # 4. commit
git push                        # 5. lähetä GitHubiin
```

### Uuden projektin aloitus (käsin)
```bash
git init                                  # kansiosta Git-repo
git add .
git commit -m "Luo perusta"
# luo tyhjä repo GitHubissa, sitten:
git remote add origin https://github.com/Jaripee-source/REPON-NIMI.git
git push -u origin main
```

### Kertaluontoiset asetukset (tehty ✅)
```bash
git config --global user.name "Jari"
git config --global user.email "numero+Jaripee-source@users.noreply.github.com"
```

### fetch vs. pull
| | |
|---|---|
| `git fetch` | Tarkistaa mitä GitHubissa on uutta – **ei muuta tiedostoja** |
| `git pull` | fetch + **tuo muutokset** tiedostoihin |

---

## 4. Sama VS Codessa (graafisesti)

**Source Control -paneeli:** `⌃ + ⇧ + G`

| Toiminto | Miten |
|---|---|
| Kloonaa repo koneelle | `Cmd + Shift + P` → *Git: Clone* → *Clone from GitHub* |
| Uusi projekti GitHubiin | Source Control → **Publish to GitHub** → valitse *private*/*public* |
| Pull | Source Control → **⋯** → Pull |
| Stage | **+** tiedoston kohdalla |
| Commit | Viesti kenttään → **Commit** (`Cmd + Enter`) |
| Push | **⋯** → Push, tai **Sync Changes** (= pull + push) |

**Commit-painikkeen valikko:**

- **Commit** – vain Macille
- **Commit (Amend)** – muokkaa edellistä committia. ⚠️ Ei jo pushattuihin!
- **Commit & Push** – commit + push
- **Commit & Sync** – commit + pull + push (turvallisin arkivalinta)

**Tiedostojen tilatunnukset:** **U** uusi (untracked) · **M** muokattu · **A** lisätty/stageattu · **D** poistettu

**Tilapalkki (vasen alakulma):** branchin nimi + `↓0 ↑1` = 1 commit pushaamatta. Molemmat nollia = synkassa.

**Hyödyllisiä asetuksia (`Cmd + ,`):** `Git: Autofetch` = true · `startup editor` = none

---

## 5. GitHub selaimessa

| Tehtävä | Missä |
|---|---|
| Uusi repo | **+** → New repository |
| Uusi tiedosto | Repon etusivu → **+** → Create new file |
| Commit-historia | Repon etusivu → kellokuvake / *Commits* |
| Repon asetukset | **Settings** (kapeassa ikkunassa **More ▾** -valikossa) |
| Näkyvyys | Settings → General → Danger Zone → Change visibility |
| GitHub Pages | Settings → Pages → Branch: `main`, `/ (root)` → Save |
| Pages-linkki etusivulle | About → ⚙️ → *Use your GitHub Pages website* |
| VS Code selaimessa | Paina repossa **.** (piste) → github.dev |
| Codespaces | Code ▾ → Codespaces → Create. **Muista Stop/Delete!** (github.com/codespaces) |

### Branch + pull request -työnkulku
1. **main ▾** → kirjoita nimi → *Create branch*
2. Tee muutokset branchiin ja commitoi
3. **Compare & pull request** → kuvaus → *Create pull request*
4. **Files changed** → rivikohtaiset kommentit (sininen **+**)
5. **Merge pull request** → *Confirm merge* → *Delete branch*

---

## 6. Hyvät käytännöt

- **Aloita aina `git pull`illa**, jos repoa muokataan useasta paikasta.
- **Commit-viestit:** lyhyt imperatiivi – *"Lisää footer"* / *"Add footer"*. Yksi kieli per repo; englanti julkisissa.
- **Tiedostonimet:** pienet kirjaimet, ei ääkkösiä eikä välilyöntejä. Mac ei erota `Kuva.jpg`/`kuva.jpg`, GitHub Pages erottaa.
- **`.gitignore`** repon juureen, Macilla vähintään:
  ```
  .DS_Store
  ```
- **Tyhjät kansiot** eivät siirry → lisää `.gitkeep`.
- **Yli 100 Mt tiedostoja** ei voi pushata.
- **Tee Git-toiminnot käsin**, kunnes työnkulku on selkärangassa – vasta sitten tekoälylle.

---

## 7. Näkyvyys ja yksityisyys

- **Näkyvyys on GitHubin ominaisuus, ei Gitin** – valitaan repon luonnissa, muutettavissa myöhemmin.
- **Yksityiset repot:** rajattomasti, maksutta. Harjoitustyöt → *private*.
- **Julkiseksi muutettaessa koko historia paljastuu**, myös poistettu sisältö.
- **Pages-sivu on aina julkinen**, vaikka repo olisi yksityinen.
- **Opiskelijat:** käyttäjänimi, josta oikea nimi ei tunnistu; ei henkilötietoja julkisiin repoihin tai sivuihin.

---

## 8. Oma tilanne (28.9.2026)

| Asia | Tila |
|---|---|
| GitHub-tili | `Jaripee-source` |
| Education (Faculty) | ✅ Voimassa 21.9.2028 asti, GitHub Pro aktiivinen |
| Copilot Pro (opettajaetu) | ⏳ Ei aktivoitunut – tarkista Copilot settings; tukipyyntö valmiina, jos ei viikossa |
| Copilot-yksityisyys | ✅ Public code: Blocked · AI training: Disabled |
| Repot | `Harjoittelu` (public, Pages käytössä) · `Omasivu` (private) |
| GitHub Classroom | ❌ Lopetettu 28.8.2026 → korvaajat: Classroom 50, Codio, tai organisaatio + template-repot |

### Seuraavat mahdolliset aiheet
1. Branchit ja PR:t VS Codessa
2. Omasivu verkkoon Pagesilla (useat tiedostot, kuvat)
3. Opetuskäyttö: kurssiorganisaatio + template-repo
