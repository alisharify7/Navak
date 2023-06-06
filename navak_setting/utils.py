import re


class UserTag():
    """
        Base Class For  verify users Tags
    """
    tag = None

    def __init__(self, UserTag: str):
        self.tag = UserTag

    def is_Verify(self):
        """
            this method verify user tag is valid
        :return: True if user tag is valid otherwise False
        """

        if re.search(r"^[\w]{4,128}$", self.tag):
            return True
        else:
            return False
