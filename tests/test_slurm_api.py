"""Test the slurm module API."""


def test_generate_slurm_submission_script():

    from dtool.slurm import generate_slurm_script

    job_parameters = {'n_cores': 8, 'partition': 'rg-sv'}
    command_string = "arctool archive compress -c 8 /tmp/staging/mytar.tar"
    actual_script = generate_slurm_script(command_string,
                                          job_parameters)

    actual = actual_script.split('\n')[-1]

    expected = 'arctool archive compress -c 8 /tmp/staging/mytar.tar'

    assert expected == actual, (expected, actual)
