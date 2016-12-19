"""Module wrapping tar and gzip."""

import os
import subprocess


def create_archive(path):
    """Create archive from path using tar.

    :param path: path to archive in staging area
    :returns: path to created tarball
    """

    path = os.path.abspath(path)
    staging_path, dataset_name = os.path.split(path)

    tar_output_filename = dataset_name + '.tar'

    dataset_info_path = os.path.join(dataset_name, '.dtool-dataset')
    tar_dataset_info = ['tar', '-cf', tar_output_filename, dataset_info_path]
    subprocess.call(tar_dataset_info, cwd=staging_path)

    readme_path = os.path.join(dataset_name, 'README.yml')
    tar_readme = ['tar', '-rf', tar_output_filename, readme_path]
    subprocess.call(tar_readme, cwd=staging_path)

    manifest_path = os.path.join(dataset_name, 'manifest.json')
    tar_manifest = ['tar', '-rf', tar_output_filename, manifest_path]
    subprocess.call(tar_manifest, cwd=staging_path)

    exclude_manifest = '--exclude={}'.format(manifest_path)
    exclude_readme = '--exclude={}'.format(readme_path)
    exclude_dataset_info = '--exclude={}'.format(dataset_info_path)
    tar_remainder = ['tar',
                     exclude_manifest,
                     exclude_readme,
                     exclude_dataset_info,
                     '-rf',
                     tar_output_filename,
                     dataset_name]

    subprocess.call(tar_remainder, cwd=staging_path)

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
