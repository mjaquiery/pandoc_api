import pypandoc
import logging
import os
import pathlib
import tempfile
from django.utils import timezone
from celery import shared_task
from .models import Job, Document, Output, Status

logger = logging.getLogger(__file__)


@shared_task()
def convert_doc(job_id):
    try:
        logger.info(f"Starting conversion job {job_id}")
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        logger.error(f"Job {job_id} does not exist. Aborting.")
        return

    try:
        logger.debug(f"Target format: {job.format}")
        logger.debug(f"Setting status to {Status.IN_PROGRESS.value}")
        job.status = Status.IN_PROGRESS.value
        job.time_start = timezone.now()
        job.save()

        doc = Document.objects.get(job=job)
        logger.debug(f"Document: {doc}")

        output_path = os.path.join("/outputs", f"job_{str(doc.id)}", f"{doc.hash[0:7]}.{job.format}")
        logger.debug(f"Writing to {output_path}")

        # Write the content to disk and load from there to avoid
        # Error: 'memoryview' has no attribute 'encode'
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write(doc.content)

        try:
            pathlib.Path.mkdir(pathlib.Path(os.path.dirname(output_path)), parents=True, exist_ok=True)
            logger.debug(f"Content:\n{tmp_file.readlines()}\n")
            pypandoc.convert_file(
                source_file=tmp_file.name,
                to=job.format,
                format='md',
                outputfile=output_path
            )
        except BaseException as e:
            logger.error(f"Pandoc error: {e}")
            job.status = Status.ERRORED.value
            job.message = e
            job.time_end = timezone.now()
            job.save()
            return
        finally:
            os.unlink(tmp_file.name)

        logger.debug(f"Registering output in database")
        Output.objects.create(
            job_id=job.id,
            format=job.format,
            file_path=output_path
        )
        job.status = Status.COMPLETE.value
        job.time_end = timezone.now()
        job.save()
        logger.info(f"Conversion completed for {job}")

    except BaseException as e:
        logger.error(f"Job scheduler error: {e}")
        job.status = Status.ERRORED.value
        job.message = e
        job.time_end = timezone.now()
        job.save()
