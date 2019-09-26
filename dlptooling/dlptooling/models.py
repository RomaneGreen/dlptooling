  
from django.db import models

class DLPJob(models.Model):
    """
    This class will store the file uploaded by the user.
    The file will later be analyzed to check for certain reges patters.
    """
    input_file = models.FileField(
        upload_to="dlp_inputs//%Y/%m/%d",
        blank=True,
        null=True,
    )
    FILE_PROCESSED = "PROC"
    FILE_NOT_PROCESSED = "NO PROC"
    FILE_STATS_CHOICES = (
        (FILE_PROCESSED, 'DLP File got processed..'),
        (FILE_NOT_PROCESSED, 'DLP file has not been processed yet.'),
    )
    file_process_status = models.CharField(
        max_length=7,
        choices=FILE_STATS_CHOICES,
        default=FILE_NOT_PROCESSED,
    )
    time_created = models.DateTimeField(
        'started',
        editable=False,
        auto_now_add=True,
        help_text="Time a file was uploaded."
    )
    time_updated = models.DateTimeField(
        'completed',
        editable=False,
        blank=True,
        auto_now=True,
        help_text="Time a file was completed."
    )


class RegexPattern(models.Model):
    """
    Stores patterns of regex. The user can add or delete patterns from
    the admin interface.
    """
    rx_pattern = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    time_created = models.DateTimeField(
        'started',
        editable=False,
        auto_now_add=True,
        help_text="Time a file was uploaded."
    )
    time_updated = models.DateTimeField(
        'completed',
        editable=False,
        blank=True,
        auto_now=True,
        help_text="Time a file was completed."
    )


class CCPattern(models.Model):
    """
    Stores patterns found from the DLP Job/File.
    """
    job_dlp = models.ForeignKey(
        DLPJob,
        on_delete=models.PROTECT
    )
    cc_pattern = models.ForeignKey(
        RegexPattern,
        on_delete=models.PROTECT
    )
    cc_number = models.CharField(
        max_length=16,
        null=True,
        blank=True,
    )
    REGEX_MATCH = 'MATCH'
    REGEX_NO_MATCH = 'NO MATCH'
    REGEX_CHOICES = (
        (REGEX_MATCH, 'Regex Pattern Matched.'),
        (REGEX_NO_MATCH, 'Regex Pattern did not MAtch'),
    )
    regex_status = models.CharField(
        max_length=8,
        choices=REGEX_CHOICES,
        default=REGEX_NO_MATCH,
    )
    time_created = models.DateTimeField(
        'started',
        editable=False,
        auto_now_add=True,
        help_text="Time a file was uploaded."
    )
    time_updated = models.DateTimeField(
        'completed',
        editable=False,
        blank=True,
        auto_now=True,
        help_text="Time a file was completed."
    )