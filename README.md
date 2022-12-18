# BaariSovellus
    
    Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
    Jos käyttäjä on omistaja hän voi luoda baari.
    Omisaja voi poista omat ja muokka baarit.
    Käyttäjä näkee baarit kartalla ja voi painaa baari, jolloin siitä näytetään lisää tietoa (kuten kuvaus ja aukioloajat).
    Käyttäjä voi antaa arvion (arvon ja kommentti) baarista ja lukea muiden antamia arvioita.
    Käyttäjä voi poista oma arvion
    Ylläpitäjä voi lisätä ja poistaa baarit sekä määrittää baarista näytettävät tiedot.
    Käyttäjä voi etsiä kaikki baarit, joiden kuvauksessa on annettu sana.
    Käyttäjä näkee myös listan, jossa baarit on järjestetty parhaimmasta huonoimpaan arvioiden mukaisesti.
    Ylläpitäjä voi tarvittaessa poistaa käyttäjän antaman arvion.
 
 ## testaus
 pahoitelen yrittin niin kauan saada soveluksen toimimaan fly.io avulla mutta se ei onnistui
 ### asenus
 avaa Sovellus hakemiston
 
ajaa kommenton pip install requirements.txt tai poetry install.

asenta erikseen dotenv pip:illä.

asenta postgresql kursimaterialin avulla.

voit käyttäää dbDump tietokantan rakentamiseen    psql database < dbDump.

voit muokka .env tiedoston oikeiden arvoihin.

-Jos on ongelmia dotenv kanssa voit poista rivit 4 ja 6 app.py:stä ja manualisesti asentaa SECRET_KEY ja DATABASE_URL environment variables.
### testamisen
voit käyttää poetry shell tai venv.
kun olet virtuali ympäröstössä anta kommenon flask run HUOM! pitäis olla Sovellus hakemistossa kun annat komenton.

voit luo uusi käyttäjä jos haluat. tai käyttää Admin käyttäjä tunnuksella : admin  passo: admin

 ### Kuvat
 jos ei saa sovelluksen toimimaan on olemassa kuvat tiedosto misitä voit nähdä kaikki eri suvujen ulkoasut
