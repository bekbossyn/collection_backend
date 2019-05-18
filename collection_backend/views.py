from django.shortcuts import render


# Create your views here.
def test_collection(request):
    return render(request, "test/test_collection.html", {})


