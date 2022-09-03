import test


def test_user_added():
    test.start_gitea()
    token = test.get_user_token()
    assert test.user_is_here('user1') == True
    test.stop_gitea()