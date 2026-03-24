def category_ranges():
    return {
        "Matemática y razonamiento": (1, 30),
        "Aptitud verbal": (31, 50),
        "Antónimos, sinónimos y analogías": (51, 65),
        "Comprensión lectora": (66, 80),
        "Prueba pedagógica": (81, 100),
    }


def youtube_embed_url(url):
    if not url:
        return None

    url = url.strip()

    if "youtube.com/watch?v=" in url:
        video_id = url.split("watch?v=")[-1].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"

    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[-1].split("?")[0].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"

    if "youtube.com/embed/" in url:
        return url

    return url