from bot import LunaBot, run, settings
run(LunaBot(**{
    "command_prefix": ["-", "."] if settings.UseBetaBot else ["!luna ", "Luna ", ".", ">"],
    "owner_id": 104223387043266560,
    "shard_count": 3,
    "shard_ids": [0,1,2]
}))