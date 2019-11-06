#!/usr/bin/env python
import click
import urllib
from bs4 import BeautifulSoup
import re


def slice(lines, keyword, start):
    """
    Get sliced lines for each test run in consoleText
    by splitting by the strings foodnet: r'foodnet' and a space: r' ' at the end.
    :param lines: parsed HTML
    :param keyword: word to cut line with
    :return:
    """
    lines_sliced=[]
    for line in lines:
        foodnet_line = re.search(keyword, line)
        if foodnet_line is not None:
            foodnet_line_ind = foodnet_line.start()
            if start:
                cut_line = line[foodnet_line_ind::]
            else:
                cut_line = line[:foodnet_line_ind]
            if type(cut_line) == unicode:
                lines_sliced.append(cut_line.encode("utf-8"))
            else:
                lines_sliced.append(cut_line)
        else:
            pass
    return lines_sliced

def escape_brackets(lines, open_bracket, close_bracket):
    """
    Escape brackets from individual foodnet lines in consoleText
    :param lines: slices lines from slice()
    :param open_bracket: string form of the open brackets e.g. "["
    :param close_bracket: string form of the open brackets e.g. "]"
    :return:
    """
    lines_sliced = []
    for line in lines:
        if open_bracket in line:
            pos=line.find(open_bracket)
            pos2=line.find(close_bracket)
            line=list(line)
            line[pos]="\\"+open_bracket
            line[pos2]="\\"+close_bracket
            line="".join(line)
        else:
            pass
        lines_sliced.append(line)
    return lines_sliced

@click.option('--job_number')  # e.g.: '1495' .../scope-django-111-branches/job_number
@click.option('--worker')  # e.g.: '[gw8]'
@click.command()
def main(job_number, worker):
    # URL set to branch # / consoleText for error text.
    url = "http://jenkins.ci.rd/job/scope-django-111-branches/{}/consoleText"\
        .format(job_number)
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html, "lxml")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # get text
    text = soup.get_text()

    # break into lines
    lines = text.splitlines()

    worker_lines=[]

    # grab lines that contain worker number
    for line in lines:
        if '[{}]'.format(worker) in line:
            worker_lines.append(line)

    sliced_line = slice(worker_lines, r'foodnet', True)
    sliced_line = slice(sliced_line, r' ', False)
    sliced_line = escape_brackets(sliced_line, "[", "]")
    sliced_line = escape_brackets(sliced_line, "(", ")")

    final_string=' \\'.join(sliced_line)
    print final_string

if __name__ == "__main__":
    main()

