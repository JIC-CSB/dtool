"""Module wrapping tar and gzip."""

import os
import subprocess
import tarfile


def intialise_tar_archive(archive_path, fname_to_add):
    """Initialise a tar archive.

    :param archive_path: path to the directory to archive
    :param rel_fpath_to_add: relative path to file in the archive directory to
                             add to tar archive
    :returns:
    """
    archive_path = os.path.abspath(archive_path)
    working_dir, dataset_name = os.path.split(archive_path)

    tar_output_filename = dataset_name + ".tar"
    path_to_add = os.path.join(dataset_name, fname_to_add)

    cmd = ["tar", "-cf", tar_output_filename, path_to_add]
    subprocess.call(cmd, cwd=working_dir)

    abs_path_of_added = os.path.join(working_dir, path_to_add)

    return path_to_add, os.stat(abs_path_of_added).st_size


def append_to_tar_archive(archive_path, fname_to_add):
    """Initialise a tar archive.

    :param archive_path: path to the directory to archive
    :param rel_fpath_to_add: relative path to file in the archive directory to
                             add to tar archive
    :returns:
    """
    archive_path = os.path.abspath(archive_path)
    working_dir, dataset_name = os.path.split(archive_path)

    tar_output_filename = dataset_name + ".tar"
    path_to_add = os.path.join(dataset_name, fname_to_add)

    cmd = ["tar", "-rf", tar_output_filename, path_to_add]
    subprocess.call(cmd, cwd=working_dir)

    abs_path_of_added = os.path.join(working_dir, path_to_add)

    return path_to_add, os.stat(abs_path_of_added).st_size


def create_archive(path):
    """Create archive from path using tar.

    :param path: path to archive in staging area
    :returns: path to created tarball
    """

    path = os.path.abspath(path)
    staging_path, dataset_name = os.path.split(path)

    tar_output_filename = dataset_name + '.tar'

    dataset_info_path, _ = intialise_tar_archive(path, ".dtool-dataset")
    readme_path, _ = append_to_tar_archive(path, "README.yml")
    manifest_path, _ = append_to_tar_archive(path, "manifest.json")

    import json
    with open(os.path.join(path, "manifest.json")) as fh:
        manifest = json.load(fh)
    for entry in manifest["file_list"]:
        rel_path = os.path.join("archive", entry["path"])
        p, _ = append_to_tar_archive(path, rel_path)

    tar_output_path = os.path.join(staging_path, tar_output_filename)
    tar_output_path = os.path.abspath(tar_output_path)

    return tar_output_path


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
