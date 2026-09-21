from src.lockbox.process import is_process_running


def test_running_process():

    assert is_process_running("python.exe")


def test_nonexistent_process():

    assert not is_process_running(
        "definitely_not_a_real_application.exe"
    )