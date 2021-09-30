from django.shortcuts import render
from django.views.generic import ListView, DetailView
from portfolio.models import Portfolio
# Create your views here.
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from mysite.views import OwnerOnlyMixin


class PortfolioLV(ListView):
    model = Portfolio

class PortfolioDV(DetailView):
    model = Portfolio

# class-based views
class PortfolioCreateView(LoginRequiredMixin, CreateView):
    model = Portfolio
    fields = ['title', 'url', 'description']
    success_url = reverse_lazy('portfolio:index')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class PortfolioChangeLV(LoginRequiredMixin, ListView):
    template_name = 'portfolio/portfolio_change_list.html'

    def get_queryset(self):
        return Portfolio.objects.filter(owner=self.request.user)



class PortfolioUpdateView(OwnerOnlyMixin, UpdateView):
    model = Portfolio
    fields = ['title', 'url']
    success_url = reverse_lazy('portfolio:index')

class PortfolioDeleteView(OwnerOnlyMixin, DeleteView):
    model = Portfolio
    success_url = reverse_lazy('portfolio:index')