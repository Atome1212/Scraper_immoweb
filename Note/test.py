property_example = {
    "Locality": "Brussels",
    "Type of property": "House",
    "Subtype of property": "Mansion",
    "Price": 1200000,
    "Type of sale": "Normal sale",
    "Number of rooms": 8,
    "Living Area (m²)": 350,
    "Fully equipped kitchen": True,
    "Furnished": False,
    "Open fire": True,
    "Terrace": {
        "Present": True,
        "Area (m²)": 30
    },
    "Garden": {
        "Present": True,
        "Area (m²)": 100
    },
    "Surface of the plot (m²)": 500,
    "Number of facades": 4,
    "Swimming pool": False,
    "State of the building": "New"
}

id_page = 1
link_page = f"https://www.immoweb.be/fr/recherche/maison/a-vendre?countries=BE&page={id_page}&orderBy=relevance"

(a) #card__title-link
link_house = "https://www.immoweb.be/fr/annonce/maison/a-vendre/nassogne/6950/11485698"

#Locality
(span) #classified__information--address-row
regex remove le span dedant
regex => avant et apres le -
locality = ["cp", "locality"] ou alors juste la locality

#Type of property

we have alle the list in filtre (help for regex)

#Subtype of property
(h1) classified__title regex to know what type of build is

we have alle the list in filtre (help for regex) but is under the first

#Price
(p) #classified__price => (span) sr-only
price:int = 

#Type of sale

## we need do find all information in that list
#Number of rooms
classified-table__row (ensemble of all information)

#Living Area (m²)
classified-table__row (ensemble of all information)

#Fully equipped kitchen
classified-table__row (ensemble of all information)

#Furnished
classified-table__row (ensemble of all information)

#Open fire
classified-table__row (ensemble of all information)

#Terrace
classified-table__row (ensemble of all information)

#Garden
classified-table__row (ensemble of all information)

#Surface of the plot (m²)":
classified-table__row (ensemble of all information)

#Number of facades
classified-table__row (ensemble of all information)

#Swimming pool
classified-table__row (ensemble of all information)

#State of the buildin

#Type of property #Subtype of property

#faire un filtre que s'adapte a chaque redemarage afain de metre a jour tout les filtres existant

dico { 

"Type of property" : [Subtype of property],

}

after stock in json

#rensaigner le nombre de maison que l'on veux 

puis link_page => get all link link_house

parcourir tout ces link (comme ca c est page par page)

for i in get all link link_house
    make all manipulation before

les stocker petit a petit pour que la ram ne sature pas 

multi thread + vpn actif

