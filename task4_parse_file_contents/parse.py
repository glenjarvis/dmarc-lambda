import xml.etree.ElementTree as ET
import os
import datetime


MISSING_FIELD = "(missing field)"

HEADERS = ["filename", "report_id", "org_name", "human_date", "begin_epoch_sec",
           "end_epoch_sec", "source_ip", "disposition", "DKIM", "SPF"]
# {0}\t{1}...\t{n}:

OUTPUT_FORMAT = "\t".join(["{{{0}}}".format(r) for r in range(0, 10)])


def node_text(node, field):
    if node is None:
        return MISSING_FIELD

    child = node.find(field)

    if isinstance(child, int):
        return child

    if child is None:
        return MISSING_FIELD
    else:
        return child.text


def report(report_node):
    report_id = node_text(report_node, 'report_id')
    org_name = node_text(report_node, 'org_name')
    date_range = report_node.find('date_range')
    begin_date = node_text(date_range, 'begin')
    end_date = node_text(date_range, 'end')
    return [report_id, org_name, begin_date, end_date]


def parse_row(row_node):
    source_ip = node_text(row_node, 'source_ip')
    policy_evaluated = (row_node.find('policy_evaluated'))
    disposition = node_text(policy_evaluated, 'disposition')
    dkim = node_text(policy_evaluated, 'dkim')
    spf = node_text(policy_evaluated, 'spf')
    return [source_ip, disposition, dkim, spf]


def human(seconds_string):
    return datetime.datetime.utcfromtimestamp(int(seconds_string)).date()


def print_records(filename, root, report_id, org_name, begin_date, end_date):
    for record in root.findall('record'):
        for row in record.findall('row'):
            source_ip, disposition, dkim, spf = parse_row(row)
            print(OUTPUT_FORMAT.format(
                filename, report_id, org_name, human(begin_date),
                begin_date, end_date, source_ip, disposition, dkim, spf))


def process_file(filename):
    try:
        root = ET.parse(filename).getroot()
        report_metadata = root.findall('report_metadata')[0]
        print_records(filename, root, *report(report_metadata))
    except ET.ParseError:
        pass



def main():
    print(OUTPUT_FORMAT.format(*HEADERS))
    for filename in os.listdir('.'):
        _, ext = os.path.splitext(filename)
        if ext == ".xml":
            process_file(filename)


if __name__ == "__main__":
    main()
