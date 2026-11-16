# Seemnevaru MVC ja testjuhitud arendus

Väike kohalik aiandusrakendus seemnete arvestuseks. Kolm domeenireeglit:
1. Uus seemnesort peab olema unikaalse nime ja mittenegatiivse täisarvulise kogusega.
2. Broneering vähendab saadaolevat kogust ainult siis, kui seemneid piisab.
3. Tühistamine taastab seemned täpselt ühe korra ning salvestab tühistamise aja.

Projekt katab tehnilise osa ülesannetest #332 (MVC) ja #333 (TDD, ORM, mockid).
Teema ei ole keelatud raamatukogu näide. Iseseisva kaitsmise nõue jääb alles.

## Käivitamine ja testid

Vaja Python 3.10+; kasutatud Python 3.14, SQLAlchemy 2.0.54 ja Flask 3.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
make migrate
make test
make dev
```

Ava http://127.0.0.1:5054. Andmed asuvad vaikimisi failis seed-stock.db.
Andmebaasi URL-i saab muuta DATABASE_URL keskkonnamuutujaga; .env.example on näide,
mitte automaatselt laetav fail. SESSION_SECRET on valikuline kohaliku sessiooni
allkirjastamise võti; selle puudumisel luuakse iga käivituse jaoks uus võti.
Rakendus on ühe kasutaja localhost-prototüüp, mitte avalik mitme kasutaja teenus.

## MVC osad

| Osa | Failid | Vastutus |
|---|---|---|
| Model | src/models.py, src/service.py, src/database.py | ORM mudelid, domeenireeglid, transaktsioonid ja migratsioonid |
| Controller | src/controllers.py | HTTP sisend, CSRF kontroll, teenuse kutsumine, veateade või ümbersuunamine |
| View | src/views/index.html, src/static/style.css | Seemnete ja broneeringute HTML vaade ning sisestusvormid |
| Koostamine | src/app.py | Seob kontrolleri, vaate ja teenuse Flaski rakenduseks |

Vaade ei tee andmebaasipäringuid. Kontroller ei sisalda SQL-i ega koosta HTML-i
stringidega. Teenuse meetodid on kasutatavad ka ilma veebiserverita.

## ORM ja migratsioonid

001_seeds.sql loob seemned koos UNIQUE nimevõtme ja koguse CHECK-piiranguga.
002_reservations.sql lisab broneeringud, FK seose ja oleku/koguse piirangud.
003_cancellation_time.sql lisab tühistamisaja. make migrate töötab puhtal
SQLite andmebaasil ning ei korda juba rakendatud migratsioone.

Broneerimine ja tühistamine muudavad mõlemad kahte tabelit ühes transaktsioonis.
Tingimuslik UPDATE väldib negatiivset laoseisu ja korduvat tühistamist. FK kontroll
on ühenduse avamisel sisse lülitatud. UI nimekirjad loetakse eraldi täpselt
määratud SELECT-päringutega; lazy relationships'eid pole ja N+1 päringuid ei teki.
Test kontrollib ka seda, et ebaõnnestunud broneeringu INSERT pöörab laoseisu tagasi.

## TDD ajalugu

Iga funktsionaalsus tehti päris feature-harus. Kõigepealt lisati testid ja
käivitati ebaõnnestuv kontroll. Siis kirjutati minimaalne teostus ning tehti
käitumist säilitav refaktor. Harud on alles ja main'i liideti --no-ff merge'iga.

- feature/register-seeds: red 73e26ec, green 3734f29, refactor cb59cb1
- feature/reserve-seeds: red 0003c80, green c9e7251, refactor 039d3ac
- feature/cancel-reservation: red 6954fbe, green 0a6804d, refactor 9517a72

Kontrolli: git log --graph --oneline --all. Tegemist on Codexi tegeliku
arendusajalooga, mitte väitega õppija iseseisvast koodikirjutamisest.

Mockid asendavad väliseid kella- ja UUID-allikaid. Domeeniloogikat ei mockita:
ühik- ja integratsioonitestid kasutavad päris SQLite andmebaasi. Faili taasavamine,
migratsioonide idempotentsus, FK/CHECK piirangud ja rollback on samuti testitud.

## Kontrollitud 16.11.2026

make test: 20 testi PASS. Flaski testiklient kontrollib HTTP-kontrollerit, Jinja
HTML-renderdust, CSRF tõrjet, vigast sisendit ja lisamise/broneerimise/tühistamise
tervikvoogu ilma socket'ita. Kohaliku veebiserveri tegelik käivitus ja brauseripilt
jäid kontrollimata, sest selle sessiooni sandbox keelab socket'id.

.github/workflows/tests.yml käivitab samad testid pushi/PR-i korral. Kohalikult
olemas olev workflow pole tõend GitHub Actionsi edukast jooksust. Katvuse >=70%
soovitust eraldi pole mõõdetud. Kood, testid ja migratsioonid on valmis; GitHubi
avaldamine ning individuaalne kaitsmine pole sellega automaatselt tehtud.
