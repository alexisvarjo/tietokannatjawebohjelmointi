# Esimerkkisovellus

Harjoitustyöni on käytettyjen autojen myyntiin, vaihtoon ja ostoon  tarkoitettu nettisivu,
jossa on tällä hetkellä seuraavat toiminnot:

- Käyttäjät voivat luoda tunnukset ja kirjautua niillä
- Käyttäjä voi lisätä, muokata ja poistaa ilmoituksia
- käyttäjä voi lähettää viestejä toisten ilmoitukseen
- käyttäjä näkee sovelluksen kaikki ilmoitukset
- sovelluksessa on hakutoiminto
- sovelluksessa on käyttäjäsivut (jotka näyttävät tällä hetkellä postaukset per käyttäjä)
- ilmotukselle voi valita useamman luokittelun
- Käyttäjä pystyy lisäämään kuvia, ja kuvia voi selailla ilmoituksessa
- Jokaisesta käyttäjästä käyttäjäkohtainen infosivu


Sovellus on testattu ``seed.py``:stä löytyvällä scriptillä sen varalta, että se toimii myös erittäin suurilla syötteillä. 10 miljoonalla käyttäjällä, viestillä ja miljoonalla postauksella tuli seuraavat tulokset ajastuksella:
```127.0.0.1 - - [25/Feb/2025 17:28:08] "GET /picture/999968 HTTP/1.1" 200 -
elapsed time: 0.00 seconds
127.0.0.1 - - [25/Feb/2025 17:28:08] "GET /picture/999967 HTTP/1.1" 200 -
elapsed time: 0.00 seconds
127.0.0.1 - - [25/Feb/2025 17:28:08] "GET /picture/999966 HTTP/1.1" 200 -
elapsed time: 0.00 seconds
127.0.0.1 - - [25/Feb/2025 17:28:08] "GET /picture/999965 HTTP/1.1" 200 -
elapsed time: 0.00 seconds
127.0.0.1 - - [25/Feb/2025 17:28:08] "GET /picture/999964 HTTP/1.1" 200 -
elapsed time: 0.00 seconds
127.0.0.1 - - [25/Feb/2025 17:28:08] "GET /picture/999963 HTTP/1.1" 200 -
elapsed time: 0.00 seconds
127.0.0.1 - - [25/Feb/2025 17:28:08] "GET /picture/999962 HTTP/1.1" 200 -
elapsed time: 0.00 seconds
127.0.0.1 - - [25/Feb/2025 17:28:08] "GET /picture/999961 HTTP/1.1" 200 -
elapsed time: 0.00 seconds
127.0.0.1 - - [25/Feb/2025 17:28:15] "GET /thread/999966 HTTP/1.1" 200 -
elapsed time: 0.00 seconds
127.0.0.1 - - [25/Feb/2025 17:28:15] "GET /picture/999966 HTTP/1.1" 200 -
