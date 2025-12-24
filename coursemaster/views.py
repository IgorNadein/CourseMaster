from django.shortcuts import render


def home(request):
    """Landing page view"""
    context = {
        'total_students': 10000,
        'total_courses': 500,
        'total_instructors': 200,
    }
    return render(request, 'home.html', context)
