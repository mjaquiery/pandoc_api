import hashlib
import logging
from django.db import models
from django.utils import timezone
from enum import Enum

logger = logging.getLogger(__file__)

LENGTH_HASH = 512
LENGTH_MESSAGE = 1024


class Status(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in progress'
    COMPLETE = 'complete'
    COMPLETE_WITH_WARNINGS = 'complete (with warnings)'
    CANCELLED = 'cancelled'
    ERRORED = 'errored'


class Format(Enum):
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"


class Document(models.Model):
    id = models.BigAutoField(primary_key=True)
    time_created = models.DateTimeField(null=True)
    time_updated = models.DateTimeField(null=True)

    hash = models.CharField(null=False, max_length=LENGTH_HASH, unique=True)
    content = models.BinaryField(null=False)

    def save(self, *args, **kwargs):
        # Recalculate hash
        if type(self.content) is not bytes:
            self.content = bytes(self.content, 'utf8')

        self.hash = hashlib.sha512(self.content).hexdigest()

        # Update timestamps
        if not self.id:
            self.time_created = timezone.now()
        self.time_updated = timezone.now()

        super(Document, self).save(*args, **kwargs)


class Job(models.Model):
    id = models.BigAutoField(primary_key=True)
    time_created = models.DateTimeField(null=True)
    time_updated = models.DateTimeField(null=True)

    document = models.ForeignKey("Document", null=True, on_delete=models.DO_NOTHING)
    format = models.CharField(null=False, default=Format.HTML.value, max_length=LENGTH_HASH)

    time_start = models.DateTimeField(null=True)
    time_end = models.DateTimeField(null=True)
    status = models.SmallIntegerField(
        choices=[(s.value, s.name) for s in Status],
        default=Status.PENDING.value
    )
    message = models.CharField(null=True, max_length=LENGTH_MESSAGE)

    def save(self, *args, **kwargs):
        # Update timestamps
        if not self.id:
            self.time_created = timezone.now()
        self.time_updated = timezone.now()

        super(Job, self).save(*args, **kwargs)


class Output(models.Model):
    id = models.BigAutoField(primary_key=True)
    time_created = models.DateTimeField(null=True)
    time_updated = models.DateTimeField(null=True)
    job = models.ForeignKey("Job", on_delete=models.DO_NOTHING)
    format = models.CharField(default=Format.HTML.value, max_length=LENGTH_HASH)

    file_path = models.CharField(null=False, max_length=LENGTH_MESSAGE)
    time_last_downloaded = models.DateTimeField(null=True)
    download_count = models.SmallIntegerField(null=True, default=0)

    def save(self, *args, **kwargs):
        # Update timestamps
        if not self.id:
            self.time_created = timezone.now()
        self.time_updated = timezone.now()

        super(Output, self).save(*args, **kwargs)
