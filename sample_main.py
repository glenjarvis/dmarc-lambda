"""Sample integration between task2 and task4 modules"""

from task2_extract_attachment.file_extraction import DmarcFileExtractor
from task4_parse_file_contents.parse import process_file


def main():

    """simple integration of file extraction and content processing"""

    destination_dir = './task2_extract_attachment/test'
    file = './task2_extract_attachment' +\
           '/tcq88aasf2uj5r4dknkpmp641bloic79f8399ag1'
    source_files = [file]
    dmarc_file_extractor = DmarcFileExtractor(destination_dir)

    for source_file in source_files:

        file_list = dmarc_file_extractor.process(source_file)

        for filename in file_list:
            process_file(filename)


if __name__ == '__main__':
    main()
