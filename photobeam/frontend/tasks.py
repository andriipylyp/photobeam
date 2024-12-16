from datetime import timedelta
from celery import shared_task
from django.utils.timezone import now
from frontend.models import Album

@shared_task
def delete_old_albums():
    try:
        threshold_date = now() - timedelta(days=7)
        old_albums = Album.objects.filter(event_date__lte=threshold_date)
        count = old_albums.count()
        old_albums.delete()
        return f"Deleted {count} albums."
    except Exception as e:
        return f"Task failed: {str(e)}"