from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreateionForm


class SignUp(CreateView):
    form_class = CreateionForm
    success_url = reverse_lazy('post:index')
    template_name = 'users/signup.html'
