import os
from dotenv import load_dotenv

load_dotenv()

PELICULAS_EJEMPLO = [
  { "id": 1, "api_id": "tt0095327", "titulo": "Cinema Paradiso", "sinopsis": "Salvatore, un aclamado cineasta, regresa a su pueblo...", "poster_url": "https://m.media-amazon.com/images/M/MV5BYmI5ZDY5ZDQtYmMyZS00NjU4LTg5NzgtZWMxYjFkMzQzZThiXkEyXkFqcGc@._V1_.jpg", "duracion_minutos": 155, "clasificacion": "ATP", "genero": "Drama", "director": "Giuseppe Tornatore", "es_reestreno": True },
  { "id": 2, "api_id": "tt0110912", "titulo": "Pulp Fiction", "sinopsis": "Las vidas de dos asesinos a sueldo, la esposa de un gánster...", "poster_url": "https://es.web.img3.acsta.net/img/05/66/05663f00b8b5df58b003aaf5c46ef8ad.jpg", "duracion_minutos": 154, "clasificacion": "+18", "genero": "Crimen / Drama", "director": "Quentin Tarantino", "es_reestreno": True },
  { "id": 3, "api_id": "tt0088763", "titulo": "Volver al Futuro", "sinopsis": "Marty McFly, un adolescente de 17 años, es enviado...", "poster_url": "https://m.media-amazon.com/images/M/MV5BZmM3ZjE0NzctNjBiOC00MDZmLTgzMTUtNGVlOWFlOTNiZDJiXkEyXkFqcGc@._V1_.jpg", "duracion_minutos": 116, "clasificacion": "ATP", "genero": "Ciencia Ficción / Aventura", "director": "Robert Zemeckis", "es_reestreno": True }
]