"""OS-moduuli mahdollistaa kaikkien tiedostojen läpi käymisen kansiossa."""
import os
import numpy as np
import matplotlib as plt
import ikkunasto as ik

tila = {
    "tekstilaatikko": None,
    "kineettiset": [],
    "intensiteetti": [],
    "pisteet":[],
    "kuvaaja":[],
    "taustanpoisto":[]
}

def lue_data(kansio):
    """
Lataa tiedostoja ohjelman muistiin ja lukee niistä datan. Tämän jälkeen luo kaksi listaa,
jossa toisessa on mitatut kineettiset energiat ja toisessa on summattuna jokainen
intensiteettispektri. Palauttaa nämä kyseiset listat ja
myös ladattujen tiedostojen määrät listana.
"""
# Tarkistaa jokaisen tiedoston valitusta kansioista.
    tiedostojenmaara = []
    # Katsoin mallia tästä artikkelista, että miten saan kaikki tiedostot käytyä läpi
    # https://stackoverflow.com/questions/18262293/how-to-open-every-file-in-a-folder
    for tiedosto in os.listdir(kansio):
        if tiedosto.startswith("measurement_") and tiedosto.endswith(".txt"):
            # Karsii tiedostot, joita ei tarvita.
            tiedostojenmaara.append(tiedosto)
            with open(os.path.join(kansio, tiedosto), 'r', encoding="utf-8") as data:
                dataluku = data.readlines()
                # Lukee datan rivi kerrallaan ja lisää sitä listoihin ehtojen mukaisesti
                for i, rivi in enumerate(dataluku):
                    rivi = rivi.split(" ")
                    rivi[0] = float(rivi[0])
                    rivi[1] = float(rivi[1])
                    # Täyttää sanakirjan kineettisillä arvoilla kerran
                    if len(tila["kineettiset"]) > 499:
                        pass
                    else:
                        tila["kineettiset"].append(rivi[0])
                    if len(tila["intensiteetti"]) < i+1:
                    # Täyttää listan, jotta siihen voidaan summata
                        tila["intensiteetti"].append(rivi[1])
                    else:
                    # Summaa edellä olevaan listaan tietyille indekseille tiedoston
                    # samojen indeksien arvot
                        tila["intensiteetti"][i] += rivi[1]
        else:
            pass
    return tila["kineettiset"], tila["intensiteetti"], tiedostojenmaara

def avaa_kansio():
    """
Napinkäsittelijä, jonka avulla käyttäjä voi valita kansion kansioselaimesta.
Funktion ladattua datan, se ilmoittaa käyttöliittymän tekstilaatikkoon
montako tiedostoa ladattiin.
"""
# Valitaan kansio, josta data luetaan.
    valittu = ik.avaa_hakemistoikkuna("kansio", ".")
# Ilmoitetaan, montako tiedostoa luettiin
    _, _, maarat = lue_data(valittu)
    ik.kirjoita_tekstilaatikkoon(tila["tekstilaatikko"], f"Tiedostoja ladattiin {len(maarat)}.")

def valitse_datapiste(hiiritapahtuma):
    """
Tallentaa hiirenklikkaustapahtuman tuplena ohjelman käytettäväksi.
"""
# Tallentaa hiiren klikkaukset sanakirjaan ohjelman käytettäväksi.
    piste1, piste2 = hiiritapahtuma.xdata, hiiritapahtuma.ydata
    monikko = tuple([piste1, piste2])
    tila["pisteet"].append(monikko)

def kuvaajan_piirto():
    """
Piirtää kuvaajan sanakirjan listoista ja ilmoittaa, jos kuvaajaa yritetään
piirtää ilman ladattua dataa
"""
# Jos kineettiset -listan pituus on nolla, ei dataa voida piirtää.
# Jos taas data on ladattu, piirtää ohjelma sen näkyviin sanakirjan listoista.
    if len(tila["kineettiset"]) == 0:
        ik.kirjoita_tekstilaatikkoon(tila["tekstilaatikko"],
        "Dataa ei ole ladattu. Lataa data, jotta kuvaaja voidaan piirtää")
    else:
        tila["kuvaaja"][2].plot(tila["kineettiset"], tila["intensiteetti"])
        tila["kuvaaja"][0].draw()

def laske_suoran_arvot(piste, piste_2):
    """
Laskee suoran kulmakertoimen ja vakiotermin parametreiksi syötetyistä klikkauksista
"""
# Laskee annetuista parametreistä kulmakertoimen ja vakion.
    x_1 = piste[0]
    y_1 = piste[1]
    x_2 = piste_2[0]
    y_2 = piste_2[1]
    kulmakerroin = (y_2 - y_1) / (x_2 - x_1)
    vakio = (((x_2 * y_1) - (x_1 * y_2)) / (x_2 - x_1))
    return kulmakerroin, vakio

def poista_lineaarinen_tausta():
    """
Poistaa kuvaajasta lineaarisen taustan käyttämällä käyttäjän klikkaamia pisteitä
hyödykseen. Muodostaa pisteistä suoran yhtälön, johon sijoitetaan kineettisten energioiden
arvot, jonka jälkeen tämä lopputulos vähenetään intensiteettiarvoista.
"""
    if len(tila["kineettiset"]) == 0:
        ik.kirjoita_tekstilaatikkoon(tila["tekstilaatikko"], f"Dataa ei ole ladattu."
        f" Lataa data, jotta kuvaajasta voidaan poistaa tausta.")
    else:
        try:
            # https://numpy.org/doc/stable/reference/generated/numpy.array.html
            # Käytin tätä dokumentaatiota apuna miinustaessani arvoja toisistansa.
            # Laskee aluksi kulmakertoimen ja vakion kahdesta viimeisimmästä klikatusta pisteestä
            k_kerroin, vakio_b = laske_suoran_arvot(tila["pisteet"][-1], tila["pisteet"][-2])
            # Jos pituus on alle kaksi, suoran arvoja ei voida laskea.
            # Tekee laskutoimituksen ja lisää arvot sanakirjaan talteen.
            for i in tila["kineettiset"]:
                tila["taustanpoisto"].append(k_kerroin * i + vakio_b)
            # Otin koodin listojen erotuksesta täältä
            # https://www.entechin.com/subtract-two-lists-python/
            # Vähentää listat toisistansa.
            erotus = np.array(tila["intensiteetti"]) - np.array(tila["taustanpoisto"])
            tila["kuvaaja"][2].plot(tila["kineettiset"], erotus)
            tila["kuvaaja"][0].draw()
            tila["intensiteetti"] = erotus
        except IndexError:
            ik.kirjoita_tekstilaatikkoon(tila["tekstilaatikko"], f"Pisteitä ei ole valittu."
            f" Valitse kaksi pistettä, jotta lineaarinen tausta voidaan poistaa.")

def integrointi():
    """
Laskee spektrin piikkien intensiteetit käyttäjän valitsemassa energiavälissä, jonka jälkeen
funktio laskee piikin pinta-alan ja ilmoittaa sen käyttäjälle.
"""
    #Tarkitaa onko dataa ladattu
    if len(tila["kineettiset"]) == 0:
        ik.kirjoita_tekstilaatikkoon(tila["tekstilaatikko"],
        "Dataa ei ole ladattu, joten integrointia ei voida suorittaa.")
    else:
        valiaikainen = []
        for i, piste in enumerate((tila["kineettiset"])):
            if tila["pisteet"][-2][0] <= tila["kineettiset"][i] <= tila["pisteet"][-1][0]:
                valiaikainen.append(i)
        alkupiste = valiaikainen[0]
        loppupiste = valiaikainen[-1]
        # Katsoin miten listoja "slicetaan" täältä:
        # https://www.geeksforgeeks.org/python-list-slicing/
        y_integraali = tila["intensiteetti"][alkupiste:loppupiste]
        x_integraali = tila["kineettiset"][alkupiste:loppupiste]
        tulos = np.trapz(y_integraali, x=x_integraali)
        ik.kirjoita_tekstilaatikkoon(tila["tekstilaatikko"], f"Energiavälin pinta-ala on"
        f" {tulos:.3f}.")

def tallenna_kuva():
    """
Tallentaa kuvaajan kuvana(png) käyttäjän valitsemaan kansioon valitulla nimellä.
Ilmoittaa jos dataa ei ole ladattuna ja kuvaa yritetään tallentaa.
"""
# Tarkistaa, onko dataa ladattu.
    if len(tila["kineettiset"]) == 0:
        ik.kirjoita_tekstilaatikkoon(tila["tekstilaatikko"],
        "Dataa ei ole ladattu, joten kuvaajaa ei voi tallentaa.")
    else:
        # Jos data on ladattu, tallentaa kuvan valittuun sijaintiin valitulla nimellä.
        tallennus = ik.avaa_tallennusikkuna("Tallenna")
        tila["kuvaaja"][1].savefig(tallennus)

def main():
    """
Luo käyttöliittymäikkunan, jossa on viisi nappia viidellä eri toiminnolla.
Käyttöliittymässä on aluksi kuvaajapohja, viisi nappia ja tekstilaatikko.
"""
    ikkuna = ik.luo_ikkuna("Ohjelma")
    nappikehys = ik.luo_kehys(ikkuna, ik.YLA)
    kuvaajakehys = ik.luo_kehys(nappikehys, ik.OIKEA)
    tekstikehys = ik.luo_kehys(kuvaajakehys, ik.ALA)
    ik.luo_nappi(nappikehys, "Lataa", avaa_kansio)
    ik.luo_nappi(nappikehys, "Piirrä", kuvaajan_piirto)
    ik.luo_nappi(nappikehys, "Poista lineaarinen tausta", poista_lineaarinen_tausta)
    ik.luo_nappi(nappikehys, "Integroi", integrointi)
    ik.luo_nappi(nappikehys, "Tallenna kuvaaja kuvana", tallenna_kuva)
    ik.luo_nappi(nappikehys, "Lopetus", ik.lopeta)
    kuvaaja = ik.luo_kuvaaja(kuvaajakehys, valitse_datapiste, leveys=700,
     korkeus=400)
    tila["kuvaaja"] = kuvaaja
    tila["kuvaaja"][2].set_xlabel("Kineettinen energia (eV)")
    tila["kuvaaja"][2].set_ylabel("Intensiteetti (mielivaltainen yksikkö)")
    tila["tekstilaatikko"] = ik.luo_tekstilaatikko(tekstikehys, leveys=80, korkeus=20)
    ik.kaynnista()

if __name__ == "__main__":
    main()
