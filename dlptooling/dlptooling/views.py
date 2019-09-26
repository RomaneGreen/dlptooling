import os

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages

from .models import DLPJob

def upload_dlp_file(request):
    """
    Reads credit card number when entered from Slack.
    """
    # Check if there is a POST request initiated.
    if request.POST.get('upload_dlp_file'):
        # Get the file.
        if request.FILES.get('dlp_file'):
            dlp_file = request.FILES.get('dlp_file')
            file_name, extension = os.path.splitext(dlp_file.name)
            if extension != '.csv':
                messages.error(request, "Please upload only .csv files.")
                return redirect('events:upload_dlp_file')

            new_dlp_job = {
                'input_file': dlp_file,
            }
            DLPJob.objects.create(**new_dlp_job)
            messages.success(
                request,
                "File upload was successful. Please check admin for resutls."
            )
            return redirect('events:upload_dlp_file')

    template_path = 'dlptooling/upload_file.html'
    context = {
        'request': request
    }
    return render(request, template_path, context)