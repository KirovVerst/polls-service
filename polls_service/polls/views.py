from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Choice
from .models import Question
from .services import VoteService


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, pk):
    service = VoteService(request.user)
    question = get_object_or_404(Question, pk=pk)

    try:
        service.vote(question, request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render_choice_not_selected_view(request, question)

    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def render_choice_not_selected_view(request, question: Question):
    return render(request, "polls/detail.html", {"question": question, "error_message": "You didn't select a choice."})
