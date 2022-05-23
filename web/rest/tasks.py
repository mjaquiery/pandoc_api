import pypandoc
import logging
from django.utils import timezone
from celery import shared_task
from .models import Job, Output, Status

logger = logging.getLogger(__file__)


@shared_task()
def convert_doc(job_id):
    logger.info(f"Starting conversion job {job_id}")
    job = Job.objects.get(id=job_id)
    logger.debug(f"Target format: {job.format}")
    logger.debug(f"Setting status to {Status.IN_PROGRESS.value}")
    job.status = Status.IN_PROGRESS.value
    job.time_start = timezone.now()
    job.save()

    output_path = f"{job.id}/{job.hash[0:7]}.{job.format}"
    logger.info(f"Creating to {output_path}")
    try:
        pypandoc.convert_text(job.content, job.format, outputfile=output_path)
    except BaseException as e:
        logger.error(f"Pandoc error: {e}")
        job.status = Status.ERRORED.value
        job.message = e
        job.time_end = timezone.now()
        job.save()
        return

    Output.objects.create(
        job_id=job.id,
        format=job.format,
        file_path=output_path
    )
    job.status = Status.COMPLETE.value
    job.time_end = timezone.now()
    job.save()
