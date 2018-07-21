from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from sample.forms import UploadFileForm
from fb2_converter import Fb2
from io import StringIO
from login_sample.settings import MEDIA_ROOT
from wsgiref.util import FileWrapper
import os
import mimetypes


class SignUpView(CreateView):
    template_name = 'sample/signup.html'
    form_class = UserCreationForm


def handle_uploaded_file(file, title):
    fil_of_file = None
    if file.name.endswith('.fb2'):
        text = StringIO('')
        for chunk in file.chunks():
            text.write(chunk.decode('utf-8'))
        text.seek(0)
        rd = Fb2(text, title)
        fil_of_file = rd.section()
    return fil_of_file


def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
        }
    return JsonResponse(data)


def get_file(request, title, name):
    the_file = os.path.join(MEDIA_ROOT, title, name)
    response = HttpResponse(
        FileWrapper(open(the_file, encoding='utf-8')),
        content_type=mimetypes.guess_type(the_file)[0]
    )
    response['Content-Disposition'] = 'attachment; filename={0}'.format(name)
    response['Content-Length'] = os.path.getsize(the_file)
    return response


def upload_file(request):
    context_dict = {}
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            sections = handle_uploaded_file(request.FILES['file'], form.cleaned_data['title'])
            context_dict['sections'] = sections
            return render(request, 'result.html', context_dict)
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
