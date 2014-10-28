# -*- coding: utf-8 -*-
from . import utils


class Message(utils.CaseInsensitiveDict):
    """Handle both Responses and Events with the same api:

    ..
        >>> resp = Message({'Response': 'Follows'}, 'Response body')
        >>> event = Message({'Event': 'MeetmeEnd', 'Meetme': '4242'})

    Responses:

    .. code-block:: python

        >>> bool(resp.success)
        True
        >>> resp
        <Message Response='Follows' content='Response body'>
        >>> print(resp.content)
        Response body
        >>> for line in resp.iter_lines():
        ...     print(resp.content)
        Response body

    Events:

    .. code-block:: python

        >>> print(event['meetme'])
        4242
        >>> print(event.meetme)
        4242
        >>> event.unknown_header
        ''

    """

    quoted_keys = ['result']

    def __init__(self, headers, content=''):
        super(Message, self).__init__(headers, content=content)
        self.manager = None,

    @property
    def id(self):
        if 'commandid' in self:
            return self['commandid']
        elif 'actionid' in self:
            return self['actionid']
        return None

    @property
    def success(self):
        """return True if a response status is Success or Follows:

        .. code-block:: python

            >>> resp = Message({'Response': 'Success'})
            >>> print(resp.success)
            Success
            >>> resp['Response'] = 'Failed'
            >>> resp.success
            False
        """
        if 'event' in self:
            return True
        status = self['response']
        if status in ('Success', 'Follows'):
            return 'Success'
        return False

    def __repr__(self):
        message = ' '.join(['%s=%r' % i for i in sorted(self.items())])
        return '<Message {0}>'.format(message)

    def iter_lines(self):
        """Iter over response body"""
        for line in self.content.split('\n'):
            yield line

    @classmethod
    def from_line(cls, line):
            mlines = line.split(utils.EOL)
            headers = {}
            content = ''
            has_body = ('Response: Follows', 'Response: Fail')
            if mlines[0].startswith(has_body):
                content = mlines.pop()
                while not content and mlines:
                    content = mlines.pop()
            for mline in mlines:
                if ': ' in mline:
                    k, v = mline.split(': ', 1)
                    if k.lower() in cls.quoted_keys:
                        v = utils.unquote(v).strip()
                    if k in headers:
                        o = headers.setdefault(k, [])
                        if not isinstance(o, list):
                            o = [o]
                        o.append(v)
                        headers[k] = o
                    else:
                        headers[k] = v
            if 'Event' in headers or 'Response' in headers:
                return cls(headers, content)
