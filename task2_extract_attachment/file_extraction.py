"""Extracts archived attachments from an email and returns dmarc paths."""

import os
import zipfile
import gzip
import datetime
from collections import namedtuple
from email import policy
from email.parser import BytesParser
import xml.etree.ElementTree as xml


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


class DmarcFileExtractor:

    """Parses the mail file and returns the paths of valid dmarc file.

    This is the sole member of the API in this module. The
    implementation of this function is the composition of several
    commands. Specifically, this function assembles a workflow by
    wiring these commands together.

    Given a directory at which files are to be placed, an instance
    of this class may be used several times for each email file
    processed. Because the extracted files remain after execution,
    a client performing an invocation may stumble upon one or more
    files produced during a previous invocation. Therefore, it is
    incumbent upon a client to use the return value of an
    invocation to determine which files were produced during that
    invocation.

    WARNING: An instance of this class is NOT suitable for use
    within multiple threads of execution.

    source_filepath is the full path to the input file
    target_directory is the full path of the directory where dmarc
        files are to be placed
    return value is a collection of zero or more paths, each of which
        is the absolute path of an extracted and unarchived xml file
    """

    def __init__(self, target_directory):

        self._result_consumer = ResultConsumer()
        mapping_consumer1 = MappingConsumer(
            self._result_consumer
        )
        zip_archive_unzip_consumer = ZipArchiveExtractionConsumer(
            mapping_consumer1,
            target_directory
        )
        zip_archive_patch_consumer = ZipArchivePatchConsumer(
            zip_archive_unzip_consumer
        )
        gzip_archive_unzip_consumer = GzipArchiveExtractionConsumer(
            self._result_consumer,
            target_directory
        )

        # content-based-router: to zip or gzip ...
        attributes_1 = ConsumerSelectionAttributes(
            predicate=lambda archive_path: archive_path.endswith('.zip'),
            consumer=zip_archive_patch_consumer
        )
        attributes_2 = ConsumerSelectionAttributes(
            predicate=lambda archive_path: archive_path.endswith('.gz'),
            consumer=gzip_archive_unzip_consumer
        )
        archive_selection_consumer = PathSelectionConsumer(
            [attributes_1, attributes_2],
            lambda ignored: True
        )

        file_writer_consumer = FileWriterConsumer(
            archive_selection_consumer,
            target_directory
        )
        mapping_consumer2 = MappingConsumer(
            file_writer_consumer
        )

        self._workflow = MailFileConsumer(
            mapping_consumer2,
            archive_selection_criteria
        )

    def process(self, source_filepath):

        """This is the sole method for this class; this is the API."""

        self._result_consumer.results = []
        self._workflow(source_filepath)

        results = list(self._result_consumer.results)
        self._result_consumer.results = []

        return results


def extract_filename(line):

    """Extract the name of filename from the metadata.

    NOT part of the API; simply external to its client.
    """

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

    """Validate the directory whose path is provided.

    NOT part of the API; simply external to its client.
    """

    if (not os.path.exists(directory_path) or
            not os.path.isdir(directory_path)):
        raise NotADirectoryError(directory_path)
    else:
        return directory_path


def filename_from_gzip_name(gzip_filename):

    """Infers the name of embedded content from the name of an archive.

    NOT part of the API; simply external to its client.
    Gzip attempts to preserve the original filename but it can
    subsequently be renamed. This function attempts to recover the
    original filename (under the assumption that the filename was
    not modified) by examining the components of the filename
    rather than looking inside of the archive. In the event that
    this algorithm fails to restore the filename (possibly because
    the filename was subsequently modified), then this algorithm
    will provide a name based on the current timestamp. Finally,
    because the dmarc file is xml, this function optimistically
    adds an xml suffix if one is not present.

    see also:
    https://superuser.com/questions/859785/
    is-gzip-supposed-to-honor-original-filename-during-decompress
    """

    file_name_components = gzip_filename.split('.')
    result = None

    if len(file_name_components) <= 1:
        # deviant case
        result = ''.join(
            map(
                lambda c: '_' if c in ('-', ':', '.', ' ') else c,
                str(datetime.datetime.utcnow())
            )
        )
    else:
        file_name_components.pop()
        file_name = '.'.join(file_name_components)
        result = file_name

    if not result.endswith('.xml'):
        result += '.xml'
    else:
        pass

    return result


def validate_dmarc_document(content):

    """Validate the content of a file against dmarc criteria.

    NOT part of the API; simply external to its client.
    This procedure attempts to verify whether the file is dmarc,
    a dialect of XML, by opening it up with the etree library
    and looking for dmarc elements.
    """

    try:
        document = xml.fromstring(content.decode('utf-8'))
        report_metadata = document.find('report_metadata')
        report_metadata.find('org_name').text.strip()
    except Exception as exception:
        raise TypeError(exception)


def archive_selection_criteria(content_type, content_disposition):

    """Determine whether the payload within the email is worthy.

    NOT part of the API; simply external to its client.
    TODO: is this the complete list of criteria?
    the following article suggests there may be more:
    https://stackoverflow.com/questions/6977544/
    rar-zip-files-mime-type"""

    return ((content_type == 'application/zip' or
             content_type == 'application/gzip') and
            content_disposition is not None and
            content_disposition.startswith('attachment;'))


def examine_consumer_input(func):

    """Decorator used for debugging the flow of information.

    NOT part of the API; simply external to its client.
    Don't wish to debug? then don't decorate (TM).
    """

    def wrapper(target, value):

        """The wrapper function which prints and invokes the command."""

        msg = 'target {} declares input {}'.format(
            target.__class__.__name__,
            value
        )

        print(msg)

        func(target, value)

    return wrapper


# generic consumers
class MappingConsumer:

    """Invokes the downstream command against each in a collection.

    This is the push based command pattern equivalent of the map
    function.

    see also:
    https://en.wikipedia.org/wiki/Map_(higher-order_function)
    """

    def __init__(self, consumer):
        self._consumer = consumer

    # @examine_consumer_input
    def __call__(self, collection):

        for item in collection:
            self._consumer(item)


class PathSelectionConsumer:

    """This command selects the consumer to pass the given payload to.

    This command is configured with a collection of
    ConsumerSelectionAttributes objects, each of which maps a predicate
    function to a downstream consumer. When a payload is passed to an
    invocation of this command, Each predicate is tested in order until
    one predicate succeeds. At this point, the payload is passed to the
    consumer associated with that predicate. If none of the predicates
    succeed, then the policy function, with which this class was
    configured, will be consulted.

    see also:
    http://www.enterpriseintegrationpatterns.com/patterns/messaging/
    ContentBasedRouter.html
    """

    def __init__(self, selection_attributes, policy_function):
        self._selection_attributes = selection_attributes
        self._policy_function = policy_function

    # @examine_consumer_input
    def __call__(self, value):

        for selection_attribute in self._selection_attributes:

            if selection_attribute.predicate(value):
                return selection_attribute.consumer(value)
            else:
                pass

        self._policy_function(value)


# specialized consumers
class ResultConsumer:

    """This consumer receives each result and adds it to its collection."""

    @property
    def results(self):

        """The results property contains the workflow's output."""

        return self._results

    @results.setter
    def results(self, results):

        """Clients need to reset this prior to invoking workflow."""

        # pylint: disable=attribute-defined-outside-init
        self._results = results

    # @examine_consumer_input
    def __call__(self, result):

        """trivial consumer for result collection"""

        self._results.append(result)


class MailFileConsumer:

    """This command reads an email and extracts desired attachments.

    Given an absolute path to a mail file, this command examines each
    attachment and determines, according to the policy provided by the
    content_criteria function, whether that attachment is desirable.

    attribution:
    https://stackoverflow.com/questions/17874360/
python-how-to-parse-the-body-from-a-raw-email-given-that-raw-email-does-not"""

    def __init__(self, consumer, content_criteria):
        self._consumer = consumer
        self._content_criteria = content_criteria

    # @examine_consumer_input
    def __call__(self, file_path):
        result = []

        with open(file_path, 'rb') as file_pointer:

            msg = BytesParser(policy=policy.default).parse(file_pointer)

            if msg.is_multipart():

                for part in msg.walk():

                    content_type = part.get_content_type()
                    content_disposition = part.get('Content-Disposition')
                    content = part.get_payload(decode=True)

                    if self._content_criteria(
                            content_type,
                            content_disposition
                    ):
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

    """This command creates and populates a file.

    The name and contents of the file are provided by the
    File_Attributes object passed as an argument and the resulting
    file is placed at the location specified by directory_path.
    """

    def __init__(self, consumer, directory_path):
        self._consumer = consumer
        self._directory_path = valid_directory_or_die(directory_path)

    # @examine_consumer_input
    def __call__(self, file_attributes):

        file_path = os.path.join(
            self._directory_path,
            file_attributes.file_name
        )

        with open(file_path, 'wb') as file_pointer:
            file_pointer.write(file_attributes.file_content)

        return self._consumer(file_path)


class ZipArchivePatchConsumer:

    """This command patches a zip archive file.

    There is a documented limitation of the zipfile module that
    this patch was designed to address.

    attribution:
    https://stackoverflow.com/questions/3083235/
    unzipping-file-results-in-badzipfile-file-is-not-a-zip-file
    """

    def __init__(self, consumer):
        self._consumer = consumer

    # @examine_consumer_input
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

        return self._consumer(archive_path)


class ZipArchiveExtractionConsumer:

    """This command decompresses a zip file.

    Each file embedded in the archive is extracted and placed at the
    location specified by directory_path.
    """

    def __init__(self, consumer, directory_path):
        self._consumer = consumer
        self._directory_path = valid_directory_or_die(directory_path)

    # @examine_consumer_input
    def __call__(self, archive_path):
        result = []

        with zipfile.ZipFile(archive_path) as zip_file:
            for info in zip_file.infolist():
                file_name = info.filename
                file_path = os.path.join(self._directory_path, file_name)

                with open(file_path, 'wb') as file_pointer:
                    file_pointer.write(zip_file.read(file_name))

                    result.append(file_path)

        return self._consumer(result)


class GzipArchiveExtractionConsumer:

    """This command decompresses a gzip file.

    The decompressed file is then placed at the location specified by
    directory_path.

    'Although its file format also allows for multiple such streams to
    be concatenated (zipped files are simply decompressed concatenated
    as if they were originally one file[3]), gzip is normally used to
    compress just single files.'

    see also:
    https://en.wikipedia.org/wiki/Gzip
    """

    def __init__(self, consumer, directory_path):
        self._consumer = consumer
        self._directory_path = valid_directory_or_die(directory_path)

    # @examine_consumer_input
    def __call__(self, archive_path):

        result = []

        with gzip.open(archive_path, 'rb') as gzip_file:
            content = gzip_file.read()

        try:
            validate_dmarc_document(content)
            gzip_file_name = os.path.basename(archive_path)
            file_name = filename_from_gzip_name(gzip_file_name)
            file_path = os.path.join(self._directory_path, file_name)

            with open(file_path, 'wb') as file_pointer:
                file_pointer.write(content)

            result.append(file_path)

        except TypeError:
            pass

        if len(result) == 1:
            return self._consumer(result[0])


class FileConsumer:

    """This command exports the file's contents."""

    def __init__(self, consumer):
        self._consumer = consumer

    # @examine_consumer_input
    def __call__(self, file_path):
        with open(file_path, encoding='utf-8') as file_pointer:
            content = file_pointer.read()

        return self._consumer(content)
