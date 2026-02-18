from django.contrib import admin
from .models import Language, Genre, Movie, WebSeries, Season, Episode, Notification, WatchHistory, LikedVideo

# Register Language
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'language_name', 'created_at']
    search_fields = ['language_name']
    list_per_page = 20

# Register Genre
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_name', 'genre_name']
    search_fields = ['category_name', 'genre_name']
    list_filter = ['category_name']
    list_per_page = 20

# Register Movie
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['id', 'movie_title', 'movie_director', 'movie_release_date', 'movie_language', 'movie_genre', 'movie_duration']
    search_fields = ['movie_title', 'movie_director']
    list_filter = ['movie_language', 'movie_genre', 'movie_release_date']
    list_per_page = 20
    date_hierarchy = 'movie_release_date'

# Register WebSeries
@admin.register(WebSeries)
class WebSeriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'series_title', 'series_director', 'series_language', 'series_genre', 'total_seasons', 'release_date']
    search_fields = ['series_title', 'series_director']
    list_filter = ['series_language', 'series_genre', 'release_date']
    list_per_page = 20
    date_hierarchy = 'release_date'

# Register Season
@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['id', 'season_name', 'series', 'season_order', 'season_release_date']
    search_fields = ['season_name', 'series__series_title']
    list_filter = ['series', 'season_release_date']
    ordering = ['series', 'season_order']
    list_per_page = 20

# Register Episode
@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'episode_title', 'series', 'season', 'episode_number', 'episode_duration', 'episode_release_date']
    search_fields = ['episode_title', 'series__series_title']
    list_filter = ['series', 'season', 'episode_release_date']
    ordering = ['series', 'season', 'episode_number']
    list_per_page = 20

# Register Notification
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'recipient_username', 'user_role', 'is_read', 'created_at']
    search_fields = ['title', 'recipient_username', 'message']
    list_filter = ['user_role', 'is_read', 'created_at']
    date_hierarchy = 'created_at'
    list_per_page = 20

# Register WatchHistory
@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_username', 'content_type', 'content_title', 'watched_at']
    search_fields = ['customer_username']
    list_filter = ['watched_at']
    date_hierarchy = 'watched_at'
    list_per_page = 20
    
    def content_type(self, obj):
        """Shows whether it's a Movie or Episode"""
        if obj.movie:
            return "Movie"
        elif obj.episode:
            return "Episode"
        return "Unknown"
    content_type.short_description = 'Content Type'
    
    def content_title(self, obj):
        """Shows the title of what was watched"""
        if obj.movie:
            return obj.movie.movie_title
        elif obj.episode:
            return f"{obj.webseries.series_title} - {obj.episode.episode_title}"
        return "N/A"
    content_title.short_description = 'Title'

# Register LikedVideo
@admin.register(LikedVideo)
class LikedVideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_username', 'content_type', 'content_title', 'liked_at']
    search_fields = ['customer_username']
    list_filter = ['liked_at']
    date_hierarchy = 'liked_at'
    list_per_page = 20
    
    def content_type(self, obj):
        """Shows whether it's a Movie or Episode"""
        if obj.movie:
            return "Movie"
        elif obj.episode:
            return "Episode"
        return "Unknown"
    content_type.short_description = 'Content Type'
    
    def content_title(self, obj):
        """Shows the title of what was liked"""
        if obj.movie:
            return obj.movie.movie_title
        elif obj.episode:
            return f"{obj.webseries.series_title} - {obj.episode.episode_title}"
        return "N/A"
    content_title.short_description = 'Title'
