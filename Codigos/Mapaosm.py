import osmnx as ox

places = [
    "Monterrey, Nuevo Leon, Mexico",
    "San Nicolas de los Garza, Nuevo Leon, Mexico",
    "Guadalupe, Nuevo Leon, Mexico",
    "Apodaca, Nuevo Leon, Mexico",
    "General Escobedo, Nuevo Leon, Mexico",
    "Garcia, Nuevo Leon, Mexico",
    "Juarez, Nuevo Leon, Mexico",
    "Santa Catarina, Nuevo Leon, Mexico",
    "Santiago, Nuevo Leon, Mexico",
    "San Pedro Garza Garcia, Nuevo Leon, Mexico"
]

G = ox.graph_from_place(
    places,
    network_type="drive"
)
ox.save_graphml(G, "mty_metropolitana.graphml")
print(G)