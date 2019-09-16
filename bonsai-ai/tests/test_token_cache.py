# Copyright (C) 2019 Microsoft, Inc.

from bonsai_ai.token_cache import BonsaiTokenCache


def test_initialize_empty_cache(temp_home_directory_read_only):
    cache = BonsaiTokenCache()
    assert cache._cache == {}


def test_initialize_cache_from_file(temp_aad_cache):
    cache = BonsaiTokenCache()
    assert cache._cache['AccessToken'] == 'access'
    assert cache._cache['RefreshToken'] == 'refresh'
    

def test_write_cache_to_file(temp_aad_cache):
    url = 'https://foo.bons.ai'
    new_workspace = 'bar'
    cache_1 = BonsaiTokenCache()
    cache_1.write_cache_to_file()

    cache_2 = BonsaiTokenCache()
    assert not cache_1.has_state_changed
