import datetime
from django import template
from reservations import models as reservation_models

register = template.Library()


@register.simple_tag(takes_context=True)
def is_booked(context, room, day):
    if day.number == 0:
        return
    try:
        date = datetime.datetime(year=day.year, month=day.month, day=day.number)
        reservation_models.BookedDay.objects.get(day=date, reservation__room=room)
        return True
    except reservation_models.BookedDay.DoesNotExist:
        return False
