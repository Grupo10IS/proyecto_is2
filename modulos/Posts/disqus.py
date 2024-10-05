from disqusapi import DisqusAPI
from django.conf import settings


def get_disqus_stats():
    disqus = DisqusAPI(settings.DISQUS_SECRET_KEY, settings.DISQUS_PUBLIC_KEY)

    # Obtenemos los datos del post específico
    forum = "tu_forum_id"  # Reemplaza con el ID de tu foro en Disqus
    thread_id = "tu_thread_id"  # Reemplaza con el ID del hilo de comentarios

    stats = disqus.get("threads.details", forum=forum, thread=thread_id)

    # Extraemos las estadísticas
    total_comments = stats["total_replies"]
    likes = stats["likes_count"]
    dislikes = stats["dislikes_count"]

    return {"total_comments": total_comments, "likes": likes, "dislikes": dislikes}
