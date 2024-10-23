from collections import defaultdict
from datetime import datetime

import requests
from django.conf import settings


def get_disqus_stats(post_id):
    # Datos de configuración
    api_key = settings.DISQUS_API_KEY
    forum = settings.DISQUS_FORUM

    # URL de la API para obtener los comentarios
    url = f"https://disqus.com/api/3.0/threads/listPosts.json"
    params = {
        "api_key": api_key,
        "forum": forum,
        "thread:ident": f"/posts/{post_id}/",
        "order": "asc",  # Para obtener en orden cronológico
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        response = data["response"]

        # Inicializamos contadores para likes, dislikes y un diccionario para comentarios por día
        likes = 0
        dislikes = 0
        comment_dates = defaultdict(
            int
        )  # Diccionario para contar comentarios por fecha

        # Procesar cada comentario individual
        for comment in response:
            # Contar comentarios por fecha
            comment_date = comment["createdAt"]  # Fecha del comentario
            date_obj = datetime.strptime(
                comment_date, "%Y-%m-%dT%H:%M:%S"
            )  # Convertir a datetime
            date_only = date_obj.strftime("%Y-%m-%d")  # Solo la fecha (sin tiempo)
            comment_dates[date_only] += 1

            # Sumar likes y dislikes (puedes ajustar según cómo quieras usarlos)
            likes += comment["likes"]
            dislikes += comment["dislikes"]

        # Calcular la cantidad total de comentarios
        total_comments = sum(comment_dates.values())

        # Regresar el conteo de comentarios por día, likes, dislikes y total de comentarios
        return {
            "comments_by_day": dict(comment_dates),
            "total_comments": total_comments,
            "likes": likes,
            "dislikes": dislikes,
        }
    else:
        print(f"Cannot get disqus statistics: {response.content}")
        return {"comments_by_day": {}, "total_comments": 0, "likes": 0, "dislikes": 0}
