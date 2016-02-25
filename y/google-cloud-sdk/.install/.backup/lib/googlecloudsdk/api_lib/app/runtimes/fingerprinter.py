# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Package containing fingerprinting for all runtimes.
"""

from googlecloudsdk.api_lib.app import ext_runtime
from googlecloudsdk.api_lib.app.ext_runtimes import fingerprinting
from googlecloudsdk.api_lib.app.runtimes import aspnet
from googlecloudsdk.api_lib.app.runtimes import go
from googlecloudsdk.api_lib.app.runtimes import java
from googlecloudsdk.api_lib.app.runtimes import python
from googlecloudsdk.api_lib.app.runtimes import python_compat
from googlecloudsdk.api_lib.app.runtimes import ruby
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log

RUNTIMES = [
    # Note that ordering of runtimes here is very important and changes to the
    # relative positions need to be tested carefully.
    go,  # Go's position is relatively flexible due to its orthogonal nature.
    ruby,
    ext_runtime.CoreRuntimeLoader('nodejs', 'Node.js', ['nodejs', 'custom']),
    java,
    python_compat,
    aspnet,
    python,  # python is last because it passes if there are any .py files.
]


class UnidentifiedDirectoryError(exceptions.Error):
  """Raised when GenerateConfigs() can't identify the directory."""

  def __init__(self, path):
    """Constructor.

    Args:
      path: (basestring) Directory we failed to identify.
    """
    super(UnidentifiedDirectoryError, self).__init__(
        'Unrecognized directory type: [{0}]'.format(path))
    self.path = path


class ConflictingConfigError(exceptions.Error):
  """Property in app.yaml conflicts with params passed to fingerprinter."""


class AlterConfigFileError(exceptions.Error):
  """Error when attempting to update an existing config file (app.yaml)."""

  def __init__(self, inner_exception):
    super(AlterConfigFileError, self).__init__(
        'Could not alter app.yaml due to an internal error:\n{0}\n'
        'Please update app.yaml manually.'.format(inner_exception))


def IdentifyDirectory(path, params=None):
  """Try to identify the given directory.

  As a side-effect, if there is a config file in 'params' with a runtime of
  'custom', this sets params.custom to True.

  Args:
    path: (basestring) Root directory to identify.
    params: (fingerprinting.Params or None) Parameters passed through to the
      fingerprinters.  Uses defaults if not provided.

  Returns:
    (fingerprinting.Module or None) Returns a module if we've identified it,
    None if not.
  """
  if not params:
    params = fingerprinting.Params()

  # Parameter runtime has precedence
  if params.runtime:
    specified_runtime = params.runtime
  elif params.appinfo:
    specified_runtime = params.appinfo.GetEffectiveRuntime()
  else:
    specified_runtime = None

  if specified_runtime == 'custom':
    params.custom = True

  for runtime in RUNTIMES:

    # If we have an app.yaml, don't fingerprint for any runtimes that don't
    # allow the runtime name it specifies.
    if (specified_runtime and runtime.ALLOWED_RUNTIME_NAMES and
        specified_runtime not in runtime.ALLOWED_RUNTIME_NAMES):
      log.info('Not checking for [%s] because runtime is [%s]' %
               (runtime.NAME, specified_runtime))
      continue

    configurator = runtime.Fingerprint(path, params)
    if configurator:
      return configurator
  return None


def GenerateConfigs(path, params=None, config_filename=None):
  """Generate all config files for the path into the current directory.

  As a side-effect, if there is a config file in 'params' with a runtime of
  'custom', this sets params.custom to True.

  Args:
    path: (basestring) Root directory to identify.
    params: (fingerprinting.Params or None) Parameters passed through to the
      fingerprinters.  Uses defaults if not provided.
    config_filename: (str or None) Filename of the config file (app.yaml).

  Raises:
    UnidentifiedDirectoryError: No runtime module matched the directory.
    ConflictingConfigError: Current app.yaml conflicts with other params.

  Returns:
    (callable()) Function to remove all generated files (if desired).
  """
  if not params:
    params = fingerprinting.Params()

  config = params.appinfo
  # An app.yaml exists, results in a lot more cases
  if config and not params.deploy:
    # Enforce --custom
    if not params.custom:
      raise ConflictingConfigError(
          'Configuration file already exists. This command generates an '
          'app.yaml configured to run an application on Google App Engine. '
          'To create the configuration files needed to run this '
          'application with docker, try `gcloud preview app gen-config '
          '--custom`.')
    # Check that current config is for MVM
    if not config.IsVm():
      raise ConflictingConfigError(
          'gen-config is only supported for App Engine Managed VMs.  Please '
          'use "vm: true" in your app.yaml if you would like to use Managed '
          'VMs to run your application.')
    # Check for conflicting --runtime and runtime in app.yaml
    if (config.GetEffectiveRuntime() != 'custom' and params.runtime is not None
        and params.runtime != config.GetEffectiveRuntime()):
      raise ConflictingConfigError(
          '[{0}] contains "runtime: {1}" which conficts with '
          '--runtime={2}.'.format(config_filename, config.GetEffectiveRuntime(),
                                  params.runtime))

  module = IdentifyDirectory(path, params)
  if not module:
    raise UnidentifiedDirectoryError(path)

  return module.GenerateConfigs()