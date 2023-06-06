import json

import navak_config.config as config


def load_roles():
    """
        this function return all roles from json conf file

    :return: dict(Roles)
    """
    json_path = (config.BASE_DIR / "navak_config" / "roles.json")
    with open(file=json_path, encoding="utf-8", mode="r") as fp:
        j = json.loads(fp.read())
        return j["navak_roles"]


def load_education():
    """
        this function return all education Degrees

    :return: dict(Education)
    """
    json_path = (config.BASE_DIR / "navak_config" / "education.json")
    with open(file=json_path, mode="r", encoding="utf-8") as fp:
        j = json.loads(fp.read())
        return j["navak_education"]


def load_work_position():
    """
        this function return all work position

    :return: dict(work position)
    """
    json_path = (config.BASE_DIR / "navak_config" / "WorkPosition.json")
    with open(file=json_path, mode="r", encoding="utf-8") as fp:
        j = json.loads(fp.read())
        return j["navak_work_position"]
