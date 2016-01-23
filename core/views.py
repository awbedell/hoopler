from django.shortcuts import render
from django.views.generic import (
    View, TemplateView, ListView, DetailView, FormView, UpdateView
)
from models import *

class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

class RosterView(TemplateView):
    template_name = 'core/roster.html'

    def get_context_data(self, **kwargs):
        context = super(RosterView, self).get_context_data(**kwargs)
        context['periods'] = self.request.user.instructor.period_set.all()
        return context
