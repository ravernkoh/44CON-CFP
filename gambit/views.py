from django.views import generic


class ErrorView(generic.TemplateView):
    template_name = 'obscurus/error.html'

    def __init__(self):
        self.error_value = 0
        self.error_type = 'Error'

    def get_context_data(self, **kwargs):
        context = super(ErrorView, self).get_context_data(**kwargs)
        context['error_value'] = "{0!s}".format(self.error_value)
        context['error_type'] = self.error_type
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super(ErrorView, self).render_to_response(context, **response_kwargs)
        response.status_code = self.error_value
        return response


class BadRequestView(ErrorView):
    def __init__(self):
        self.error_value = 400
        self.error_type = 'Bad Request'


class PermissionDeniedView(ErrorView):
    def __init__(self):
        self.error_value = 403
        self.error_type = 'Permission Denied'


class PageNotFoundView(ErrorView):
    def __init__(self):
        self.error_value = 404
        self.error_type = 'Page Not Found'


class ServerErrorView(ErrorView):
    def __init__(self):
        self.error_value = 500
        self.error_type = 'Server Error'
