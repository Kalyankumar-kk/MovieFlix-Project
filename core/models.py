from django.db import models

# Create your models here.
class Language(models.Model):
    # This stores the name of the language (e.g., "English", "Hindi")
    language_name = models.CharField(max_length=100)
    # Automatically adds the date when the language was entered
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.language_name # Fixes "Language object (1)"

class Genre(models.Model):
    category_name = models.CharField(max_length=100)
    genre_name = models.CharField(max_length=100)

    def __str__(self):
        return self.genre_name # Fixes "Genre object (12)"
    

class Movie(models.Model):
    movie_title = models.CharField(max_length=255)
    movie_director = models.CharField(max_length=255)
    movie_release_date = models.DateField()
    # Relationship to your other models
    movie_language = models.ForeignKey('Language', on_delete=models.CASCADE)
    movie_genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    
    # Fields stored in DB but hidden from your main 7-column list
    movie_banner = models.ImageField(upload_to='movie_banners/')
    movie_duration = models.CharField(max_length=50)
    movie_description = models.TextField()
    movie_video_url = models.URLField()


    @property
    def get_embed_url(self):
        url = self.movie_video_url
        if "watch?v=" in url:
            # Splits by the video ID and ignores extra parameters like &t= or &list=
            video_id = url.split("watch?v=")[1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return url


class WebSeries(models.Model):
    series_title = models.CharField(max_length=255)
    series_director = models.CharField(max_length=255, default="Unknown")
    series_language = models.ForeignKey('Language', on_delete=models.CASCADE, null=True)
    series_genre = models.ForeignKey('Genre', on_delete=models.CASCADE, null=True)
    series_banner = models.ImageField(upload_to='webseries_banners/')
    total_seasons = models.IntegerField(default=1)
    release_date = models.DateField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    # FIX: Update this to use the Season relationship
    def get_episodes_count(self):
        counts = []
        # Loop through the seasons defined for this series
        for sn in self.seasons_list.all().order_by('season_order'):
            count = Episode.objects.filter(season=sn).count()
            counts.append(f"{sn.season_name}: {count} Episodes")
        return counts
    
    def total_seasons_range(self):
        return range(1, self.total_seasons + 1)


class Season(models.Model):
    series = models.ForeignKey(WebSeries, on_delete=models.CASCADE, related_name='seasons_list')
    season_name = models.CharField(max_length=100)
    season_order = models.IntegerField()
    # ADD THESE TWO FIELDS
    season_release_date = models.DateField(null=True, blank=True)
    season_description = models.TextField(null=True, blank=True)
    season_banner = models.ImageField(upload_to='season_banners/', null=True, blank=True)

    class Meta:
        ordering = ['season_order']

class Episode(models.Model):
    series = models.ForeignKey(WebSeries, on_delete=models.CASCADE, related_name='episodes')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_episodes', null=True)
    episode_title = models.CharField(max_length=255)
    video_url = models.URLField()

    episode_number = models.PositiveIntegerField(default=1)
    # ADD THESE TWO FIELDS
    episode_release_date = models.DateField(null=True, blank=True)
    episode_banner = models.ImageField(upload_to='episode_banners/', null=True, blank=True)

    episode_description = models.TextField(null=True, blank=True)
    episode_duration = models.CharField(max_length=50, null=True, blank=True) # e.g., "45 mins"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['episode_number']
    

    @property
    def get_embed_url(self):
        """Converts standard YouTube links to embed format for iFrames"""
        # FIX: Change 'self.episode_video_url' to 'self.video_url'
        url = self.video_url 
        if not url:
            return ""
        if "youtube.com/watch?v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif "youtu.be/" in url:
            video_id = url.split("/")[-1]
            return f"https://www.youtube.com/embed/{video_id}"
        return url


class Notification(models.Model):
    recipient_username = models.CharField(max_length=100)
    user_role = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    redirect_url = models.URLField(max_length=500, null=True, blank=True) 
    image = models.ImageField(upload_to='notification_banners/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


# core/models.py
class WatchHistory(models.Model):
    customer_username = models.CharField(max_length=100)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
    web_series = models.ForeignKey(WebSeries, on_delete=models.CASCADE, null=True, blank=True)
    # ADD THIS FIELD:
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, null=True, blank=True)
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-watched_at']
    

# core/models.py or wherever your other models are
class LikedVideo(models.Model):
    customer_username = models.CharField(max_length=100)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
    web_series = models.ForeignKey(WebSeries, on_delete=models.CASCADE, null=True, blank=True)
    # ADD THIS NEW FIELD
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True, blank=True)
    
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, null=True, blank=True)
    liked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Updated constraint to handle all three levels
        unique_together = ('customer_username', 'movie', 'web_series', 'season', 'episode')
        ordering = ['-liked_at']
