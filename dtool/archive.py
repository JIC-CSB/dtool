"""Module wrapping tar and gzip."""

import os
import json
import hashlib
import subprocess
import tarfile

from dtool import DataSet


def shasum_from_file_object(f):

    BUF_SIZE = 65536
    hasher = hashlib.sha1()
    buf = f.read(BUF_SIZE)
    while len(buf) > 0:
        hasher.update(buf)
        buf = f.read(BUF_SIZE)

    return hasher.hexdigest()


class ArchiveDataSet(DataSet):
    """Class for creating specific archive datasets."""

    def __init__(self, name):
        super(ArchiveDataSet, self).__init__(name=name,
                                             data_directory="archive")


class _ArchiveFileBase(object):

    # Don't touch this!
    header_file_order = (".dtool/dtool",
                         ".dtool/manifest.json",
                         "README.yml")


class ArchiveFileBuilder(_ArchiveFileBase):
    """Class for building up tarred archive datasets.
    """

    def __init__(self):
        self._tar_path = None
        self._archive_dataset = None

    @classmethod
    def from_path(cls, path):
        """Return :class:`dtool.archive.ArchiveFileBuilder`.

        Parsed from a archive dataset directory."""
        archive_builder = cls()
        archive_builder._archive_dataset = ArchiveDataSet.from_path(path)
        return archive_builder

    def initialise_tar(self, path):
        path = os.path.abspath(path)
        self._tar_path = os.path.join(
            path, self._archive_dataset.name + ".tar")
        working_dir, dataset_dir = os.path.split(
            self._archive_dataset._abs_path)

        headers_with_path = [os.path.join(dataset_dir, hf)
                             for hf in ArchiveFile.header_file_order]

        cmd = ["tar", "-cf", self._tar_path] + headers_with_path
        subprocess.call(cmd, cwd=working_dir)

    def append_to_tar(self, path):
        path = os.path.abspath(path)
        working_dir, dataset_dir = os.path.split(
            self._archive_dataset._abs_path)
        archive_dir_rel_path = os.path.join(
            dataset_dir, self._archive_dataset.data_directory)
        cmd = ["tar", "-rf", self._tar_path, archive_dir_rel_path]
        subprocess.call(cmd, cwd=working_dir)

    def persist_to_tar(self, path):
        """Write archive dataset to tarball."""

        self._archive_dataset.update_manifest()
        self.initialise_tar(path)
        self.append_to_tar(path)

        return self._tar_path


class ArchiveFile(_ArchiveFileBase):
    """Class for working with tarred/gzipped archive datasets.

    Initialising using a dataset is used for creating archives, while
    initialising from a file is used for extracting and verifying."""

    # TODO - consider replacing initialisation with a .from_dataset
    def __init__(self):
        self._name = None
        self._tar_path = None

    def _extract_file_contents(self, file_path):
        with tarfile.open(self._tar_path, 'r:*') as tar:
            fp = tar.extractfile(file_path)
            contents = fp.read()

        return contents

    def _extract_string_contents(self, file_path):
        contents = self._extract_file_contents(file_path)

        return contents.decode('utf-8')

    @property
    def admin_metadata(self):

        return self._admin_metadata

    @property
    def manifest(self):

        return self._manifest

    @classmethod
    def from_file(cls, path):
        """Read archive from file, either .tar or .tar.gz"""

        archive_file = cls()

        archive_file._tar_path = path

        with tarfile.open(path, 'r:*') as tar:
            first_member = tar.next()
            archive_file._name, _ = first_member.name.split(os.path.sep, 1)

        admin_file_path = os.path.join(archive_file._name, '.dtool', 'dtool')
        admin_str = archive_file._extract_string_contents(admin_file_path)
        archive_file._admin_metadata = json.loads(admin_str)

        manifest_file_path = os.path.join(
            archive_file._name,
            archive_file.admin_metadata['manifest_path'])
        manifest_str = archive_file._extract_string_contents(
            manifest_file_path)
        archive_file._manifest = json.loads(manifest_str)

        return archive_file

    def calculate_file_hash(self, filename):

        full_file_path = os.path.join(
            self._name,
            self.admin_metadata['manifest_root'],
            filename)

        with tarfile.open(self._tar_path, 'r:*') as tar:
            fp = tar.extractfile(full_file_path)

            return shasum_from_file_object(fp)

    def verify_file(self, file_in_archive):
        """Verify single file in archive.

        :param file_in_archive: file to verify
        :returns: True if checksum matches, False otherwise.
        """
        file_list = self.manifest["file_list"]

        filedict_by_path = {entry['path']: entry for entry in file_list}

        file_entry = filedict_by_path[file_in_archive]

        manifest_hash = file_entry['hash']
        archive_hash = self.calculate_file_hash(file_in_archive)

        return manifest_hash == archive_hash

    def verify_all(self):
        """Verify all files in archive.

        :returns: True if all files verify, False otherwise.
        """

        # TODO - raise exception?

        file_list = self.manifest["file_list"]

        for entry in file_list:
            file_in_archive = entry['path']
            manifest_hash = entry['hash']
            archive_hash = self.calculate_file_hash(file_in_archive)

            if archive_hash != manifest_hash:
                return False

        return True

    def summarise(self):
        """Return dictionary with summary information about an archive.

        :returns: dictionary of summary information about the archive
        """
        total_size = sum(entry['size'] for entry in self.manifest['file_list'])

        summary = {}
        summary['n_files'] = len(self.manifest['file_list'])
        summary['total_size'] = total_size
        summary['manifest'] = self.manifest

        return summary


################################################################
# Helper function(s) for wrapping shell commands on the tar file.
################################################################


def compress_archive(path, n_threads=8):
    """Compress the (tar) archive at the given path.

    Uses pigz for speed.

    :param path: path to the archive tarball
    :param n_threads: number of threads for pigz to use
    :returns: path to created gzip file
    """
    path = os.path.abspath(path)

    basename = os.path.basename(path)
    archive_name, ext = os.path.splitext(basename)
    assert ext == '.tar'

    compress_tool = 'pigz'
    compress_args = ['-p', str(n_threads), path]
    compress_command = [compress_tool] + compress_args

    subprocess.call(compress_command)

    return path + '.gz'
