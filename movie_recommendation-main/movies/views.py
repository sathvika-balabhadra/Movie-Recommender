from django.shortcuts import render, redirect
from django.views import generic, View
from movies.models import Movie, Genre, MyList, WatchHistory, Like, View as ViewModel
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
import json
from datetime import timedelta
from django.utils import timezone
from django.db.models import F, Count, Q, FloatField, ExpressionWrapper
import re
from movies.recommendation import get_similar_recommendation

class WatchView(LoginRequiredMixin, generic.DetailView):
    model = Movie
    template_name = "movies/watch.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["similar_movies"] = get_similar_recommendation(context["movie"].title, num_recommendations=7)

        context["like"] = False
        context["my_list"] = False
        if Like.objects.filter(user=self.request.user, movie=context["movie"]):
            context['like']=True
        if MyList.objects.filter(user=self.request.user, movie=context["movie"]):
            context['my_list']=True

        return context

class PopularMoviesView(generic.ListView):
    model = Movie
    template_name = "movies/movie_list.html"

    def get_queryset(self):
        last_7_days = timezone.now() - timedelta(days=7)

        qs = Movie.objects.prefetch_related("genres", "language").annotate(
            recent_likes=Count("likes", filter=Q(likes__created_at__gte=last_7_days)),
            recent_views=Count("views", filter=Q(views__created_at__gte=last_7_days))
        ).annotate(
            popularity=ExpressionWrapper(
                F("recent_likes") / (F("recent_views") + 1.0),
                output_field=FloatField()
            )
        )
        qs = qs.filter(popularity__gt=0).order_by("-popularity", "-recent_likes", "-recent_views", "-pk")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Popular Movies"
        return context

class MovieGenreView(generic.ListView):
    model = Genre
    queryset = Genre.objects.all().order_by("name")
    template_name = "movies/movie_genre_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["genre_list"] = [movie for movie in context["genre_list"] if movie.total_movies > 0]
        return context

class MovieByGenreView(generic.ListView):
    model = Movie
    template_name = "movies/movie_list.html"

    def get_queryset(self):
        self.genre = Genre.objects.get(pk=self.kwargs['pk'])
        return Movie.objects.filter(genres=self.genre).order_by("-pk")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"{self.genre.name} Movies"
        return context

class NewMovieListView(generic.ListView):
    model = Movie
    template_name = "movies/movie_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return  qs.prefetch_related("language", "genres").order_by("-created_at")[:14]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "New Releases"
        return context

class MyListMovieListView(LoginRequiredMixin, generic.ListView):
    model = MyList
    template_name = "movies/movie_list.html"

    def get_queryset(self):
        qs =  super().get_queryset()
        qs = qs.filter(user=self.request.user).order_by("-created_at")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "My List"
        context["movie_list"] = [mylist.movie for mylist in context["mylist_list"]]
        return context

class WatchHistoryMovieListView(LoginRequiredMixin, generic.ListView):
    model = WatchHistory
    template_name = "movies/movie_list.html"
    
    def get_queryset(self):
        qs =  super().get_queryset()
        qs = qs.filter(user=self.request.user).order_by("-created_at")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Watch History"
        context["movie_list"] = [mylist.movie for mylist in context["object_list"]]
        return context

class MovieListView(generic.ListView):
    model = Movie
    template_name = "movies/movie_list.html"

    def get_queryset(self):
        self.q = self.request.GET.get("search", "").strip()
        qs = super().get_queryset()
        qs = qs.prefetch_related("language", "genres")
        if self.q:
            # Tokenize and normalize the query
            tokens = re.findall(r'\w+', self.q.lower())
            
            # Build the search query
            search_filter = Q()
            for token in tokens:
                search_filter |= (
                    Q(title__icontains=token) |
                    Q(language__name__icontains=token) | 
                    Q(genres__name__icontains=token)
                )
            return qs.filter(search_filter).distinct()
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.q:
            context["title"] = f"Search: {self.q}"
        else:
            context["title"] = "Movies"
        return context
    
class LikeMovie(View):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        try:
            data = json.loads(request.body)
            id = data["id"]
            if not isinstance(id, int):
                return JsonResponse({"error": "Invalid id"}, status=400)
            try:
                movie = Movie.objects.get(pk=id)
            except Movie.DoesNotExist:
                return JsonResponse({"error": "Movie not found"}, status=404)
            history = WatchHistory.objects.filter(user=user, movie=movie).first()
            if history:
                like, created = Like.objects.get_or_create(user=user, movie=movie)
                if not created:
                    Movie.objects.filter(pk=like.movie.id).update(total_likes=F('total_likes') - 1)
                    like.delete()
                    return JsonResponse({"status": False, "id": id})
                else:
                    return JsonResponse({"status": True, "id": id})
            else:
                return JsonResponse({"error": "Movie has not been watched."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid data"}, status=400)


class UpdateHistory(View):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        try:
            data = json.loads(request.body)
            id = data["id"]
            print(id)
            if not isinstance(id, int):
                return JsonResponse({"error": "Invalid id"}, status=400)
            try:
                movie = Movie.objects.get(pk=id)
            except Movie.DoesNotExist:
                return JsonResponse({"error": "Movie not found"}, status=404)
            ip = request.META.get("REMOTE_ADDR")
            watch = WatchHistory.objects.filter(user=user, movie=movie).last()
            view = ViewModel.objects.filter(user=user, movie=movie).last()
            if not view:
                ViewModel.objects.create(user=user, movie=movie, user_ip=ip)
                WatchHistory.objects.create(user=user, movie=movie)
            else:
                if view.created_at <= timezone.now() - timedelta(days=1):
                    ViewModel.objects.create(user=user, movie=movie, user_ip=ip)
                    watch.objects.create(user=user, movie=movie)
            return JsonResponse({"status": True, "id": id})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid data"}, status=400)
  
class ToggleMyListView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        try:
            data = json.loads(request.body)
            id = data["id"]
            if not isinstance(id, int):
                return JsonResponse({"error": "Invalid movie ID"}, status=400)
            try:
                movie = Movie.objects.get(pk=id)
            except Movie.DoesNotExist:
                return JsonResponse({"error": "Movie not found"}, status=404)
            my_list, created = MyList.objects.get_or_create(user=user, movie=movie)
            if not created:
                my_list.delete()
                return JsonResponse({"status": False, "id": id})
            else:
                return JsonResponse({"status": True, "id": id})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid data"}, status=400)