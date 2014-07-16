from django.shortcuts import render

# Create your views here.
def start_page(request, template='entry_page.html'):
    context = {'domain': get_domain(8000), 'domain8010': get_domain()}
    return render_to_response(template, RequestContext(request, context))
