# -*- coding: utf-8 -*-
"""
    Indexer
"""
import fnmatch
import os
import posixpath
import re
import cPickle as pickle

from trac.util.text import to_unicode
from trac.versioncontrol.api import Changeset, Node, NoSuchNode


class TagIndexer(object):
    def __init__(self, env, repo):
        self.env = env
        self.repo = repo

        config = env.config['code-tags']
        self.tags = config.get('tags', ['XXX', 'TODO', 'FIXME'])
        self.scan_folders = config.getlist('scan_folders', '*')
        self.exclude_folders = config.getlist('exclude_folders', '')
        self.scan_files = config.getlist('scan_files', '*')
        self.exclude_files = config.getlist('exclude_files', '')
        self.enable_unicode = config.getbool('enable_unicode', True)

        p = []
        for word in self.tags:
            p.append(r'\b' + re.escape(word) + r'\b')
        self.tag_re = re.compile(r'(%s):?\s*(.*?)\s*$' % '|'.join(p))

        cdir = os.path.join(os.path.abspath(env.path), 'cache', 'codetags')
        if not os.path.exists(cdir):
            os.makedirs(cdir)
        self.cachedir = cdir

    def is_path_valid(self, path):
        """Determine whether the given path is valid path to scan."""
        for rule in self.scan_folders:
            if fnmatch.fnmatch(path, rule):
                return True

    def contains_valid_paths(self, node):
        if node.kind != Node.DIRECTORY:
            return True

        # Check if given node is a parent directory of the folders to scan
        for rule in self.scan_folders:
            subdirs = rule.split('/')
            for depth in range(0, len(subdirs)):
                subdir = '/'.join(subdirs[:depth + 1])
                if fnmatch.fnmatch(node.path, subdir):
                    return True

        return False

    def walk_repo(self, repo, rev):
        """Walks through the whole repository and yields all files
        matching the settings from the config.
        This method is just used for bootstrapping the cache."""

        def do_walk(path, scan):
            node = repo.get_node(path, rev)
            if node.kind == Node.DIRECTORY:
                # Skip excluded directories (and all of their subdirectories)
                for rule in self.exclude_folders:
                    if fnmatch.fnmatch(node.path, rule):
                        return

                do_scan = self.is_path_valid(node.path)
                for subnode in node.get_entries():
                    if self.contains_valid_paths(subnode):
                        for result in do_walk(subnode.path, do_scan):
                            yield result
            elif scan:
                fname = posixpath.basename(node.path)
                for rule in self.exclude_files:
                    if fnmatch.fnmatch(fname, rule):
                        return
                for rule in self.scan_files:
                    if fnmatch.fnmatch(fname, rule):
                        yield node.path
                        return

        return do_walk('/', True)

    def load_from_cache(self):
        """Load the tags from the cache."""
        fn = os.path.join(self.cachedir, 'tags')
        if not os.path.exists(fn):
            return {}
        f = file(fn, 'rb')
        result = pickle.load(f)
        f.close()
        return result

    def get_youngest_rev(self):
        """Work around a bug in Trac's CachedRepository class which causes
        Subversion revision 0 to be converted into None."""
        rev = self.repo.get_youngest_rev()
        if rev is None and hasattr(self.repo, 'repos'):
            rev = self.repo.repos.get_youngest_rev()
        return rev

    def save_to_cache(self, folders):
        """Saves changes to the cache."""
        # update cache revision
        f = file(os.path.join(self.cachedir, 'revision'), 'wb')
        pickle.dump(self.get_youngest_rev(), f)
        f.close()
        # cache tree
        f = file(os.path.join(self.cachedir, 'tags'), 'wb')
        pickle.dump(folders, f, 2)
        f.close()

    def get_cache_revision(self):
        """Returns the revision of the cache."""
        fn = os.path.join(self.cachedir, 'revision')
        if not os.path.exists(fn):
            return None
        f = file(fn, 'rb')
        rev = pickle.load(f)
        f.close()
        return rev

    def get_changed_files(self):
        """Returns the files which require a rescan from the
        last cached revision to the current one."""
        cur_rev = self.get_youngest_rev()
        cached_rev = self.get_cache_revision()
        # special case: scan all files
        if cached_rev is None:
            for fn in self.walk_repo(self.repo, cur_rev):
                yield fn, cur_rev
            return
        # special case: scan no file
        elif not self.repo.rev_older_than(cached_rev, cur_rev):
            return
        # otherwise yield changed files
        changes = set()
        rev = cached_rev
        while self.repo.rev_older_than(rev, cur_rev):
            rev = self.repo.next_rev(rev)
            cset = self.repo.get_changeset(rev)
            for path, kind, change, base_path, base_rev in cset.get_changes():
                if kind == Node.DIRECTORY:
                    continue
                folder = posixpath.dirname(path)
                if not self.is_path_valid(folder):
                    continue
                if change == Changeset.MOVE:
                    changes.add(base_path)
                fname = posixpath.basename(path)
                for rule in self.exclude_files:
                    if fnmatch.fnmatch(fname, rule):
                        break
                else:
                    for rule in self.scan_files:
                        if fnmatch.fnmatch(fname, rule):
                            changes.add(path)
                            break
        for n in changes:
            yield n, cur_rev

    def get_new_tags(self):
        """Parses the text to load the new tags."""
        files = {}
        for fn, rev in self.get_changed_files():
            try:
                node = self.repo.get_node(fn, rev)
            except NoSuchNode:
                # Deal with deleted files by appending an empty file node, to
                # flush the cache for this file if there's any.
                files[fn] = [{'path': fn}]
                continue

            f = node.get_content()
            content = f.read()
            if self.enable_unicode:
                content = to_unicode(content)
            lines = content.splitlines()
            if hasattr(f, 'close'):
                f.close()
            for idx, line in enumerate(lines):
                m = self.tag_re.search(line)
                if m is not None:
                    files.setdefault(node.path, []).append({
                        'path': node.path,
                        'tag': m.group(1),
                        'line': idx + 1,
                        'text': m.group(2)
                    })

            # File was returned by get_changed_files, but no tags where found.
            # Thus return an empty file node instead (to flush cache for this
            # file if there's any).
            if node.path not in files:
                files[node.path] = [{'path': node.path}]

        return files

    def update_cache(self):
        """Updates the cache."""
        files = self.load_from_cache()
        # update with new files
        new_tags = self.get_new_tags()
        if new_tags:
            for path, matches in new_tags.iteritems():
                if len(matches) == 1 and 'tag' not in matches[0]:
                    # Clean up files without tags in the latest revision
                    if path in files:
                        del files[path]
                else:
                    files[path] = matches
        # Save when things have changed or no previous cache existed
        if new_tags or files == {}:
            self.save_to_cache(files)

        return files

    def get_taglist(self):
        """Returns a list of active tags and updates cache."""
        files = self.update_cache()
        # sort folders and create dict for hdf
        folders = {}
        items = files.items()
        items.sort()
        for filepath, matches in items:
            folders.setdefault(posixpath.dirname(filepath), []).extend(
                matches)
        items = folders.items()
        items.sort()
        result = []
        for path, matches in items:
            result.append({
                'href': self.env.href.browser(path),
                'path': path,
                'matches': [{
                    'class': 'tag-%s' % m['tag'].lower(),
                    'href': '%s#L%d' % (
                        self.env.href.browser(m['path']),
                        m['line']
                    ),
                    'basename': posixpath.basename(m['path']),
                    'lineno': m['line'],
                    'tag': m['tag'],
                    'text': m['text']
                } for m in matches]
            })
        return result
