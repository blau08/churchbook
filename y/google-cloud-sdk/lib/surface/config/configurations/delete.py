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

"""Command to delete named configuration."""

from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core import named_configs
from googlecloudsdk.core.console import console_io


class Delete(base.SilentCommand):
  """Deletes a named configuration."""

  detailed_help = {
      'DESCRIPTION': """\
          {description} You cannot delete a configuration that is active, even
          when overridden with the --configuration flag.  To delete the current
          active configuration, first `gcloud config configurations activate`
          another one.

          See `gcloud topic configurations` for an overview of named
          configurations.
          """,
      'EXAMPLES': """\
          To delete named configuration, run:

            $ {command} my_config

          To delete several configurations, run:

            $ {command} my_config1 my_config2

          To list get a list of existing configurations, run:

            $ gcloud config configurations list
          """,
  }

  @staticmethod
  def Args(parser):
    """Adds args for this command."""
    parser.add_argument(
        'configuration_names',
        nargs='+',
        help=('Configuration names to delete, '
              'can not be currently active configuration.'))

  def Run(self, args):
    # Fail the delete operation when we're attempting to delete the
    # active config.
    current_config = named_configs.GetNameOfActiveNamedConfig()
    if current_config in args.configuration_names:
      raise named_configs.NamedConfigWriteError(
          'Deleting named configuration failed because configuration '
          '[{0}] is set as active.  Use `gcloud config configurations '
          'activate` to change the active configuration.'.format(
              current_config))

    printer = console_io.ListPrinter(
        'The following configurations will be deleted:')
    printer.Print(args.configuration_names, output_stream=log.status)
    console_io.PromptContinue(default=True, cancel_on_no=True)

    for configuration_name in args.configuration_names:
      named_configs.DeleteNamedConfig(configuration_name)
      log.DeletedResource(configuration_name)
