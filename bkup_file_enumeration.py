"""
Script for finding out if there are any backup files left on the website.

Usage:
-f
    File which contains a list of valid webpages, separated by newlines.
    ex: http://www.example.com/page1.php
        https://www.example.com/dir/page2.asp

"""

import argparse
import http.client
import ssl
import urllib.parse


class BackupEnumerator:
    """Backup file finder class."""

    def __init__(self, input_file_name, cookie):
        """Constructor."""
        self.file_extensions_all_possibilities = ["bak", "txt", "src", "dev", "old", "inc", "orig", "copy", "cpy", "tmp", "bkup", "backup", ""]
        self.file_extensions_only_last = [".zip", ".tar", ".gz", ".tar.gz", "~"]
        self.file_extensions_only_first = ["Copy of "]

        self.input_file_name = input_file_name
        self.cookie = cookie

    def enumerate(self):
        """Enumerate all webpages."""
        urls = self.extract_URLs(self.input_file_name)
        print(urls)
        for url in urls:
            self.test_page(url)

    def extract_URLs(self, input_file_name):
        """Get the lines from the file."""
        file = open(input_file_name, 'r')
        lines = []
        for line in file.readlines():
            # Don't add empty lines.
            if len(line.strip()) > 0:
                lines.append(line.strip())
        return lines

    def test_page(self, url):
        """Check if there are any backup files associated with this URL."""
        if self.get_url_components(url):
            components = self.get_url_components(url)
        else:
            return False
        for extension in self.file_extensions_only_first:
            self.check_in_front(components, extension)
        for extension in self.file_extensions_only_last:
            self.check_in_back(components, extension)
        for extension in self.file_extensions_all_possibilities:
            self.check_in_front(components, extension + '.')
            self.check_in_middle(components, '.' + extension)
            self.check_in_back(components, '.' + extension)

    def check_in_back(self, components, extension):
        """
        Check if having the extension in the back gives a valid url.

        Example:
            somePage.php  ==>  somePage.php.zip
        """
        protocol, root, directory, filename = components
        check_filename = filename + extension

        self.request(protocol, root, directory, check_filename)

    def check_in_middle(self, components, extension):
        """
        Check if having the extension in the middle gives a valid url.

        Example:
            somePage.php  ==>  somePage.zip.php
        """
        protocol, root, directory, filename = components
        if len(filename.split('.')) > 1:
            name, original_extension = filename.split('.')
            original_extension = '.' + original_extension
        else:
            return False
        check_filename = name + extension + original_extension

        self.request(protocol, root, directory, check_filename)

    def check_in_front(self, components, extension):
        """
        Check if having the extension in the front gives a valid url.

        Example:
            somePage.php  ==>  Copy of somePage.php
        """
        protocol, root, directory, filename = components
        check_filename = extension + filename

        self.request(protocol, root, directory, check_filename)

    def get_url_components(self, url):
        """Split URL into protocol, directory, filename."""
        if 'http://' not in url and 'https://' not in url:
            print("Protocol not found, skipping: " + url)
            return False
        if url[:7] == 'http://':
            protocol = url[:7]
            file_path = url[7:]
        elif url[:8] == 'https://':
            protocol = url[:8]
            file_path = url[8:]
        else:
            print("Error when parsing protocol. Skipping: " + url)
            return False
        # Split the string from the last '/'.
        # To do this, we reverse the string, split from the first '/' and
        # then reverse them both back.
        filename, root_and_directory = [x[::-1] for x in file_path[::-1].split('/', 1)]
        # Replace the lost '/'
        root_and_directory = root_and_directory + '/'
        root, directory = root_and_directory.split('/', 1)
        directory = '/' + directory
        return [protocol, root, directory, filename]

    def request(self, protocol, root, directory, filename):
        """Make an HTTP or HTTP request to the given URL."""
        check_file_location = urllib.parse.quote(directory + filename)

        print("GET: " + protocol + root + check_file_location)
        try:
            if protocol == 'http://':
                conn = http.client.HTTPConnection(root)
            elif protocol == 'https://':
                conn = http.client.HTTPSConnection(root)
            else:
                raise ValueError('Invalid protocol!')
            if self.cookie:
                headers = {'Cookie': self.cookie}
                conn.request("GET", check_file_location, headers)
            else:
                conn.request("GET", check_file_location)
            response = conn.getresponse()
            print(response.status, response.reason)
        except ssl.SSLError as err:
            print("Request failed, looks like it doesn't support HTTPS?")
            print(err)
            return False
        except Exception as err:
            print('Request failed.')
            print(err)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="Name of the file which contains a list of valid web pages, separated by newlines.")
    parser.add_argument("-c", help="Cookie value. NOT TESTED YET!!!!!", nargs='?', default=None)
    args = parser.parse_args()
    if args.c is not None:
        print("WARNING. I haven't tested whether cookies work correctly yet! The functionality has been implemented though, so disable this if you want to try anyway.")
    else:
        bkenum = BackupEnumerator(args.f, args.c)
        bkenum.enumerate()
