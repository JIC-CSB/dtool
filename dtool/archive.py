"""Module wrapping tar and gzip."""

import os
import json
import uuid
import hashlib
import subprocess
import tarfile


def shasum_from_file_object(f):

    BUF_SIZE = 65536
    hasher = hashlib.sha1()
    buf = f.read(BUF_SIZE)
    while len(buf) > 0:
        hasher.update(buf)
        buf = f.read(BUF_SIZE)

    return hasher.hexdigest()


class Archive(object):

    @classmethod
    def from_file(cls, file_path):

        archive = cls()

        archive.file_path = file_path
        basename = os.path.basename(file_path)
        archive.name, _ = basename.split('.', 1)

        info_file_path = os.path.join(archive.name, '.dtool-dataset')
        with tarfile.open(archive.file_path, 'r:*') as tar:
            info_fp = tar.extractfile(info_file_path)
            info_str = info_fp.read().decode("utf-8")
            archive.info = json.loads(info_str)

        manifest_path = os.path.join(archive.name, 'manifest.json')
        with tarfile.open(archive.file_path, 'r:*') as tar:
            manifest_fp = tar.extractfile(manifest_path)
            manifest_str = manifest_fp.read().decode("utf-8")
            archive.manifest = json.loads(manifest_str)

        archive.uuid = archive.info['uuid']

        return archive

    def calculate_file_hash(self, filename):

        full_file_path = os.path.join(self.name, 'archive', filename)

        with tarfile.open(self.file_path, 'r:*') as tar:
            fp = tar.extractfile(full_file_path)

            return shasum_from_file_object(fp)


def initialise_tar_archive(archive_path, fname_to_add):
    """Initialise a tar archive.

    :param archive_path: path to the directory to archive
    :param rel_fpath_to_add: relative path to file in the archive directory to
                             add to tar archive
    :returns: tar output filename
    """
    archive_path = os.path.abspath(archive_path)
    working_dir, dataset_name = os.path.split(archive_path)

    tar_output_filename = dataset_name + ".tar"
    path_to_add = os.path.join(dataset_name, fname_to_add)

    cmd = ["tar", "-cf", tar_output_filename, path_to_add]
    subprocess.call(cmd, cwd=working_dir)

    tar_output_filename = os.path.join(working_dir, tar_output_filename)
    return tar_output_filename


def append_to_tar_archive(archive_path, fname_to_add):
    """Initialise a tar archive.

    :param archive_path: path to the directory to archive
    :param rel_fpath_to_add: relative path to file in the archive directory to
                             add to tar archive
    :returns: tar output filename
    """
    archive_path = os.path.abspath(archive_path)
    working_dir, dataset_name = os.path.split(archive_path)

    tar_output_filename = dataset_name + ".tar"
    path_to_add = os.path.join(dataset_name, fname_to_add)

    cmd = ["tar", "-rf", tar_output_filename, path_to_add]
    subprocess.call(cmd, cwd=working_dir)

    tar_output_filename = os.path.join(working_dir, tar_output_filename)
    return tar_output_filename


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


def extract_file(archive_path, file_in_archive):
    """Extract a file from an archive.

    The archive can be a tarball or a compressed tarball.

    :param archive_path: path to the archive to extract a file from
    :param file_in_archive: file to extract
    :returns: path to extracted file
    """
    archive_path = os.path.abspath(archive_path)

    archive_basename = os.path.basename(archive_path)
    archive_dirname = os.path.dirname(archive_path)
    archive_name, exts = archive_basename.split('.', 1)
    assert "tar" in exts.split(".")  # exts is expected to be tar or tar.gz

    extract_path = os.path.join(archive_name, file_in_archive)
    with tarfile.open(archive_path, 'r:*') as tar:
        tar.extract(extract_path, path=archive_dirname)

    return os.path.join(archive_dirname, extract_path)


def verify_file(archive_path, file_in_archive):
    """Verify single file in archive.

    The archive can be a tarball or a compressed tarball.

    :param archive_path: path to the archive containing the file
    :param file_in_archive: file to verify
    :returns: True if checksum matches, False otherwise.
    """
    archive_path = os.path.abspath(archive_path)

    archive = Archive.from_file(archive_path)

    file_list = archive.manifest["file_list"]

    filedict_by_path = {entry['path']: entry for entry in file_list}

    file_entry = filedict_by_path[file_in_archive]

    manifest_hash = file_entry['hash']
    archive_hash = archive.calculate_file_hash(file_in_archive)

    return manifest_hash == archive_hash


def verify_all(archive_path):
    """Verify all files in archive.

    :param archive_path: path to archive containing files
    :returns: True if all files verify, False otherwise.
    """

    # TODO - raise exception?

    archive_path = os.path.abspath(archive_path)

    archive = Archive.from_file(archive_path)

    file_list = archive.manifest["file_list"]

    for entry in file_list:
        file_in_archive = entry['path']
        manifest_hash = entry['hash']
        archive_hash = archive.calculate_file_hash(file_in_archive)

        if archive_hash != manifest_hash:
            return False

    return True


def icreate_collection(staging_path, collection_name):
    """Create new collection. If collection exists, return path to existing
    collection. The i in icreate refers to the fact that the function is
    idempotent.

    :param staging_path: path in which to create collection
    :param collection_name: name of collection to create
    :returns: Path to collection.
    """

    staging_path = os.path.abspath(staging_path)

    collection_path = os.path.join(staging_path, collection_name)
    collection_file_path = os.path.join(collection_path, '.dtool-collection')

    if os.path.isdir(collection_path):
        if not os.path.isfile(collection_file_path):
            raise(ValueError('Path exists but is not a collection'))
        else:
            return collection_path

    os.mkdir(collection_path)

    collection_uuid = str(uuid.uuid4())

    collection_info = {'uuid': collection_uuid}

    with open(collection_file_path, 'w') as fh:
        json.dump(collection_info, fh)

    return collection_path


def is_collection(path):
    """Return True if path is a collection.

    :param path: path to test
    :returns: True if path is a collection, False othewise
    """

    path = os.path.abspath(path)

    collection_file_path = os.path.join(path, '.dtool-collection')

    return os.path.isfile(collection_file_path)
