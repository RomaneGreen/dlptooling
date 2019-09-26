# from __future__ import absolute_import
# import os
# from celery import Celery
# from django.conf import settings

# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dlptooling.settings')
# app = Celery('dlptooling')

# # Using a string here means the worker will not have to
# # pickle the object when using Windows.
# app.config_from_object('django.conf:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))


import re
import io
import csv

from io import StringIO
from slackclient import SlackClient

from django.conf import settings
from events.models import DLPJob
from events.models import RegexPattern
from events.models import CCPattern

from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)


@periodic_task(
    run_every=(crontab(minute='*/1')),
    name="listen_to_slack_msg",
    ignore_result=True
)
def listen_to_slack_msg():
    """
    Listents to Slack messages every minute.
    """
    client = SlackClient(SLACK_BOT_USER_TOKEN)
    success = client.rtm_connect(with_team_state=False)
    if not success:
        logger.info("Not able to connect to slack!!")
    else:
        events = client.rtm_read()

@periodic_task(
    run_every=(crontab(minute='*/1')),
    name="process_dlp_jobs",
    ignore_result=True
)
def process_dlp_jobs():
    """
    Opens up the DLP file and processes the entire file
    """
    # Query DLP Jobs will status NOT PROC.
    not_processed_dlp_files = DLPJob.objects.filter(
        file_process_status=DLPJob.FILE_NOT_PROCESSED,
    ).order_by('time_created')
    print()
    print("* * * not_processed_dlp_files: ", not_processed_dlp_files)

    if not_processed_dlp_files:
        dlp_obj = not_processed_dlp_files.first()
        dlp_input_file = dlp_obj.input_file
        dlp_input_file = StringIO(dlp_input_file.read().decode(errors='ignore'))
        dlp_input_file = csv.DictReader(dlp_input_file)

        regex_pattern = RegexPattern.objects.all().values_list('rx_pattern', flat=True)
        print("* * * regex_pattern: ", regex_pattern)
        for row in dlp_input_file:
            for rx in regex_pattern:
                regex_match = re.findall(rx, row['CCNUM'])
                if regex_match:
                    new_cc_obj = {
                        'job_dlp': dlp_obj,
                        'cc_pattern': RegexPattern.objects.get(rx_pattern=regex_match[0]),
                        'cc_number': row['CCNUM'],
                        'regex_status': CCPattern.REGEX_MATCH,
                    }
                    CCPattern.objects.create(**new_cc_obj)
                    break
            else:
                # Send Msg to Slack.
                client = SlackClient(SLACK_BOT_USER_TOKEN)
                success = client.rtm_connect(with_team_state=False)
                if not success:
                    logger.info("Not able to connect to slack!!")
                else:
                    slack_msg = ".csvRow: {}; regex: {}".format(str(row), str(regex_pattern))
                    client.api_call("chat.postMessage", channel="general", text=slack_msg)

                new_cc_obj = {
                    'job_dlp': dlp_obj,
                    'cc_pattern': RegexPattern.objects.get(rx_pattern=rx),
                    'cc_number': row['CCNUM'],
                    'regex_status': CCPattern.REGEX_NO_MATCH,
                }
                CCPattern.objects.create(**new_cc_obj)
            print("* * * row: ", row)
        dlp_obj.file_process_status = DLPJob.FILE_PROCESSED
        dlp_obj.save()