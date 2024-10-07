import requests
from django.conf import settings


def get_disqus_stats(post_id):
    # Datos de configuración
    api_key = settings.DISQUS_API_KEY
    forum = settings.DISQUS_FORUM

    # URL de la API para obtener los comentarios
    url = f"https://disqus.com/api/3.0/threads/details.json"
    params = {
        "api_key": api_key,
        "forum": forum,
        "thread:ident": f"/posts/{post_id}/",
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        response = data["response"]

        likes = response["likes"]
        dislikes = response["dislikes"]
        comments = response["posts"]

        return {"comments": comments, "likes": likes, "dislikes": dislikes}
    else:
        print(f"Cannot get disqus statistics: {response.content}")
        return {"comments": 0, "likes": 0, "dislikes": 0}
