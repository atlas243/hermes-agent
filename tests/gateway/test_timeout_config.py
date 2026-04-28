from gateway.run import _resolve_timeout_config_for_chat


def test_resolve_timeout_config_for_chat_uses_channel_override():
    user_config = {
        "timeout": {"max_ceiling": 600, "idle_threshold": 300},
        "channels": {
            "-1003746885691": {
                "name": "Atlas - Development",
                "timeout": {"max_ceiling": 7200, "idle_threshold": 300},
            }
        },
    }

    ceiling, idle = _resolve_timeout_config_for_chat(user_config, "-1003746885691")

    assert ceiling == 7200
    assert idle == 300


def test_resolve_timeout_config_for_chat_falls_back_to_global_timeout():
    user_config = {
        "timeout": {"max_ceiling": 600, "idle_threshold": 300},
        "channels": {},
    }

    ceiling, idle = _resolve_timeout_config_for_chat(user_config, "-1000000000000")

    assert ceiling == 600
    assert idle == 300
