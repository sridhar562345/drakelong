
import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    can_import_settings = True
    help = 'Generate views and docs from swagger spec files'

    def add_arguments(self, parser):
        parser.add_argument('-j', '--jars', action='store_true', help='Push JARs to S3.')
        parser.add_argument('-d', '--docs', action='store_true', help='Push Docs to S3.')
        parser.add_argument('-l', '--local', action='store_true', help='Push Docs to S3.')
        parser.add_argument('--bucket', action='store', help='Name of the S3 bucket to push to.', required=True)
        parser.add_argument('--region', action='store', help='Region to upload.',
                            default='eu-west-1')
        parser.add_argument('--prefix', action='store', help='S3 path prefix to upload to.', default='')
        parser.add_argument('--source', action='store', help='Local path prefix to upload to.', default='')

    def handle(self, *args, **options):
        if options['docs']:
            self.upload_dir_files('docs', options)
        if options['jars']:
            self.upload_dir_files('android_jars', options)
        if options['local']:
            self.upload_dir_files(options['source'], options)

    def upload_dir_files(self, dir_name, options):
        from django.conf import settings
        base_dir = settings.BASE_DIR
        dir_path = os.path.join(base_dir, dir_name)

        try:
            if os.path.exists(dir_path):
                command = "aws s3 sync {local_folder} s3://{bucket_name}/{folder_path} --acl public-read".format(
                    local_folder=dir_path, bucket_name=options['bucket'],
                    folder_path=options['prefix'])
                os.system(command)

            else:
                self.stderr.write("%s Not found" % dir_path)
        except Exception as err:
            print(err)
            exit(1)
            raise
