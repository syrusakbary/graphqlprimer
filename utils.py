from datetime import datetime
import pytz


def parse_datetime(value):
    return datetime.strptime(value, "%a %b %d %H:%M:%S +0000 %Y")
    # .astimezone(
    #     pytz.timezone("Europe/Madrid")
    # )
