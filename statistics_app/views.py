from django.shortcuts import render

def statistics_view(request):
    return render(request, "statistics_app/statistics.html")

def error_stats(request):
    return render(request, "statistics_app/error_stats.html")