"""
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import re
import os
import imp
import uuid
import inspect


# ------------------------------------------------------------------------------
class SimpleFactory(object):
    """
    This is a simple 'getting started with factories' module. It offers a
    simple factory mechanism with a few basic features:

        * Recursive folder searching for plugins
        * Simple function call for accessing the plugin list

    This is typically enough to get started, but its worth noting that
    the following (generally quite useful nice-to-have) features are
    absent:

        * Ability to specify a plugin identifer
        * Ability to access a plugin by identifier
        * Removing plugins from the factory
        * Plugin sorted in user-defined priority

    Finally, some restrictions based on this factory:

        * Files containing plugins must not contain relative imports
        * Plugins must not be in the same file as the abstract

    Many of these restrictions or missing features are relatively straight
    forward to implement, but as a starting point to getting used to - or
    experimenting with the plugin/factory approach this should suffice.
    """
    _PY_CHECK = re.compile('[a-zA-Z].*\.py$')
    
    # --------------------------------------------------------------------------
    def __init__(self, abstract, paths):

        # -- Store our incoming variables
        self._paths = paths
        self._abstract = abstract

        # -- Store a list of plugins
        self.plugins = list()

        # -- Any paths we're giving during the init we should
        # -- register
        for path in paths:
            self.register_path(path)

    # --------------------------------------------------------------------------
    # noinspection PyBroadException
    def register_path(self, path):
        """
        Looks for plugins in any python files found on the given
        path

        :param path: Absolute folder location

        :return: Count of plugins registered
        """
        current_plugin_count = len(self.plugins)

        filepaths = list()

        # -- Collate all our valid files in an initial pass. This could
        # -- be done in situ, but for the sake of clarity its done up-front
        for root, _, files in os.walk(path):
            for filename in files:

                # -- skip any private or structural files, along with
                # -- any files which are not py files
                if not self._PY_CHECK.match(filename):
                    continue

                filepaths.append(
                    os.path.join(
                        root,
                        filename
                    ),
                )

        # -- Start cycling over the files we have found and look inside
        # -- for plugins
        for filepath in filepaths:

            # -- We have no control over what we load, so we wrap
            # -- this is a try/except
            try:

                # -- import the file under a unique namespace
                _module = imp.load_source(
                    str(uuid.uuid4()),
                    filepath
                )

                # -- Look for implementations of the abstract
                for item_name in dir(_module):

                    item = getattr(
                        _module,
                        item_name,
                    )

                    # -- If this bases off the abstract, we should store it
                    if inspect.isclass(item):
                        if issubclass(item, self._abstract):
                            self.plugins.append(item)

            # -- We keep the exception type explitely broad as it
            # -- is completely out of our control what might be being
            # -- imported
            except BaseException:
                pass

        # -- Return the amount of plugins which have
        # -- been loaded during this registration pass
        return len(self.plugins) - current_plugin_count
