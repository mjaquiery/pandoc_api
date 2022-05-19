import hashlib
from django.db import models
from django.utils import timezone
from enum import IntEnum

LENGTH_HASH = 512
LENGTH_MESSAGE = 1024


class Status(IntEnum):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETE = 200
    ERRORED = -1


class Job(models.Model):
    id = models.BigAutoField(primary_key=True)
    time_created = models.DateTimeField(null=False)
    time_updated = models.DateTimeField(null=False)

    hash = models.CharField(null=False, max_length=LENGTH_HASH)
    document = models.BinaryField(null=False)

    time_start = models.DateTimeField(null=True)
    time_end = models.DateTimeField(null=True)
    status = models.SmallIntegerField(
        choices=[(s.value, s.name) for s in Status],
        default=Status.PENDING.value
    )
    message = models.CharField(null=True, max_length=LENGTH_MESSAGE)

    time_last_downloaded = models.DateTimeField(null=True)
    download_count = models.SmallIntegerField(null=True)

    def save(self, *args, **kwargs):
        # Recalculate hash
        if type(self.document) is not bytes:
            self.document = bytes(self.document, 'utf8')

        self.hash = hashlib.sha512(self.document).hexdigest()

        # Update timestamps
        if not self.id:
            self.time_created = timezone.now()
        self.time_updated = timezone.now()

        super(Job, self).save(*args, **kwargs)
