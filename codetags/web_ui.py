# -*- coding: utf-8 -*-

from trac.core import Component, implements
from trac.env import IEnvironmentSetupParticipant
from trac.perm import IPermissionRequestor
from trac.web.chrome import INavigationContributor, ITemplateProvider, \
                            add_stylesheet
from trac.web.api import IRequestHandler
from trac.util.html import html
from trac.versioncontrol.api import RepositoryManager

from codetags.indexer import TagIndexer


class CodetagsPlugin(Component):
    implements(IEnvironmentSetupParticipant, INavigationContributor,
               IPermissionRequestor, IRequestHandler, ITemplateProvider)

    # IEnvironmentSetupParticipant methods

    def environment_created(self):
        self.upgrade_environment()

    def environment_needs_upgrade(self, db=None):
        repo = RepositoryManager(self.env).get_repository(None)
        indexer = TagIndexer(self.env, repo)

        if indexer.get_cache_revision() is None:
            return True
        else:
            return False

    def upgrade_environment(self, db=None):
        repo = RepositoryManager(self.env).get_repository(None)
        indexer = TagIndexer(self.env, repo)

        # Force an update of the taglist cache
        indexer.update_cache()

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'codetags'

    def get_navigation_items(self, req):
        if 'CODETAGS_VIEW' in req.perm:
            yield 'mainnav', 'codetags', \
                  html.a("Code Tags", href=req.href.codetags())

    # IPermissionRequestor methods

    def get_permission_actions(self):
        return ['CODETAGS_VIEW']

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info == '/codetags'

    def process_request(self, req):
        req.perm.require('CODETAGS_VIEW')

        folders = []
        for repo in RepositoryManager(self.env).get_real_repositories():
            indexer = TagIndexer(self.env, repo)
            folders.append(indexer.get_taglist())

        add_stylesheet(req, 'codetags/style.css')
        data = {'folders': folders}
        return 'codetags.html', data, None

    # ITemplateProvider methods

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('codetags', resource_filename(__name__, 'htdocs'))]
