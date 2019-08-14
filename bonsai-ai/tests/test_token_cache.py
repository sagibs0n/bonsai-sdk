# Copyright (C) 2019 Microsoft, Inc.

from bonsai_ai.token_cache import BonsaiTokenCache


def test_initialize_empty_cache(temp_home_directory_read_only):
    cache = BonsaiTokenCache()
    assert cache._cache == {}


def test_initialize_cache_from_file(temp_aad_cache):
    cache = BonsaiTokenCache()
    assert isinstance(cache._cache['BONSAI_WORKSPACES'], dict)
    assert cache._cache['BONSAI_WORKSPACES']['https://foo.bons.ai'] == 'foo'
    assert cache._cache['AccessToken'] == 'access'
    assert cache._cache['RefreshToken'] == 'refresh'


def test_get_workspace(temp_aad_cache):
    url_1 = 'https://foo.bons.ai'
    url_2 = 'https://bar.bons.ai'
    workspace_1 = 'foo'
    workspace_2 = 'bar'

    # get workspace that was already in cache   
    cache = BonsaiTokenCache()
    assert cache.get_workspace(url_1) == workspace_1
    assert not cache.has_state_changed

    # add second workspace
    cache.add_workspace(url_2, workspace_2)
    assert cache.has_state_changed
    assert cache.get_workspace(url_2) == workspace_2

    # overwrite initial workspace
    new_workspace = 'baz'
    cache.add_workspace(url_1, new_workspace)
    assert cache.get_workspace(url_1) == new_workspace

    # cache should have two entries
    workspace_dict_key = 'BONSAI_WORKSPACES'
    assert cache._cache.get(workspace_dict_key)
    assert len(cache._cache[workspace_dict_key]) == 2
    

def test_write_cache_to_file(temp_aad_cache):
    url = 'https://foo.bons.ai'
    new_workspace = 'bar'
    cache_1 = BonsaiTokenCache()
    cache_1.add_workspace(url, new_workspace)
    cache_1.write_cache_to_file()

    cache_2 = BonsaiTokenCache()
    assert not cache_1.has_state_changed
    assert cache_2.get_workspace(url) == new_workspace
