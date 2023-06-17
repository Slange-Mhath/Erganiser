from datetime import datetime


def current_month_year(request):
    return {
        "current_year": datetime.now().year,
        "current_month": datetime.now().month,
    }
