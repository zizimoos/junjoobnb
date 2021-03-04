# from django.shortcuts import render, redirect
# from django.core.paginator import Paginator, EmptyPage
from django.views.generic import ListView, DetailView

# from django.http import Http404
from django_countries import countries
from django.utils import timezone
from django.shortcuts import render
from . import models


# from django.http import HttpResponse
class HomeView(ListView):

    """ HomeView Definition """

    model = models.Room
    paginate_by = 10
    paginate_orphans = 5
    ordering = "created"
    context_object_name = "rooms"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["now"] = now
        return context


# def room_detail(request, pk):
#     try:
#         room = models.Room.objects.get(pk=pk)
#         return render(request, "rooms/detail.html", {"room": room})
#     except models.Room.DoesNotExist:
#         # return redirect(reverse("core:home"))
#         raise Http404()


class RoomDetail(DetailView):

    """ RoomDetail Definition """

    model = models.Room


def search(request):
    print(request.GET)
    city = request.GET.get("city", "anywhere")
    city = str.capitalize(city)
    room_types = models.RoomType.objects.all()
    return render(
        request,
        "rooms/search.html",
        {"city": city, "countries": countries, "room_types": room_types},
    )
