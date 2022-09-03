from time import sleep
import test


def test_start_gitea():
    assert test.start_gitea() == True
def test_user_added():
    sleep(5)
    assert test.user_is_here('user1') == True
    test.stop_gitea()