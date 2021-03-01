from math import ceil
from django.shortcuts import render
from django.core.paginator import Paginator
from . import models

# from django.http import HttpResponse


# Create your views here.
def all_rooms(request):
    page = request.GET.get("page")
    room_list = models.Room.objects.all()
    paginator = Paginator(room_list, 10)
    rooms = paginator.get_page(page)
    # page = int(page or 1)
    # page_size = 10
    # limit = page_size * page
    # offset = limit - page_size
    # all_rooms = models.Room.objects.all()[offset:limit]
    # page_count = models.Room.objects.count() / page_size

    return render(
        request,
        "rooms/all_rooms.html",
        # context={
        #     "rooms": all_rooms,
        #     "page": page,
        #     "page_count": ceil(page_count),
        #     "page_range": range(1, ceil(page_count)),
        # },
        {"rooms": rooms},
    )
