# application.py
from datetime import datetime
from http.client import CREATED
from itertools import filterfalse
import json
import os
import sqlite3
import sys
from weakref import ref
from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for  # type: ignore
import stripe # type: ignore
from dateutil.relativedelta import relativedelta # type: ignore
from werkzeug.utils import secure_filename  # type: ignore # Make sure stripe is installed: pip install stripe

application = Flask(__name__)

application.secret_key = 'your_secret_key_here'  # Required for flashing messages


# Simulated user database
users = {}

# Add your project directory to the system path
project_home = '/home/Mourad0Ramli/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)



DATA_FILE = "data.json"

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f)
        
# Sample properties (replace or expand with real data)
PROPERTIES = [
    {
        "title": "Marina Apartment Agadir",
        "ville": "Agadir",
        "type": "Appartements",
        "max_adultes": 5,
        "max_enfants": 0,
        "url": "/Appartements01",
        "img": "/static/Appartements1-images/Agadir-photo1.jpg",
        "prix": "1 450 000 MAD",
        "alt": "Marina Apartment Agadir",
        "localisation": "🌍 Marina Agadir Morocco, 80000 Agadir, Maroc",
        "description": "Appartement à Agadir : 2 chambres, 1 salle de bains, salon, cuisine équipée, climatisation, Wi-Fi gratuit, piscine intérieure et extérieure, terrasse, jardin. Situé en bord de mer, Parking privé gratuit. À proximité de la plage d’Agadir, de la Marina et des ruines d’Agadir Oufella."
    },

    {
        "title": "Zephyr Agadir",
        "ville": "Agadir",
        "type": "Appartements",
        "max_adultes": 6,
        "max_enfants": 2,
        "url": "/Appartements02",
        "img": "/static/Appartements2-images/Zephyr-Agadir-Photo1.jpg",
        "prix": "980 000 MAD",
        "alt": "Zephyr Agadir",
        "localisation": "🌍 Lot 9, Secteur H, Founty, Agadir 80000 , Founty, 80000 Agadir, Maroc",
        "description": "Appartement Zephyr à Agadir – Quartier Founty : hébergements climatisés avec Wi‑Fi gratuit, salle de bains privative, télévision à écran plat, certains avec terrasse. Piscine extérieure, parking privé gratuit. À 1,7 km de la plage d’Agadir."
    },

    {
    "title": "ISLAN bay apartment Agadir",
    "ville": "Agadir",
    "type": "Appartements",
    "max_adultes": 2,
    "max_enfants": 1,
    "url": "/Appartements03",
    "img": "/static/Appartements3-images/ISLAN bay-photo1.jpg",
    "prix": "720 000 MAD",
    "alt": "ISLAN bay apartment Agadir",
    "localisation": "🌍 Residence ISLAN GH26, 80023 Agadir, Maroc",
    "description": "Appartement ISLAN Bay à Agadir : 1 chambre, salon, kitchenette, climatisation, Wi‑Fi gratuit, télévision à écran plat. Piscine privée, balcon et parking privé gratuit."
},
{
    "title": "Luxurious Sea-View 2Br Apartment Agadir",
    "ville": "Agadir",
    "type": "Appartements",
    "max_adultes": 5,
    "max_enfants": 4,
    "url": "/Appartements04",
    "img": "/static/Appartements4-images/Luxurious Sea-View 2Br-photo1.jpg",
    "prix": "1 450 000 MAD",
    "alt": "Luxurious Sea-View 2Br Apartment Agadir",
    "localisation": "🌍 Boite postale 1138 poste principale Agadir, Founty, 80000 Agadir, Maroc",
    "description": "Appartement Luxueux à Agadir : 2 chambres, cuisine équipée (réfrigérateur, lave-vaisselle), climatisation, Wi‑Fi gratuit, télévision par satellite, terrasse avec vue sur la mer et la ville. Piscine extérieure, jardin, parking privé gratuit."
},
{
    "title": "Tamourrit Apartment Taghazout",
    "ville": "Taghazout",
    "type": "Appartements",
    "max_adultes": 4,
    "max_enfants": 2,
    "url": "/Appartements05",
    "img": "/static/Appartements5-images/Tamourrit Apartment-photo1.jpg",
    "prix": "1 200 000 MAD",
    "alt": "Tamourrit Appartement Taghazout",
    "localisation": "🌍 Rue Taghazot, 80022 Taghazout, Maroc",
    "description": "Appartement à Taghazout : 1 chambre, 2 salles de bains, cuisine entièrement équipée (réfrigérateur, machine à café), salon, balcon avec vue sur la mer, terrasse, jardin. Accès direct à la plage, piscine extérieure, climatisation, Wi‑Fi gratuit, parking privé."
},
{
    "title": "Bouad Seafront apartment Taghazout",
    "ville": "Taghazout",
    "type": "Appartements",
    "max_adultes": 6,
    "max_enfants": 3,
    "url": "/Appartements06",
    "img": "/static/Appartements6-images/Bouad Seafront-photo1.jpg",
    "prix": "750 000 MAD",
    "alt": "Bouad Seafront apartment Taghazout",
    "localisation": "🌍 Hash Point, 65100 Taghazout, Maroc",
    "description": "Appartements en bord de mer à Taghazout, à 19 km d’Agadir. Hébergements avec cuisine, coin repas, salle de bains privative. Barbecue sur place, location de voitures disponible."
},
{
    "title": "Heavenly apartment Essaouira",
    "ville": "Essaouira",
    "type": "Appartements",
    "max_adultes": 4,
    "max_enfants": 0,
    "url": "/Appartements07",
    "img": "/static/Appartements7-images/Heavenly apartment-Photo1.jpg",
    "prix": "950 000 MAD",
    "alt": "Heavenly apartment Essaouira",
    "localisation": "🌍 Route Sidi Magdoul 1st floor, 44000 Essaouira, Maroc",
    "description": "Appartement avec vue mer à Essaouira, à 700 m de la plage et 3,7 km du Golf de Mogador. 2 chambres, salon, cuisine équipée, salle de bains avec douche. Wi-Fi gratuit, climatisation, terrasse et balcon avec vue sur la ville."
},
{
    "title": "New! Stunning and Comfortable apartement Marrakech",
    "ville": "Marrakech",
    "type": "Appartements",
    "max_adultes": 2,
    "max_enfants": 1,
    "url": "/Appartements08",
    "img": "/static/Appartements8-images/New ! Stunning and Comfortable apartement-photo1.jpg",
    "prix": "850 000 MAD",
    "alt": "New Stunning and Comfortable apartement Marrakech",
    "localisation": "🌍 JXMR+QR9, Rue el Imam Malik, Marrakech 40000, Maroc",
    "description": "Appartement moderne situé à Guéliz, Marrakech. 1 chambre, cuisine équipée, salle de bains, climatisation, Wi-Fi gratuit, parking privé."
},

{
    "title": "TheCasaEdition Gauthier Residency City Center Casablanca",
    "ville": "Casablanca",
    "type": "Appartements",
    "max_adultes": 4,
    "max_enfants": 1,
    "url": "/Appartements09",
    "img": "/static/Appartements9-images/TheCasaEdition Gauthier Residency City Center-photo1.jpg",
    "prix": "1 300 000 MAD",
    "alt": "TheCasaEdition Gauthier Residency City Center Casablanca",
    "localisation": "🌍 12 Rue Bachir El Ibrahim, Sidi Belyout, 20250 Casablanca, Maroc",
    "description": "TheCasaEdition Gauthier Residency City Center à Casablanca, à 400 m du centre. Hébergements climatisés avec balcon, cuisine équipée, Wi-Fi gratuit, terrasse et salle de bains privative."
},

{
    "title": "Rabat Agdal Pearl",
    "ville": "Rabat",
    "type": "Appartements",
    "max_adultes": 4,
    "max_enfants": 3,
    "url": "/Appartements010",
    "img": "/static/Appartements10-images/Rabat Agdal Pearl-photo1.jpg",
    "prix": "1 300 000 MAD",
    "alt": "Rabat Agdal Pearl",
    "localisation": "🌍 15 bis, Rue Jabal Bouiblane, Agdal, 10080 Rabat, Maroc",
    "description": "L’hébergement Rabat Agdal Pearl - Luxuriously Spacious & Well located se trouve à Rabat, à 700 m du Ministry of Higher Education et à 1,2 km du Ministry of Equipment. Il propose un appartement climatisé avec 2 chambres, cuisine équipée, Wi-Fi gratuit, terrasse et parking privé."
},
{
    "title": "Alma Prestigia Appartment Marrakech",
    "ville": "Marrakech",
    "type": "Appartements",
    "max_adultes": 3,
    "max_enfants": 4,
    "url": "/Appartements011",
    "img": "/static/Appartements11-images/Alma Prestigia Appartment-photo1.jpg",
    "prix": "1 200 000 MAD",
    "alt": "Alma Prestigia Appartment Marrakech",
    "localisation": "🌍 prestigia Corail, 40000 Marrakech, Maroc",
    "description": "Alma Prestigia Appartments à Marrakech propose Wi-Fi gratuit, piscine extérieure, jardin et terrasse. Certains logements climatisés avec TV, lave-linge et cuisine équipée. Restaurant sur place avec plats américains, belges, brésiliens et options halal sur demande."
},

{
    "title": "Sea view Mogador apartment Essaouira",
    "ville": "Essaouira",
    "type": "Appartements",
    "max_adultes": 3,
    "max_enfants": 1,
    "url": "/Appartements012",
    "img": "/static/Appartements12-images/Mogador apartment-photo1.jpg",
    "prix": "1 050 000 MAD",
    "alt": "Sea view Mogador apartment Essaouira",
    "localisation": "🌍 شارع محمد الخامس, 44100 Essaouira, Maroc",
    "description": "Sea view apartment Mogador à Essaouira, à 500 m de la plage. Appartement 1 chambre avec piscine privée, jardin, Wi-Fi gratuit et parking privé. Cuisine équipée, 2 salles de bains, linge et articles de toilette fournis."
},

{
    "title": "L'Orientale By La Siredrah-Marrakech",
    "ville": "Marrakech",
    "type": "Maisons",
    "max_adultes": 6,
    "max_enfants": 0,
    "url": "/Maisons1",
    "img": "/static/Maisons1-images/L'Orientale By La Siredrah-photo1.jpg",
    "prix": "1 350 000 MAD",
    "alt": "L'Orientale By La Siredrah-Marrakech",
    "localisation": "🌍 Route Amizmiz Km 7, 40000 Marrakech, Maroc",
    "description": "Maison d’hôte à Marrakech : chambres clim., Wi‑Fi, TV, piscine, jardin, resto, bar, navette aéroport, réception 24h."
},
{
    "title": "Yanis Guest House-Marrakech",
    "ville": "Marrakech",
    "type": "Maisons",
    "max_adultes": 5,
    "max_enfants": 1,
    "url": "/Maisons2",
    "img": "/static/Maisons2-images/Yanis Guest House-Photo1.jpg",
    "prix": "1 250 000 MAD",
    "alt": "Yanis Guest House-Marrakech",
    "localisation": "🌍 DR SOUDANI, 540 Rte de Targa, 40000 Marrakech, Maroc",
    "description": "Maison d’hôte à Rabat (800 m plage) : chambres clim., patio, cuisine équipée, Wi‑Fi, terrasse, navette aéroport, réception 24h."
},
{
    "title": "RIAD LALLA ZINEB-Rabat",
    "ville": "Rabat",
    "type": "Maisons",
    "max_adultes": 6,
    "max_enfants": 3,
    "url": "/Maisons3",
    "img": "/static/Maisons3-images/RIAD LALLA ZINEB-Photo1.jpg",
    "prix": "2 700 000 MAD",
    "alt": "RIAD LALLA ZINEB-Rabat",
    "localisation": "🌍 Rue el Kobba, Médina, Rabat, Maroc",
    "description": "Maison d’hôte : 3 chambres SDB, clim., Wi‑Fi, 2 piscines ext., resto, parking, navette aéroport."
},

{
    "title": "Pearl Surf Camp Morocco-Agadir",
    "ville": "Agadir",
    "type": "Maisons",
    "max_adultes": 2,
    "max_enfants": 1,
    "url": "/Maisons4",
    "img": "/static/Maisons4-images/Pearl Surf Camp Morocco-Photo1.jpg",
    "prix": "1 330 000 MAD",
    "alt": "Pearl Surf Camp Morocco-Agadir",
    "localisation": "🌍 Km 26 route d'Essaouira, Imi Ouaddar, 80750 Agadir, Maroc",
    "description": "Maison d’hôte à Agadir, à 400 m de la plage. Chambres avec Wi‑Fi, jardin, terrasse, parking gratuit. Proche Atlantica Parc, Golf Tazegzout et port. Petit-déjeuner inclus."
},
{
    "title": "Single fin taghazout surf & stay",
    "ville": "Taghazout",
    "type": "Maisons",
    "max_adultes": 4,
    "max_enfants": 2,
    "url": "/Maisons5",
    "img": "/static/Maisons5-images/Single fin taghazout surf & stay-Photo1.jpg",
    "prix": "2 500 000 MAD",
    "alt": "Single fin taghazout surf & stay",
    "localisation": "🌍 Centre Taghazout, 80022 Taghazout, Maroc",
    "description": "Auberge surf & détente à Taghazout, chambres avec vue montagne, piscine intérieure, terrasse et cuisine commune."
},
{
    "title": "Riad Dar Sarah-Taghazout",
    "ville": "Taghazout",
    "type": "Maisons",
    "max_adultes": 2,
    "max_enfants": 1,
    "url": "/Maisons6",
    "img": "/static/Maisons6-images/Riad Dar Sarah-photo1.jpg",
    "prix": "1 330 000 MAD",
    "alt": "Riad Dar Sarah",
    "localisation": "🌍 Ait Bihi, 80022 Taghazout, Maroc",
    "description": "Riad de charme à Taghazout avec chambres vue montagne, piscine intérieure, terrasse, jardin et restaurant marocain."
},
{
    "title": "Dar Tahra-Casablanca",
    "ville": "Casablanca",
    "type": "Maisons",
    "max_adultes": 3,
    "max_enfants": 3,
    "url": "/Maisons7",
    "img": "/static/Maisons7-images/Dar Tahra-photo1.jpg",
    "prix": "1 270 000 MAD",
    "alt": "Dar Tahra",
    "localisation": "🌍 78, Boulevard Dammam Angle Bd Panoramique. Technopark , Aïn Chock, 20000 Casablanca, Maroc",
    "description": "Maison d’hôtes de charme à 15 min du centre de Casablanca, avec jardin, piscine extérieure, hammam et salons marocains. Chambres climatisées avec vue, Wi-Fi gratuit et petit-déjeuner inclus."
},
{
    "title": "LHOSTEL à Casablanca",
    "ville": "Casablanca",
    "type": "Maisons",
    "max_adultes": 5,
    "max_enfants": 3,
    "url": "/Maisons8",
    "img": "/static/Maisons8-images/LHOSTEL à Casablanca-photo1.jpg",
    "prix": "580 000 MAD",
    "alt": "LHOSTEL à Casablanca",
    "localisation": "🌍 6, rue d'Aix Oasis, Maârif, 20410 Casablanca, Maroc",
    "description": "Auberge conviviale à Casablanca avec jardin, terrasse, cuisine commune et Wi-Fi gratuit. Petit-déjeuner buffet, parking privé, proche centre-ville et transports."
},
{
    "title": "Auberge Les Montagnes du Paradis-Agadir",
    "ville": "Agadir",
    "type": "Maisons",
    "max_adultes": 3,
    "max_enfants": 2,
    "url": "/Maisons9",
    "img": "/static/Maisons9-images/Auberge Les Montagnes du Paradis-photo1.jpg",
    "prix": "850 000 MAD",
    "alt": "Auberge Les Montagnes du Paradis-Agadir",
    "localisation": "🌍 6, rue d'Aix Oasis, Maârif, 20410 Casablanca, Maroc",
    "description": "Auberge conviviale à Casablanca avec jardin, terrasse, cuisine commune et Wi-Fi gratuit. Petit-déjeuner buffet, parking privé, proche centre-ville et transports."
},
{
    "title": "Riad Dar Rabiaa-Rabat",
    "ville": "Rabat",
    "type": "Maisons",
    "max_adultes": 6,
    "max_enfants": 4,
    "url": "/Maisons10",
    "img": "/static/Maisons10-images/Riad Dar Rabiaa-photo1.jpg",
    "prix": "1 150 000 MAD",
    "alt": "Riad Dar Rabiaa-Rabat",
    "localisation": "🌍 Rue Hotel Chorfas 7, Médina, 10000 Rabat, Maroc",
    "description": "Riad authentique au cœur de Rabat, proche de la plage, de la Kasbah des Oudayas et de la Tour Hassan. Piscine intérieure, terrasse, bar, Wi-Fi gratuit et chambres climatisées."
},
{
    "title": "Riad Dar Awil-Essaouira",
    "ville": "Essaouira",
    "type": "Maisons",
    "max_adultes": 2,
    "max_enfants": 2,
    "url": "/Maisons11",
    "img": "/static/Maisons11-images/Riad Dar Awil-photo1.jpg",
    "prix": "935 000 MAD",
    "alt": "Riad Dar Awil-Essaouira",
    "localisation": "🌍 58 Rue d'Agadir Essaouira, Ahl Agadir, 44000 Essaouira, Maroc",
    "description": "Riad Dar Awil à Essaouira, avec salon commun, terrasse, restaurant, réception 24h/24, transferts aéroport, et vue sur la ville."
},
{
    "title": "RIAD MAROSKO-Essaouira",
    "ville": "Essaouira",
    "type": "Maisons",
    "max_adultes": 6,
    "max_enfants": 2,
    "url": "/Maisons12",
    "img": "/static/Maisons12-images/RIAD MAROSKO-photo1.jpg",
    "prix": "968 000 MAD",
    "alt": "RIAD MAROSKO Essaouira",
    "localisation": "🌍 66 Rue d'Agadir, Ahl Agadir, 44000 Essaouira, Maroc",
    "description": "Maison d’hôtes à Essaouira, quartier Ahl Agadir, avec patio, terrasse, Wi-Fi gratuit et petit-déjeuner servi sur place. À 700 m de la plage et 6 km du Golf de Mogador."
},
{
    "title": "RIAD MAROSKO-Essaouira",
    "ville": "Essaouira",
    "type": "Maisons",
    "max_adultes": 2,
    "max_enfants": 2,
    "url": "/Maisons12",
    "img": "/static/Maisons12-images/RIAD MAROSKO-photo1.jpg",
    "prix": "968 000 MAD",
    "alt": "RIAD MAROSKO Essaouira",
    "localisation": "🌍 66 Rue d'Agadir, Ahl Agadir, 44000 Essaouira, Maroc",
    "description": "Maison d’hôtes à Essaouira, quartier Ahl Agadir, avec patio, terrasse, Wi-Fi gratuit et petit-déjeuner servi sur place. À 700 m de la plage et 6 km du Golf de Mogador."
},
{
    "title": "Villa Darbouazza-Casablanca",
    "ville": "Casablanca",
    "type": "Villas",
    "max_adultes": 4,
    "max_enfants": 2,
    "url": "/Villas1",
    "img": "/static/Villas1-images/Villa Darbouazza-photo1.jpg",
    "prix": "3 800 000 MAD",
    "alt": "Villa Darbouazza-Casablanca",
    "localisation": "🌍 Dar Bouazza, 27223 Casablanca, Maroc",
    "description": "Villa à Casablanca : 2 chambres, clim., Wi‑Fi, TV, cuisine équipée, piscine intérieure & privée, jardin, terrasse, parking gratuit, à 400 m de Jack Beach et 16 km du Morocco Mall."
},
{
    "title": "Villa de Luxe piscine privée-Casablanca",
    "ville": "Casablanca",
    "type": "Villas",
    "max_adultes": 6,
    "max_enfants": 3,
    "url": "/Villas2",
    "img": "/static/Villas2-images/Villa de Luxe piscine privée-photo1.jpg",
    "prix": "3 916 000 MAD",
    "alt": "Villa de Luxe piscine privée",
    "localisation": "🌍 Villa N 14 Residence Hyde Park Bouskoura Casablanca, 27182 Casablanca, Maroc",
    "description": "Villa à Casablanca : 3 chambres, clim., Wi‑Fi, TV, cuisine équipée, 4 salles de bain, piscine extérieure & privée, jardin, terrasse, parking gratuit, à 17 km d’Anfa Place et 19 km de la Mosquée Hassan II."
},
{
    "title": "Villa Nawal-Agadir",
    "ville": "Agadir",
    "type": "Villas",
    "max_adultes": 4,
    "max_enfants": 2,
    "url": "/Villas3",
    "img": "/static/Villas3-images/Villa Nawal-photo1.jpg",
    "prix": "3 200 000 MAD",
    "alt": "Villa Nawal-Agadi",
    "localisation": "🌍 Villa 8 Dyar Shemsi, 83005 Agadir, Maroc",
    "description": "Villa à Agadir : 2 chambres, 2 SDB, clim., Wi‑Fi, salon, cuisine équipée, piscine privée chauffée sans vis-à-vis, terrasse, jardin, parking gratuit."
},
{
    "title": "Villa Palmeraie Golf Agadir",
    "ville": "Agadir",
    "type": "Villas",
    "max_adultes": 6,
    "max_enfants": 3,
    "url": "/Villas4",
    "img": "/static/Villas4-images/Villa Palmeraie Golf Agadir-photo1.jpg",
    "prix": "3 234 000 MAD",
    "alt": "Villa Palmeraie Golf Agadir",
    "localisation": "🌍 Domaine la palmeraie II Aghroude Bensergao Villa 16, 80100 Agadir, Maroc",
    "description": "Villa à Agadir : 4 chambres, 3 SDB, clim., Wi‑Fi, salon, cuisine équipée, piscine privée, terrasse, jardin, parking gratuit."
},
{
    "title": "Villa Camélia des 3 Z-Marrakech",
    "ville": "Marrakech",
    "type": "Villas",
    "max_adultes": 6,
    "max_enfants": 2,
    "url": "/Villas5",
    "img": "/static/Villas5-images/Villa Camélia des 3 Z-photo1.jpg",
    "prix": "2 750 000 MAD",
    "alt": "Villa Camélia des 3 Z",
    "localisation": "🌍 Résidence River Palm Palmeraie Villa 128, 40060 Marrakech, Maroc",
    "description": "Villa à Marrakech : 3 chambres, 3 SDB, clim., Wi‑Fi, salon, cuisine équipée, piscine privée, spa, parc aquatique, terrasse, jardin, parking gratuit."
},
{
    "title": "Villa de luxe à Marrakech",
    "ville": "Marrakech",
    "type": "Villas",
    "max_adultes": 5,
    "max_enfants": 4,
    "url": "/Villas6",
    "img": "/static/Villas6-images/Villa de luxe à Marrakech-photo1.jpg",
    "prix": "6 500 000 MAD",
    "alt": "Villa de luxe à Marrakech",
    "localisation": "🌍 Dar jihane Amezrou ltehtani, sidi abdellah ghiat, Marrakech, Maroc",
    "description": "Villa à Marrakech : 4 chambres, 4 SDB, clim., Wi‑Fi, salon, cuisine équipée, piscine privée, jardin, terrasse, parking gratuit. Vue sur les montagnes."
},
{
    "title": "SUPERBE VILLA-Rabat",
    "ville": "Rabat",
    "type": "Villas",
    "max_adultes": 6,
    "max_enfants": 1,
    "url": "/Villas7",
    "img": "/static/Villas7-images/SUPERBE VILLA-photo1.jpg",
    "prix": "3 560 000 MAD",
    "alt": "SUPERBE VILLA",
    "localisation": "🌍 VILLA 54 A2B, 10000 Rabat, Maroc",
    "description": "Villa à Rabat : 3 chambres, 1 SDB, clim., Wi‑Fi, salon, cuisine équipée, piscine privée intérieure et extérieure, bain à remous, terrasse, jardin, barbecue, parking gratuit. À quelques pas de la plage des Nations."
},
{
    "title": "Villa 3 Charme et Vue Mer Face-Rabat",
    "ville": "Rabat",
    "type": "Villas",
    "max_adultes": 5,
    "max_enfants": 4,
    "url": "/Villas8",
    "img": "/static/Villas8-images/Villa 3 Charme et Vue Mer Face-photo1.jpg",
    "prix": "3 000 000 MAD",
    "alt": "Villa 3 Charme et Vue Mer Face",
    "localisation": "🌍 Le Mall du Carrousel, 10000 Rabat, Maroc",
    "description": "Villa à Rabat : 1 chambre, 2 SDB, clim., salon, cuisine équipée, télévision à écran plat, balcon, terrasse, jardin. Située en bord de mer, à proximité du Carrousel Mall. À 7 km de la Bibliothèque nationale et 8,2 km de la Kasbah des Oudayas."
},
{
    "title": "Villa BERBERINE-Essaouira",
    "ville": "Essaouira",
    "type": "Villas",
    "max_adultes": 6,
    "max_enfants": 4,
    "url": "/Villas9",
    "img": "/static/Villas9-images/Villa BERBERINE-photo1.jpg",
    "prix": "4 260 000 MAD",
    "alt": "Villa BERBERINE",
    "localisation": "🌍 DOUAR BOUZAMA- IDA OUGUERD, 44000 Essaouira, Maroc",
    "description": "Villa à Essaouira : 4 chambres, 4 SDB, Wi‑Fi gratuit, salon commun, cuisine équipée, télévision à écran plat, jardin, terrasse avec vue. Piscine extérieure et piscine privée."
},
{
    "title": "Villa Serinie-Essaouira",
    "ville": "Essaouira",
    "type": "Villas",
    "max_adultes": 5,
    "max_enfants": 4,
    "url": "/Villas10",
    "img": "/static/Villas10-images/Villa Serinie-photo1.jpg",
    "prix": "2 725 000 MAD",
    "alt": "Villa Serinie",
    "localisation": "🌍 P2212, 44000 Essaouira, Maroc",
    "description": "Villa à Essaouira : 4 chambres, 4 SDB, climatisation, Wi‑Fi gratuit, salon, cuisine entièrement équipée, télévision à écran plat, jardin, terrasse avec vue sur la montagne. Piscine extérieure privée."
},
{
    "title": "Kiola Villa-Taghazout",
    "ville": "Taghazout",
    "type": "Villas",
    "max_adultes": 6,
    "max_enfants": 2,
    "url": "/Villas11",
    "img": "/static/Villas11-images/Kiola Villa-photo1.jpg",
    "prix": "5 800 000 MAD",
    "alt": "Kiola Villa-Taghazout",
    "localisation": "🌍 Ifraden Taghazout, 80022 Taghazout, Maroc",
    "description": "Villa à Taghazout : 4 chambres, 4 salles de bains, climatisation, Wi-Fi gratuit, piscine extérieure privée, jardin, terrasse avec vue sur la mer, parking privé gratuit, à proximité du Golf Tazegzout et de l’Atlantica Parc Aquatique."
},
{
    "title": "Lemon Grove Villa Taghazout",
    "ville": "Taghazout",
    "type": "Villas",
    "max_adultes": 6,
    "max_enfants": 1,
    "url": "/Villas12",
    "img": "/static/Villas12-images/Lemon Grove Villa Taghazout-photo1.jpg",
    "prix": "4 200 000 MAD",
    "alt": "Lemon Grove Villa Taghazout",
    "localisation": "🌍 Residence Amda Taghazout Bay villa 93, 80022 Taghazout, Maroc",
    "description": "Villa à Taghazout : 3 chambres, 2 salles de bains, climatisation, piscine privée, balcon, terrasse, jardin, parking privé gratuit, à 1,9 km de la plage de Taghazout, proche du Golf Tazegzout et du port d’Agadir."
},
    # Add more properties if needed
]


@application.route("/results")
def results():
    type_ = request.args.get("type")
    ville = request.args.get("ville")
    adultes = request.args.get("adultes")
    enfants = request.args.get("enfants")

    # Convert to int for comparison (guard against errors)
    try:
        adultes = int(adultes) if adultes else 0
        enfants = int(enfants) if enfants else 0
    except ValueError:
        adultes = 0
        enfants = 0

    filtered = [
        prop for prop in PROPERTIES
        if (not type_ or prop["type"] == type_)
        and (not ville or prop["ville"] == ville)
        and prop.get("max_adultes", 0) >= adultes
        and prop.get("max_enfants", 0) >= enfants
    ]

    return render_template("results.html", properties=filtered)





# ------------------------ Routes ------------------------
@application.route('/')
@application.route('/Accueil')
def Accueil():

    return render_template("Accueil.html")

@application.route('/Mourad')
def Mourad():
    return render_template('Mourad.html')

@application.route('/Taha')
def Taha():
    return render_template('Taha.html')

@application.route('/Tismane')
def Tismane():
    return render_template('Tismane.html')

@application.route('/Yahya')
def Yahya():
    return render_template('Yahya.html')


@application.route('/ACHATS-VENTES/Appartements')
def appartements():
    return render_template('Appartements.html')

@application.route('/ACHATS-VENTES/Maisons')
def maisons():
    return render_template('Maisons.html')

@application.route('/Maisons1')
def Maisons1():
    return render_template('Maisons-dossier/Maisons1.html')

@application.route('/Maisons2')
def Maisons2():
    return render_template('Maisons-dossier/Maisons2.html')

@application.route('/Maisons3')
def Maisons3():
    return render_template('Maisons-dossier/Maisons3.html')

@application.route('/Maisons4')
def Maisons4():
    return render_template('Maisons-dossier/Maisons4.html')

@application.route('/Maisons5')
def Maisons5():
    return render_template('Maisons-dossier/Maisons5.html')

@application.route('/Maisons6')
def Maisons6():
    return render_template('Maisons-dossier/Maisons6.html')

@application.route('/Maisons7')
def Maisons7():
    return render_template('Maisons-dossier/Maisons7.html')

@application.route('/Maisons8')
def Maisons8():
    return render_template('Maisons-dossier/Maisons8.html')

@application.route('/Maisons9')
def Maisons9():
    return render_template('Maisons-dossier/Maisons9.html')

@application.route('/Maisons10')
def Maisons10():
    return render_template('Maisons-dossier/Maisons10.html')

@application.route('/Maisons11')
def Maisons11():
    return render_template('Maisons-dossier/Maisons11.html')

@application.route('/Maisons12')
def Maisons12():
    return render_template('Maisons-dossier/Maisons12.html')

@application.route('/ACHATS-VENTES/Villas')
def villas():
    return render_template('villas.html')

@application.route('/Villas1')
def Villas1():
    return render_template('Villas-dossier/Villas1.html')

@application.route('/Villas2')
def Villas2():
    return render_template('Villas-dossier/Villas2.html')

@application.route('/Villas3')
def Villas3():
    return render_template('Villas-dossier/Villas3.html')

@application.route('/Villas4')
def Villas4():
    return render_template('Villas-dossier/Villas4.html')

@application.route('/Villas5')
def Villas5():
    return render_template('Villas-dossier/Villas5.html')

@application.route('/Villas6')
def Villas6():
    return render_template('Villas-dossier/Villas6.html')

@application.route('/Villas7')
def Villas7():
    return render_template('Villas-dossier/Villas7.html')

@application.route('/Villas8')
def Villas8():
    return render_template('Villas-dossier/Villas8.html')

@application.route('/Villas9')
def Villas9():
    return render_template('Villas-dossier/Villas9.html')

@application.route('/Villas10')
def Villas10():
    return render_template('Villas-dossier/Villas10.html')

@application.route('/Villas11')
def Villas11():
    return render_template('Villas-dossier/Villas11.html')

@application.route('/Villas12')
def Villas12():
    return render_template('Villas-dossier/Villas12.html')

@application.route('/Contact')
def contact():
    return render_template('Contact.html')

@application.route('/Site')
def site():
    return render_template('Site.html')

@application.route('/longuedureeAppartements1')
def longuedureeAppartements1():
    return render_template('longue-duree-dossier/longue-dureeAppartements1.html')

@application.route('/longuedureeAppartements2')
def longuedureeAppartements2():
    return render_template('longue-duree-dossier/longue-dureeAppartements2.html')

@application.route('/longuedureeAppartements3')
def longuedureeAppartements3():
    return render_template('longue-duree-dossier/longue-dureeAppartements3.html')

@application.route('/longuedureeMaisons1')
def longuedureeMaisons1():
    return render_template('longue-duree-dossier/longue-dureeMaisons1.html')

@application.route('/longuedureeMaisons2')
def longuedureeMaisons2():
    return render_template('longue-duree-dossier/longue-dureeMaisons2.html')

@application.route('/longuedureeMaisons3')
def longuedureeMaisons3():
    return render_template('longue-duree-dossier/longue-dureeMaisons3.html')

@application.route('/longuedureeVillas1')
def longuedureeVillas1():
    return render_template('longue-duree-dossier/longue-dureeVillas1.html')

@application.route('/longuedureeVillas2')
def longuedureeVillas2():
    return render_template('longue-duree-dossier/longue-dureeVillas2.html')

@application.route('/longuedureeVillas3')
def longuedureeVillas3():
    return render_template('longue-duree-dossier/longue-dureeVillas3.html')

@application.route('/JournaliereAppartements1')
def JournaliereAppartements1():
    return render_template('Journaliere-dossier/JournaliereAppartements1.html')

@application.route('/JournaliereAppartements2')
def JournaliereAppartements2():
    return render_template('Journaliere-dossier/JournaliereAppartements2.html')

@application.route('/JournaliereAppartements3')
def JournaliereAppartements3():
    return render_template('Journaliere-dossier/JournaliereAppartements3.html')

@application.route('/JournaliereMaisons1')
def JournaliereMaisons1():
    return render_template('Journaliere-dossier/JournaliereMaisons1.html')

@application.route('/JournaliereMaisons2')
def JournaliereMaisons2():
    return render_template('Journaliere-dossier/JournaliereMaisons2.html')

@application.route('/JournaliereMaisons3')
def JournaliereMaisons3():
    return render_template('Journaliere-dossier/JournaliereMaisons3.html')

@application.route('/JournaliereVillas1')
def JournaliereVillas1():
    return render_template('Journaliere-dossier/JournaliereVillas1.html')

@application.route('/JournaliereVillas2')
def JournaliereVillas2():
    return render_template('Journaliere-dossier/JournaliereVillas2.html')

@application.route('/JournaliereVillas3')
def JournaliereVillas3():
    return render_template('Journaliere-dossier/JournaliereVillas3.html')


@application.route('/Appartements01')
def Appartements01():
    return render_template('Appartements-dossier/Appartements1.html')

@application.route('/Appartements02')
def Appartements02():
    return render_template('Appartements-dossier/Appartements2.html')

@application.route('/Appartements03')
def Appartements03():
    return render_template('Appartements-dossier/Appartements3.html')

@application.route('/Appartements04')
def Appartements04():
    return render_template('Appartements-dossier/Appartements4.html')

@application.route('/Appartements05')
def Appartements05():
    return render_template('Appartements-dossier/Appartements5.html')

@application.route('/Appartements06')
def Appartements06():
    return render_template('Appartements-dossier/Appartements6.html')

@application.route('/Appartements07')
def Appartements07():
    return render_template('Appartements-dossier/Appartements7.html')

@application.route('/Appartements08')
def Appartements08():
    return render_template('Appartements-dossier/Appartements8.html')

@application.route('/Appartements09')
def Appartements09():
    return render_template('Appartements-dossier/Appartements9.html')

@application.route('/Appartements010')
def Appartements010():
    return render_template('Appartements-dossier/Appartements10.html')

@application.route('/Appartements011')
def Appartements011():
    return render_template('Appartements-dossier/Appartements11.html')

@application.route('/Appartements012')
def Appartements012():
    return render_template('Appartements-dossier/Appartements12.html')

@application.route('/account')
def account():
    data = load_data()  # Load from file instead of session
    return render_template('loginTIGMINO.html', contact_data=data)

@application.route('/Réglages')
def Réglages():
    return render_template('settingsTIGMINO.html')

@application.route('/Réglages2')
def Réglages2():
    return render_template('settingsTIGMINO2.html')


# Fake in-memory database
users = {}

@application.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # ✅ If email already exists, flash error message and redirect
    if email in users:
        flash("❌ Cet email est déjà utilisé.")
        return redirect(request.referrer or url_for('Accueil'))

    # ✅ Register new user
    users[email] = {
        'username': username,
        'password': password
    }

    session['user'] = email
    session['username'] = username
    return redirect(request.referrer or url_for('Accueil'))


@application.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # ✅ Show error only when login fails
    if email not in users or users[email]['password'] != password:
        flash("❌ Identifiants incorrects.")
        return redirect(request.referrer or url_for('Accueil'))

    session['user'] = email
    session['username'] = users[email]['username']
    return redirect(request.referrer or url_for('Accueil'))


@application.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('username', None)
    return redirect(url_for('Accueil'))







@application.route('/search_ads', methods=['POST'])
def search_ads():
    query = request.form.get('search')
    # Add your filter logic here
    results = filterfalse(query)  # Suppose this is a function you created
    return render_template('dashboard.html', ads=results)





@application.route("/Réglages2", methods=["GET", "POST"])
def password_settings():
    if 'user' not in session:
        return redirect("/Réglages2")  # Not logged in

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        user_email = session['user']
        user_data = users.get(user_email)

        if user_data is None:
            flash("❌ Utilisateur introuvable.")
        elif current_password != user_data['password']:
            flash("❌ Mot de passe actuel incorrect.")
        elif new_password != confirm_password:
            flash("❌ Les nouveaux mots de passe ne correspondent pas.")
        else:
            users[user_email]['password'] = new_password
            flash("✅ Mot de passe changé avec succès !")

    return render_template("settingsTIGMINO2.html")







@application.route("/Réglages", methods=["GET", "POST"])
def reglages():
    if request.method == "POST":
        info = {
            "message": request.form["message"],
            "city": request.form["city"],
            "adultes": request.form["adultes"],
            "enfants": request.form["enfants"],
            "type": request.form["type"],
        }

        data = load_data()
        data.append(info)
        save_data(data)

        return redirect("/account")

    return render_template("settingsTIGMINO.html")






@application.route("/clear_all", methods=["POST"])
def clear_all():
    save_data([])  # Clear JSON file
    return redirect("/account")


@application.route("/login")
def login_page():
    data = load_data()
    return render_template("loginTIGMINO.html", data=data)

@application.route("/delete/<int:index>", methods=["POST"])
def delete_entry(index):
    data = load_data()
    if 0 <= index < len(data):
        del data[index]
        save_data(data)
    return redirect("/account")







UPLOAD_FOLDER = 'static/uploads'
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Make sure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@application.route("/profilepic", methods=["GET", "POST"])
def profilepic():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        file = request.files.get("profile_pic")
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join(application.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Delete old profile picture if exists
            old = session.get("profile_pic")
            if old and old != filename:
                try:
                    os.remove(os.path.join(application.config["UPLOAD_FOLDER"], old))
                except:
                    pass

            session["profile_pic"] = filename
            flash("✅ Photo téléchargée avec succès !")
            return redirect("/profilepic")

    return render_template("profile_picture.html")

@application.route("/remove_profile_pic", methods=["POST"])
def remove_profile_pic():
    if "user" in session:
        pic = session.pop("profile_pic", None)
        if pic:
            try:
                os.remove(os.path.join(application.config["UPLOAD_FOLDER"], pic))
            except:
                pass
        flash("🗑️ Photo supprimée.")
    return redirect("/profilepic")



@application.route("/locations/journaliere", methods=["GET"]) 
def locations_journaliere():
    ville = request.args.get("ville")
    adultes = request.args.get("adultes")
    enfants = request.args.get("enfants")
    date_depart = request.args.get("date_depart")
    date_retour = request.args.get("date_retour")

    today = datetime.today().strftime('%Y-%m-%d')
    days_difference = None
    weeks_difference = None

    # Safe conversion
    try:
        adultes = int(adultes) if adultes else 0
        enfants = int(enfants) if enfants else 0
    except ValueError:
        adultes = 0
        enfants = 0

    # Duration calculation
    if date_depart and date_retour:
        try:
            d1 = datetime.strptime(date_depart, "%Y-%m-%d")
            d2 = datetime.strptime(date_retour, "%Y-%m-%d")
            delta = d2 - d1
            days_difference = delta.days
            weeks_difference = days_difference // 7
        except ValueError:
            days_difference = None
            weeks_difference = None

    # Filtering
    matching_cards = [
        prop for prop in SHORT_TERM_PROPERTIES
        if (not ville or prop["ville"] == ville)
        and prop.get("max_adultes", 0) >= adultes
        and prop.get("max_enfants", 0) >= enfants
    ]

    return render_template(
        "locations journaliere.html",
        ville=ville,
        adultes=adultes,
        enfants=enfants,
        date_depart=date_depart,
        date_retour=date_retour,
        days=days_difference,
        weeks=weeks_difference,
        today=today,
        cards=matching_cards
    )



SHORT_TERM_PROPERTIES = [

    {
        "title": "Atlantic Palm Beach-Agadir",
        "ville": "Agadir",
        "type": "Appartements",
        "max_adultes": 2,
        "max_enfants": 4,
        "url": "/JournaliereAppartements1",
        "img": "/static/JournaliereAppartements1/Atlantic Palm Beach-photo1.jpg",
        "prix": "18 957 MAD / jours",
        "alt": "Atlantic Palm Beach",
        "localisation": "🌍 City Founty A1 Secteur A Zone Touristique, Agadir 80000c",
        "description": "Appart. avec clim, Wi-Fi gratuit, piscine, vue mer/piscine. Resto, services, près aéroport (19 km)."
    },
    {
        "title": "Panorama Guesthouse-Agadir",
        "ville": "Agadir",
        "type": "Maisons",
        "max_adultes": 2,
        "max_enfants": 4,
        "url": "/JournaliereMaisons1",
        "img": "/static/JournaliereMaisons1/Panorama Guesthouse-photo1.jpg",
        "prix": "33 701 MAD / jours",
        "alt": "Panorama Guesthouse",
        "localisation": "🌍 CR AOURIR, DR OUBAHA TAMRAGHTE, Agadir 80000",
        "description": "Chambres avec balcon vue mer, jardin, terrasse, cuisine partagée, Wi-Fi. Piscine int., loc. vélos/voitures, navette aéroport (36 km)."
    },
    {
        "title": "Villa de Luxe - Agadir City",
        "ville": "Agadir",
        "type": "Villas",
        "max_adultes": 3,
        "max_enfants": 4,
        "url": "/JournaliereVillas1",
        "img": "/static/JournaliereVillas1/Villa de Luxe - Agadir City-photo1.jpg",
        "prix": "58 528 MAD / jours",
        "alt": "Villa de Luxe - Agadir City",
        "localisation": "🌍 Agadir, Maroc",
        "description": "Villa 4 ch. à Agadir avec piscine privée, jardin, terrasse vue ville/montagne. Cuisine équipée, 3 sdb. Sauna, hammam, parking gratuit. À 6 km de la Marina, 20 km aéroport."
    },
    {
        "title": "AFRICA SURF HOUSE-Taghazout",
        "ville": "Taghazout",
        "type": "Appartements",
        "max_adultes": 5,
        "max_enfants": 2,
        "url": "/JournaliereAppartements2",
        "img": "/static/JournaliereAppartements2/AFRICA SURF HOUSE-photo1.jpg",
        "prix": "12 132 MAD / jours",
        "alt": "AFRICA SURF HOUSE-Taghzout",
        "localisation": "🌍 G7WQ+2FP, Taghazout",
        "description": "Appart. avec Wi-Fi gratuit, plage privée, 3 ch., cuisine, terrasse. Proche Plage Taghazout (500 m), Golf (4,4 km), parc aquatique (8,1 km), port & marina Agadir (18–19 km), aéroport (40 km)."
    },
    {
        "title": "Atlas Hostel Taghazout",
        "ville": "Taghazout",
        "type": "Maisons",
        "max_adultes": 6,
        "max_enfants": 3,
        "url": "/JournaliereMaisons2",
        "img": "/static/JournaliereMaisons2/Atlas Hostel Taghazout-photo1.jpg",
        "prix": "16 366 MAD / jours",
        "alt": "Atlas Hostel Taghazout",
        "localisation": "🌍 G7WQ+3Q6, Rue Iwlit, Taghazout 80000",
        "description": "Auberge avec terrasse, cuisine partagée, salon commun, Wi-Fi gratuit. Proche plage (400 m), golf (4,4 km), marina (19 km). Randonnée, bagagerie, navette aéroport (40 km)."
    },
    {
        "title": "Villa Belle Vue-Taghazout",
        "ville": "Taghazout",
        "type": "Villas",
        "max_adultes": 6,
        "max_enfants": 4,
        "url": "/JournaliereVillas2",
        "img": "/static/JournaliereVillas2/Villa Belle Vue-photo1.jpg",
        "prix": "65 716 MAD / jours",
        "alt": "Villa Belle Vue Taghazout",
        "localisation": "🌍 G7WR+4C, Taghazout",
        "description": "Villa 6 ch. à Taghazout avec piscine privée, jardin, terrasse. Clim., cuisine équipée, 6 sdb, Wi-Fi, TV. À 200 m de la plage, 5 km du golf, 20 km port d’Agadir, 42 km aéroport."
    },
    {
        "title": "The lodge Residence by Goodmove-Rabat",
        "ville": "Rabat",
        "type": "Appartements",
        "max_adultes": 5,
        "max_enfants": 1,
        "url": "/JournaliereAppartements3",
        "img": "/static/JournaliereAppartements3/The lodge Residence by Goodmove-photo1.jpg",
        "prix": "29 572 MAD / jours",
        "alt": "The lodge Residence by Goodmove-Rabat",
        "localisation": "🌍 6ème étage, Riad Andalous seville n°85, Rabat 10100",
        "description": "Appart. climatisé avec Wi-Fi gratuit, cuisine équipée, terrasse, parking privé. À 5,1 km du Golf royal, 10–11 km de la Bibliothèque nationale et Tour Hassan, 17 km de l’aéroport."
    },
    {
        "title": "Riad Dar El Mesk-Rabat",
        "ville": "Rabat",
        "type": "Maisons",
        "max_adultes": 4,
        "max_enfants": 4,
        "url": "/JournaliereMaisons3",
        "img": "/static/JournaliereMaisons3/Riad Dar El Mesk-photo1.jpg",
        "prix": "13 801 MAD / jours",
        "alt": "Riad Dar El Mesk-Rabat",
        "localisation": "🌍 n17 Impasse El Kalkhe, Av. Mohammed V, Rabat 10030",
        "description": "Maison d’hôtes avec terrasse, patio, salon commun, Wi-Fi gratuit. À 700 m de la plage, proche Tour Hassan, Kasbah des Oudayas. À 2,2 km de la Bibliothèque nationale, 3,9 km de la Marina. Navette aéroport (10 km)."
    },
    {
        "title": "Villa élégante-Rabat",
        "ville": "Rabat",
        "type": "Villas",
        "max_adultes": 4,
        "max_enfants": 4,
        "url": "/JournaliereVillas3",
        "img": "/static/JournaliereVillas3/Villa élégante-photo1.jpg",
        "prix": "28 094 MAD / jours",
        "alt": "Villa élégante-Rabat",
        "localisation": "🌍 12040, 249 R322, Temara",
        "description": "Villa 4 ch. à Harhoura avec jardin, plage privée, terrasse. Clim., cuisine équipée, 4 sdb, Wi-Fi, TV. À 2,3 km de la plage la Falaise, 12 km du golf, 14 km bibliothèque, 24 km aéroport."
    }

]



@application.route("/locations/longue-duree", methods=["GET"])
def locations_longue_duree():
    ville = request.args.get("ville")
    adultes = request.args.get("adultes")
    enfants = request.args.get("enfants")
    date_depart = request.args.get("date_depart")
    date_retour = request.args.get("date_retour")

    today = datetime.today().strftime('%Y-%m-%d')
    months_difference = None

    # Safely convert values
    try:
        adultes = int(adultes) if adultes else 0
        enfants = int(enfants) if enfants else 0
    except ValueError:
        adultes = 0
        enfants = 0

    # Calculate duration in months
    if date_depart and date_retour:
        try:
            d1 = datetime.strptime(date_depart, "%Y-%m-%d")
            d2 = datetime.strptime(date_retour, "%Y-%m-%d")

            # Calculate full months between the two dates
            months_difference = (d2.year - d1.year) * 12 + (d2.month - d1.month)

            # If the end day is greater than or equal to start day, count it as a full month
            if d2.day >= d1.day:
                months_difference += 1
        except ValueError:
            months_difference = None

    # Filter matching properties
    matching_cards = [
        prop for prop in LONG_TERM_PROPERTIES
        if (not ville or prop["ville"] == ville)
        and prop.get("max_adultes", 0) >= adultes
        and prop.get("max_enfants", 0) >= enfants
    ]

    return render_template(
        "locations longue duree.html",
        ville=ville,
        adultes=adultes,
        enfants=enfants,
        date_depart=date_depart,
        date_retour=date_retour,
        months=months_difference,
        today=today,
        cards=matching_cards
    )




LONG_TERM_PROPERTIES = [
  {
    "title": "Appartement 2 chambre proche Medina-Marrakech",
    "ville": "Marrakech",
    "type": "Appartements",
    "max_adultes": 4,
    "max_enfants": 2,
    "url": "/longuedureeAppartements1",
    "img": "/static/longue-dureeAppartements1/appartement 2 chambre proche Medina-photo1.jpg",
    "prix": "17 370 MAD / moins",
    "alt": "Appartement 2 chambre proche Medina",
    "localisation": "🌍 Mabrouka hiba M2 APT 1 RDC MARRAKECH, 40000",
    "description": "Appart. 2 ch. avec clim, Wi-Fi gratuit, balcon, terrasse, parking. À 4–7 km de musées, gare, Médina. Aéroport à 7 km."
  },
  {
    "title": "Riad Malayine-Marrakech",
    "ville": "Marrakech",
    "type": "Maisons",
    "max_adultes": 5,
    "max_enfants": 3,
    "url": "/longuedureeMaisons1",
    "img": "/static/longue-dureeMaisons1/Riad Malayine-photo1.jpg",
    "prix": "350 090 MAD / moins",
    "alt": "Riad Malayine",
    "localisation": "🌍 53 Av. Imam El Ghazali, Marrakech 40000",
    "description": "Riad Malayine en centre-ville avec clim., Wi-Fi, salon commun, terrasse, restaurant, excursions. Proche sites touristiques, aéroport à 6 km."
  },
  {
    "title": "Villa Marrakech",
    "ville": "Marrakech",
    "type": "Villas",
    "max_adultes": 6,
    "max_enfants": 4,
    "url": "/longuedureeVillas1",
    "img": "/static/longue-dureeVillas1/Villa Marrakech-photo1.jpg",
    "prix": "83 409 MAD / moins",
    "alt": "Villa Marrakech",
    "localisation": "🌍 MXHR+JWG, Residence Talmoulkt, Casablanca Rd, Marrakesh 40000",
    "description": "Villa haut standing avec piscine, terrasse vue montagne, cuisine équipée, clim., Wi-Fi. À proximité de lieux culturels et aéroport (9 km)."
  },
  {
    "title": "Ourlfa apartment-Casablanca",
    "ville": "Casablanca",
    "type": "Appartements",
    "max_adultes": 2,
    "max_enfants": 1,
    "url": "/longuedureeAppartements2",
    "img": "/static/longue-dureeAppartements2/Ourlfa apartment-photo1.jpg",
    "prix": "53 567 MAD / moins",
    "alt": "Ourlfa apartment",
    "localisation": "🌍 Oulfa, Casablanca",
    "description": "Appart. 1 ch. avec balcon, cuisine, salon, Wi-Fi, parking. À 5–8 km du Morocco Mall, Anfa Place, Mosquée Hassan II, 23 km aéroport."
  },
  {
    "title": "Diamond House",
    "ville": "Casablanca",
    "type": "Maisons",
    "max_adultes": 5,
    "max_enfants": 4,
    "url": "/longuedureeMaisons2",
    "img": "/static/longue-dureeMaisons2/Diamond House-photo1.jpg",
    "prix": "12 942 MAD / moins",
    "alt": "Diamond House",
    "localisation": "🌍 Casablanca beausejour, Hay Hassani, 20200 Casablanca, Maroc",
    "description": "Maison avec jacuzzi, balcon, terrasse, cuisine équipée, Wi-Fi, parking. À 4–7 km de sites touristiques, 25 km aéroport."
  },
  {
    "title": "Nassali Villa-Casablanca",
    "ville": "Casablanca",
    "type": "Villas",
    "max_adultes": 6,
    "max_enfants": 1,
    "url": "/longuedureeVillas2",
    "img": "/static/longue-dureeVillas2/Nassali-photo1.jpg",
    "prix": "65 716 MAD / moins",
    "alt": "Nassali Villa",
    "localisation": "🌍 F4Q2+3W5, Route d'Ourik",
    "description": "Villa 4 ch. avec piscine privée, jardin, terrasse, balcon, clim., Wi-Fi, TV. Proche plage Aïn Diab (1,8 km), 25 km aéroport."
  },
  {
    "title": "Appartement charmant, 2Terrasses-Essaouira",
    "ville": "Essaouira",
    "type": "Appartements",
    "max_adultes": 3,
    "max_enfants": 3,
    "url": "/longuedureeAppartements3",
    "img": "/static/longue-dureeAppartements3/Appartement charmant, 2Terrasses-photo1.jpg",
    "prix": "10 500 MAD / moins",
    "alt": "Appartement charmant",
    "localisation": "🌍 4 Rue Abdellah Chefchaouni, Essaouira 44000",
    "description": "Appart. 3 ch. avec 2 terrasses, vue sur ville, cuisine, Wi-Fi, TV. À 1,3 km plage, 6,1 km golf, 17 km aéroport."
  },
  {
    "title": "Dar Essaada-Essaouira",
    "ville": "Essaouira",
    "type": "Maisons",
    "max_adultes": 4,
    "max_enfants": 4,
    "url": "/longuedureeMaisons3",
    "img": "/static/longue-dureeMaisons3/Dar Essaada-photo1.jpg",
    "prix": "13 801 MAD / moins",
    "alt": "Dar Essaada-Essaouira",
    "localisation": "🌍 Essaouira",
    "description": "Maison d’hôtes avec piscine, hammam, Wi‑Fi. Excursions sur demande. À 12 km d’Essaouira, 20 min de Sidi Kaouki."
  },
  {
    "title": "Family Villa Soleil Essaouira",
    "ville": "Essaouira",
    "type": "Villas",
    "max_adultes": 2,
    "max_enfants": 4,
    "url": "/longuedureeVillas3",
    "img": "/static/longue-dureeVillas3/Family Villa Soleil-photo1.jpg",
    "prix": "20 526 MAD / moins",
    "alt": "Family Villa Soleil",
    "localisation": "🌍 Centre، Hotel Villa Soleil, Sidi Kaouki 44000",
    "description": "Villa familiale avec terrasse, balcon, Wi‑Fi gratuit. À 700 m plage, 3,1 km golf, 14 km aéroport."
  }
]


# ------------------------



if __name__ == '__main__':
    application.run(debug=True)



# The important part for PythonAnywhere:
application = application

