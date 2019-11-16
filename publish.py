#!/usr/bin/env python
from glob import glob
from pprint import pprint
import traceback
from praw import Reddit
from praw.exceptions import ClientException, PRAWException
import argparse
import sys
import os
from pathlib import Path

PROGRAM = "Reddit Stylesheet Updater"
VERSION = "0.5"
MAX_EDIT_REASON_LENGTH = 256
IMAGE_SUFFIXES = ['jpg', 'jpeg', 'png']

class StyleSheetUpdater:

    def __init__(self, ua):
        self.ua = ua

    def main(self):
        argparser = argparse.ArgumentParser('Publish reddit stylesheet')
        argparser.add_argument("-c", "--clear", action='store_true', help="Clear subreddit styles and images before uploading (rarely    necessary)")
        argparser.add_argument("subreddit", help="Subreddit to upload to")
        argparser.add_argument("dir", help="Dir to push files from")
        self.args = argparser.parse_args()

        sr_name = self.args.subreddit
        input_dir = Path(self.args.dir)

        #self.r = Reddit(ua=self.ua)
        #self.subreddit = self.r.subreddit(sr_name)

        if self.args.clear:
            self.clear()

        stylesheet = None
        for fn in input_dir.glob('**/*'):
            if not fn.is_file():
                continue
            print("File: %s" % fn)
            suf = fn.suffix.lower()
            if suf == '.css':
                print("Stylesheet: %s" % fn)
                #stylesheet = codecs.getreader("UTF-8")(fn)
            elif suf in IMAGE_SUFFIXES:
                if self.args.no_images:
                    print("Not uploading image %s" % fn)
                    continue
                try:
                    #self.upload_file(fn)
                    print("Upload file %s" % fn)
                    pass
                except ClientException as e:
                    print("Failed uploading %s" % fn)
                    traceback.print_exc()
            else:
                print("Skipping file %s" % fn)
        # Need to do this last, or the images wouldn't be there
        if stylesheet:
            self.put_stylesheet(stylesheet.read(), reason=self.args.reason)

    def put_stylesheet(self, styles, reason = u''):
        print("Put stylesheet to %s:\n-------------------------------------------------\n%s\n-------------------------------------------------" % (self.subreddit.display_name, styles))
        ss_wp = "config/stylesheet"
        try:
            reason = reason[:MAX_EDIT_REASON_LENGTH]
            r = self.subreddit.edit_wiki_page(ss_wp, styles, reason=reason)
            print(repr(r))
        except PRAWException as e:
            print(e._raw.status_code)
            print(e._raw.text)
            raise e

    def upload_file(self, fn):
        print("upload file %s" % fn)
        self.subreddit.upload_image(fn)

    def clear(self):
        print("clear all styles and files")
        existing_styles = self.subreddit.get_stylesheet()
        self.put_stylesheet('')
        for image in existing_styles['images']:
            print("  Removing %(name)s" % image)
            self.subreddit.delete_image(image['name'])


if __name__ == "__main__":
    DUMMY_VALUE = 'dc38489e-3cc0-4167-83c6-f992d50fb04e'
    print("::add-mask::%s" % os.environ.get('praw_client_id', DUMMY_VALUE))
    print("::add-mask::%s" % os.environ.get('praw_client_secret', DUMMY_VALUE))
    print("::add-mask::%s" % os.environ.get('praw_client_refresh_token', DUMMY_VALUE))
    print("::add-mask::%s" % os.environ.get('praw_password', DUMMY_VALUE))
    print("::add-mask::%s" % os.environ.get('praw_username', DUMMY_VALUE))

    pprint(sys.argv)
    pprint(os.environ)
    pprint(glob('%s/%s/**' % (os.environ['GITHUB_WORKSPACE'], sys.argv[2]), recursive=True))
    pprint(glob('%s/**' % (sys.argv[2]), recursive=True))

    uploader = StyleSheetUpdater("%s/%s" % (PROGRAM, VERSION))
    uploader.main()
