import datetime
import re


def load():
    """ Loads the jclouds plugin. """
    return Jclouds()


class Jclouds:
    """ Customizes the jclouds review dashboard and provides
        custom pull request and comment parsers. """

    def __init__(self):
        """ Configure the view and the repos to be scanned """
        self.config = {
            'title': 'jclouds Code Review Dashboard',
            'headers': { 'left': 'Need More Work',
                         'middle': 'Jenkins Happy',
                         'right': 'Someone Likes!' },
            'template': 'jclouds.html',
        }
        self.repos = self._repos()

    def parse_pull(self, pull, data):
        """ Parse the pull request object and populate any additional
            data that is going to be accessed when rendering the dashboard. """
        data['obsolete'] = data['old'] >= 180
        data['likes'] = 0
        data['oks'] = []
        data['fails'] = []
        data['unstable'] = []

    def parse_comment(self, comment, data):
        """ Parse the comment object and populate any additional
            data that is going to be accessed when rendering the dashboard. """
        created = datetime.datetime.strptime(comment['created_at'],
                                             '%Y-%m-%dT%H:%M:%SZ')
        if self._has(comment, ['\+1', 'lgtm']):
            data['likes'] = data['likes'] + 1
        if self._has(comment, ['SUCCESS']):
            data['oks'].append(created)
        if self._has(comment, ['FAILURE']):
            data['fails'].append(created)
        if self._has(comment, ['UNSTABLE']):
            data['unstable'].append(created)

    def classify(self, pull):
        """ Invoked once the pull request has been completely parsed.
            This method returns the column where the pull request must appear. """
        likes = pull['likes']
        oks = sorted(pull['oks'], reverse=True)
        fails = sorted(pull['fails'], reverse=True)
        unstable = sorted(pull['unstable'], reverse=True)
        pull['total-oks'] = len(oks)
        pull['total-fails'] = len(fails)
        pull['total-unstable'] = len(unstable)

        if likes > 0:
            return 'right'
        elif pull['build_status'] == 'success':
            return 'middle'
        elif pull['build_status'] == 'failure':
            return 'left'
        elif len(oks) == 0:
            return 'left'
        elif len(fails) == 0:
            return 'middle'
        elif oks[0] > fails[0]:
            return 'middle'
        else:
            return 'left'

    def _has(self, comment, patterns):
        for pattern in patterns:
            if re.search(pattern, comment["body"]):
                return True
        return False

    def _repos(self):
        return ["https://api.github.com/repos/jclouds/jclouds",
                "https://api.github.com/repos/jclouds/jclouds-chef",
                "https://api.github.com/repos/jclouds/jclouds-cli",
                "https://api.github.com/repos/jclouds/jclouds-karaf",
                "https://api.github.com/repos/jclouds/jclouds-labs",
                "https://api.github.com/repos/jclouds/jclouds-labs-google",
                "https://api.github.com/repos/jclouds/jclouds-labs-aws",
                "https://api.github.com/repos/jclouds/jclouds-labs-openstack",
                "https://api.github.com/repos/jclouds/jclouds-examples",
                "https://api.github.com/repos/jclouds/jclouds-site"]
