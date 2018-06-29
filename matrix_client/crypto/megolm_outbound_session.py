from datetime import datetime, timedelta

from olm import OutboundGroupSession


class MegolmOutboundSession(OutboundGroupSession):

    """Outbound group session aware of the users it is shared with.

    Also remembers the time it was created and the number of messages it has encrypted,
    in order to know if it needs to be rotated.

    Args:
        max_age (datetime.timedelta): Optional. The maximum time the session should
            exist. Default to one week if not present.
        max_messages (int): Optional. The maximum number of messages that should be sent.
            A new message in considered sent each time there is a call to ``encrypt``.
            Default to 100 if not present.
    """

    def __init__(self, max_age=None, max_messages=None):
        self.devices = set()
        if max_age:
            self.max_age = timedelta(milliseconds=max_age)
        else:
            self.max_age = timedelta(days=7)
        self.max_messages = max_messages or 100
        self.creation_time = datetime.now()
        self.message_count = 0
        super(MegolmOutboundSession, self).__init__()

    def __new__(cls, **kwargs):
        return super(MegolmOutboundSession, cls).__new__(cls)

    def add_device(self, device_id):
        """Adds a device the session is shared with."""
        self.devices.add(device_id)

    def add_devices(self, device_ids):
        """Adds devices the session is shared with.

        Args:
            device_ids (iterable): An iterable of device ids, preferably a set.
        """
        self.devices.update(device_ids)

    def should_rotate(self):
        """Wether the session should be rotated.

        Returns:
            True if it should, False if not.
        """
        if self.message_count >= self.max_messages or \
                datetime.now() - self.creation_time >= self.max_age:
            return True
        return False

    def encrypt(self, plaintext):
        self.message_count += 1
        return super(MegolmOutboundSession, self).encrypt(plaintext)
