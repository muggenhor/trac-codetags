# -*- coding: utf-8 -*-
import os
from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.perm import IPermissionRequestor
from trac.web.chrome import INavigationContributor, ITemplateProvider, \
                            add_stylesheet
from trac.web.main import IRequestHandler
from trac.util import escape, Markup
from codetags.indexer import TagIndexer
from trac import __version__ as TracVersion
from pkg_resources import parse_version

class CodetagsPlugin(Component):
    implements(IEnvironmentSetupParticipant, INavigationContributor, \
               ITemplateProvider, IRequestHandler, IPermissionRequestor)

    # IEnvironmentSetupParticipant methods
    def environment_created(self):
        self.cache_exists = False
        self.upgrade_environment(self.env.get_db_cnx())

    def environment_needs_upgrade(self, db):
        repo = self.env.get_repository()
        indexer = TagIndexer(self.env, repo)

        if indexer.get_cache_revision() is None:
            return True
        else:
            return False

    def upgrade_environment(self, db):
        repo = self.env.get_repository()
        indexer = TagIndexer(self.env, repo)

        # Force an update of the taglist cache
        indexer.update_cache()

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        return 'codetags'
                
    def get_navigation_items(self, req):
        if not req.perm.has_permission('CODETAGS_VIEW'):
            return
        yield 'mainnav', 'codetags', Markup('<a href="%s">Code Tags</a>' \
                                    % escape(self.env.href.codetags()))

    # IPermissionRequestor methods
    def get_permission_actions(self):
        return ['CODETAGS_VIEW']

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info == '/codetags'
    
    def process_request(self, req):
        req.perm.assert_permission('CODETAGS_VIEW')
        repo = self.env.get_repository(authname=req.authname)
        indexer = TagIndexer(self.env, repo)
        folders = indexer.get_taglist()
        
        add_stylesheet(req, 'codetags/style.css')
        if parse_version(TracVersion) < parse_version('0.11'):
            req.hdf['folders'] = folders
            return 'codetags.cs', None
        else:
            data = {'folders': folders}
            return 'codetags.html', data, None

    # ITemplateProvider methods
    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('codetags', resource_filename(__name__, 'htdocs'))]
