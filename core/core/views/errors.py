from django.shortcuts import render


def error_400(request, exception):
    return render(
        request, "errors/400.html", {"exception": exception}, status=400
    )


def error_403(request, exception):
    return render(
        request, "errors/403.html", {"exception": exception}, status=403
    )


def error_404(request, exception):
    return render(
        request, "errors/404.html", {"exception": exception}, status=404
    )


def error_500(request):
    return render(request, "errors/500.html", status=500)
