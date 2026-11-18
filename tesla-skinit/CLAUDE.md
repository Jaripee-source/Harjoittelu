# Tesla custom wrap -skinit: best practices

Opit Model Y Premium (2025+) -krokotiiliskinin (`Iloinen_Krokotiili.png`) tekemisestä.
Generaattori: `make_skin.py` (ajo: `python3 -I make_skin.py <template.png> <out.png>`).

## Lähde ja vaatimukset
- Pohjat: `https://github.com/teslamotors/custom-wraps`, yksi kansio per malli/versio.
  Varmista oikea versio (esim. Model Y 2025+: base / premium / performance — pohjat eroavat).
  Kloonaa omaan tyhjään hakemistoon scratchpadiin, ja aja kuvia lukevat skriptit `python3 -I`.
- Teslan vaatimukset: PNG, 512–1024 px (käytä pohjan 1024×1024), **max 1 Mt**,
  nimi max 30 merkkiä (kirjaimet, numerot, `_`, `-`, välilyönti), max 10 kpl/lähde.
- Siirto: sovellus (Creations → Wrap → Upload) tai USB `Wraps/`-kansio (ei NTFS).
  Autossa: Toybox → Paint Shop → Wraps.

## Pohjan rakenne (UV-asettelu)
- `template.png` on RGBA: maalattavat paneelit valkoisia (alpha 255), lasi ja tausta läpinäkyviä.
  Paneelit saa erilleen: `scipy.ndimage.label((alpha>200) & (rgb>200))`.
  Ääriviivapikselit kannattaa liittää lähimpään paneeliin (distance_transform_edt),
  ettei paneelien reunoihin jää valkoista.
- Asettelu on kuin auto ylhäältä katsottuna ja kyljet käännettyinä ulos:
  ylhäällä etupuskuri → konepelti → (keskellä lasikatto, ei maalattava) → takaluukku ja takapuskuri alhaalla.
  Kyljet vasemmalla ja oikealla, **peilikuvina** (symmetria-akseli x ≈ 511.5).
- Suunnat: **y = auton pituussuunta** (pieni y = keula).
  Kyljissä **sisäreuna (lähellä keskiviivaa) = vyötärölinja/ylhäällä, ulkoreuna = helma/maa**.
  Etupuskurissa pieni y = alhaalla (maata kohti), iso y = konepellin reuna.
- Model Y Premium -paneelien id:t (label-järjestys): 1 etupuskuri, 2 konepelti, 3/4 etulokasuojat
  (kapeita kaistaleita!), 5/7 ja 15/16 kattolistat/pilarit, 6/8 etuovet, 9/10 peilit,
  11/12 takaovet, 13/14 takakulmat, 17 takaluukku, 18/19 takapuskurin kulmat, 20 takapuskuri.
- Teksti oikealla kyljellä pitää kääntää/peilata, jotta se näkyy autossa oikein päin.

## Tekniikka, joka toimi
- Proseduraalinen tekstuuri numpy + scipy (+ Pillow); `pip install scipy`, jos puuttuu.
- Suomut: Voronoi (`cKDTree.query(k=2)`), **kysely paneeli kerrallaan** vain sen paneelin pisteillä,
  ettei solu vuoda saumojen yli. Korkeus = f(d2−d1), normaalit gradientista, diffuusi + spekulaari + AO.
- Pisteet paneelityypin mukaan: pää epäsäännöllinen jittered grid (~12 px), kyljet rivit pituussuunnassa
  (isot harjanteelliset kilvet ylhäällä → pienet alhaalla), takaosa poikittaiset rivit.
- Domain warp (fbm-kohina ±10 px) pisteiden kyselyyn → orgaaniset, ei-laattamaiset solut.
- Fotorealismia lisäsi: pyöreä "tyyny"-profiili (ei viisteitä), **ohuet** urat, solun sisäinen värikohina,
  matalataajuinen läiskikkyys, maltillinen ja vaihteleva kiilto. Vältä voimakasta per-solu-värivaihtelua
  ja paksuja tummia uria (näyttää lasimaalaukselta/mosaiikilta).
- Kuviot (raidat, täplät) kannattaa ankkuroida solukeskipisteisiin, jolloin ne noudattavat suomuja.
- Hahmon piirteet (silmät, sieraimet, suu) piirretään suoraan samaan korkeus- ja värikarttaan:
  käyrät Catmull-Rom-polylinjoina + etäisyyskenttä; hampaat ellipseinä käyrän normaalin suuntaan.
  Oikea puoli = peilaus `x → 1023 − x`.
- "Ystävällinen" ilme: isot pyöreät silmät, pyöreät pupillit, kiiltopisteet, pyöreät hampaat,
  suupielet ylöspäin (kohti konepeltiä). **Ei** raskasta yläluomea: edestä katsottuna se näyttää
  unelias/uhkaavalta, koska kuva nähdään autossa pystysuunnassa käännettynä.

## Tiedostokoko
- Täysvärinen RGBA `optimize=True` mahtui hyvin (≈775 kt kohinaisellakin tekstuurilla).
- Varalla palettikvantisointi (255 väriä + läpinäkyvä indeksi) ≈ 320 kt, mutta aiheuttaa raidoitusta
  liukuväreihin (esim. silmät) → käytä vain jos raja ylittyy.

## Työnkulku ja tarkistus
1. Lue pohja, tulosta paneelien bounding boxit ja vaakasuuntaiset leveydet ennen piirtämistä.
2. Renderöi, katso koko kuva + **2× rajatut lähikuvat** (pää, kylki). Ongelmat näkyvät vasta zoomattuna.
3. Iteroi 3–4 kierrosta; tarkista lopuksi koko, mitat, tila (RGBA) ja nimi.
4. Kerro käyttäjälle rehellisesti: saumakohdat ja suunnat on pääteltävä tasopohjasta,
   lopullinen tarkistus tehdään auton 3D-näkymässä.
5. Tallenna lopputulos ja skripti repoon (konttiympäristö on väliaikainen), commit + push.
