from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView

from hypha.apply.users.decorators import staff_required
from hypha.apply.utils.views import DelegatedViewMixin

from .filters import NotificationFilter
from .forms import CommentForm
from .messaging import MESSAGES, messenger
from .models import COMMENT, Activity


class ActivityContextMixin:
    def get_context_data(self, **kwargs):
        related_query = self.model.activities.rel.related_query_name
        query = {related_query: self.object}
        extra = {
            # Do not prefetch on the related_object__author as the models
            # are not homogeneous and this will fail
            'actions': Activity.actions.filter(**query).select_related(
                'user',
            ).prefetch_related(
                'related_object',
            ).visible_to(self.request.user),
            'comments': Activity.comments.filter(**query).select_related(
                'user',
            ).prefetch_related(
                'related_object',
            ).visible_to(self.request.user),
        }
        return super().get_context_data(**extra, **kwargs)


class CommentFormView(DelegatedViewMixin, CreateView):
    form_class = CommentForm
    context_name = 'comment_form'

    def form_valid(self, form):
        source = self.kwargs['object']
        form.instance.user = self.request.user
        form.instance.source = source
        form.instance.type = COMMENT
        form.instance.timestamp = timezone.now()
        response = super().form_valid(form)
        messenger(
            MESSAGES.COMMENT,
            request=self.request,
            user=self.request.user,
            source=source,
            related=self.object,
        )
        return response

    def get_success_url(self):
        return self.object.source.get_absolute_url() + '#communications'

    def get_form_kwargs(self):
        # We dont want to pass the submission as the instance
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance')
        return kwargs


@method_decorator(staff_required, name='dispatch')
class NotificationsView(ListView):
    model = Activity
    template_name = 'activity/notifications.html'
    filterset_class = NotificationFilter

    def get_queryset(self):
        # List only last 30 days' activities
        queryset = Activity.objects.latest()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct().order_by('-timestamp')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(NotificationsView, self).get_context_data()
        context['filter'] = self.filterset
        return context
