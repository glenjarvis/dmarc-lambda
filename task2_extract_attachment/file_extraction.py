"""file_extraction.py: extracts the zip attachment(s) from raw email file
provided by the Simple Email Service"""

import os
import zipfile
from collections import namedtuple
from email import policy
from email.parser import BytesParser


__author__ = 'sweetjonnie'
__license__ = 'Apache License 2.0'
__email__ = 'jsavell@gmail.com'
__status__ = 'Prototype'

# pylint: disable=too-few-public-methods
FileAttributes = namedtuple('FileAttributes', ['file_name', 'file_content'])
ConsumerSelectionAttributes = namedtuple(
    'ConsumerSelectionAttributes',
    ['predicate', 'consumer']
)


def extract_files(source_filepath, target_directory):

    """the signature of this function is the API of this module
       the implementation of this function is the agent of dependency injection
       source_filepath is the full path to the input file
       target_directory is the full path of the directory to be used for
         processing
       return value is a collection of utf-8 strings, each of which contains
         the contents of an extracted and unarchived file"""

    result = []

    def file_content_consumer(file_content):

        """trivial consumer for file_content collection"""

        result.append(file_content)

    file_consumer = FileConsumer(
        file_content_consumer
    )
    tee_consumer1 = TeeConsumer(
        file_consumer
    )

    # we need to introduce a content-based-router

    # end of content-based-router

    zip_archive_unzip_consumer = ZipArchiveExtractionConsumer(
        tee_consumer1,
        target_directory
    )
    zip_archive_patch_consumer = ZipArchivePatchConsumer(
        zip_archive_unzip_consumer
    )
    file_writer_consumer = FileWriterConsumer(
        zip_archive_patch_consumer,
        target_directory
    )
    tee_consumer2 = TeeConsumer(
        file_writer_consumer
    )
    workflow = MailFileConsumer(
        tee_consumer2
    )

    # initiate consumption
    workflow(
        source_filepath
    )

    return result


def extract_filename(line):

    """NOT part of the API; simply external to its client.
    extract the name of filename from the metadata."""

    key = 'filename'
    filename_position_start = line.index(key) + len(key)

    while (filename_position_start < len(line) and
           not line[filename_position_start].isalpha()):
        filename_position_start += 1

    filename_position_end = len(line) - 1

    while (filename_position_end > 0 and
           not line[filename_position_end].isalpha()):
        filename_position_end -= 1

    if filename_position_end < filename_position_start:
        raise FileNotFoundError('embedded file name not found')
    else:
        return line[filename_position_start: 1 + filename_position_end]


def valid_directory_or_die(directory_path):

    """NOT part of the API; simply external to its client.
    life is too short for bad directories. fight back."""

    if (not os.path.exists(directory_path) or
            not os.path.isdir(directory_path)):
        raise NotADirectoryError(directory_path)
    else:
        return directory_path


def examine_consumer_input(func):

    """NOT part of the API; simply external to its client.
    decorator used for debugging the flow of information.
    don't wish to debug? then don't decorate (TM)."""

    def wrapper(target, value):

        """Crocket: 'just a wrapper function ...'"""

        msg = 'target {} declares input {}'.format(
            target.__class__.__name__,
            value
        )
        print(msg)
        func(target, value)

    return wrapper


# generic consumers
class TeeConsumer:

    """given a collection of things, this command iterates
    over the collection and ships each item downstream. this
    is the map function within the push based command pattern.

    see also:
    https://en.wikipedia.org/wiki/Map_(higher-order_function)
    """

    def __init__(self, consumer):
        self._consumer = consumer

    @examine_consumer_input
    def __call__(self, collection):

        for item in collection:
            self._consumer(item)


class PathSelectionConsumer:

    """configured with a collection of ConsumerSelectionAttributes
    objects which map predicates to consumers, this command selects
    the downstream consumer to pass payload to. if none of the
    predicates match, then the policy function is consulted.
    while this class is generic, the collection of
    ConsumerSelectionAttributes and the policy function with which
    the instance is constructed are very specific to the type of
    data expected in the invocation.

    see also:
    http://www.enterpriseintegrationpatterns.com/patterns/messaging/
    ContentBasedRouter.html
    """

    def __init__(self, selection_attributes, policy):
        self._selection_attributes = selection_attributes
        self._policy = policy

    @examine_consumer_input
    def __call__(self, value):

        for selection_attribute in self._selection_attributes:

            if selection_attribute.predicate(value):
                selection_attribute.consumer(value)
            else:
                pass

        self._policy(value)


# specialized consumers
class MailFileConsumer:

    """given an absolute path to a mail file, this command
    shreds the file and extracts desired attachments.
    attribution: code borrowed from
    https://stackoverflow.com/questions/17874360/
python-how-to-parse-the-body-from-a-raw-email-given-that-raw-email-does-not"""

    def __init__(self, consumer):
        self._consumer = consumer

    @examine_consumer_input
    def __call__(self, file_name):
        result = []

        with open(file_name, 'rb') as file_pointer:

            msg = BytesParser(policy=policy.default).parse(file_pointer)

            if msg.is_multipart():

                for part in msg.walk():

                    content_type = part.get_content_type()
                    content_disposition = part.get('Content-Disposition')
                    content = part.get_payload(decode=True)

                    if (content_type == 'application/zip' and
                            content_disposition is not None and
                            content_disposition.startswith('attachment;')):
                        try:
                            file_name = extract_filename(content_disposition)

                            file_attributes = FileAttributes(
                                file_name=file_name,
                                file_content=content
                            )

                            result.append(file_attributes)
                        except ValueError:
                            # this is an error we may discard
                            pass

            if len(result) <= 0:
                raise FileNotFoundError('no embedded file found')
            else:
                return self._consumer(result)


class FileWriterConsumer:

    """given a file-attributes object, this command creates
    and populates a file."""

    def __init__(self, consumer, directory_path):
        self._consumer = consumer
        self._directory_path = valid_directory_or_die(directory_path)

    @examine_consumer_input
    def __call__(self, file_attributes):

        file_path = os.path.join(
            self._directory_path,
            file_attributes.file_name
        )

        with open(file_path, 'wb') as file_pointer:
            file_pointer.write(file_attributes.file_content)

        return self._consumer(file_path)


class ZipArchivePatchConsumer:

    """given an absolute path to an archive file, this
    command patches the archive in order to overcome a
    limitation of the zipfile module.
    attribution: code stolen from
    https://stackoverflow.com/questions/3083235/
    unzipping-file-results-in-badzipfile-file-is-not-a-zip-file"""

    def __init__(self, consumer):
        self._consumer = consumer

    @examine_consumer_input
    def __call__(self, archive_path):
        with open(archive_path, 'r+b') as file_pointer:
            content = file_pointer.read()
            pos = content.rfind(b'\x50\x4b\x05\x06')

            if pos > 0:
                file_pointer.seek(pos + 20)
                file_pointer.truncate()
                file_pointer.write(b'\x00\x00')
                file_pointer.seek(0)
            else:
                pass

        self._consumer(archive_path)


class ZipArchiveExtractionConsumer:

    """given an archive file, this command unarchives
    the file and creates a file for each piece of content
    found within."""

    def __init__(self, consumer, directory_path):
        self._consumer = consumer
        self._directory_path = valid_directory_or_die(directory_path)

    @examine_consumer_input
    def __call__(self, archive_path):
        result = []

        with zipfile.ZipFile(archive_path) as zip_file:
            for info in zip_file.infolist():
                file_name = info.filename
                file_path = os.path.join(self._directory_path, file_name)

                with open(file_path, 'wb') as file_pointer:
                    file_pointer.write(zip_file.read(file_name))

                    result.append(file_path)

        self._consumer(result)

        # os.remove(archive_path)


class FileConsumer:

    """given an absolute path to a file, this command
    exports the file's contents."""

    def __init__(self, consumer):
        self._consumer = consumer

    @examine_consumer_input
    def __call__(self, file_path):
        with open(file_path, encoding='utf-8') as file_pointer:
            content = file_pointer.read()

        self._consumer(content)

        # os.remove(file_path)
