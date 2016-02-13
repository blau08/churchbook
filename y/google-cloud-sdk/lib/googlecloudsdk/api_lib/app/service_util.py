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

"""Utilities for dealing with service resources."""

from googlecloudsdk.core import exceptions
from googlecloudsdk.core.util import text


class ServiceValidationError(exceptions.Error):
  pass


class ServicesNotFoundError(exceptions.Error):

  @classmethod
  def FromServiceLists(cls, requested_services, all_services):
    """Format a ServiceNotFoundError.

    Args:
      requested_services: list of str, IDs of services that were not found.
      all_services: list of str, IDs of all available services

    Returns:
      ServicesNotFoundError, error with properly formatted message
    """
    return cls(
        'The following {0} not found: [{1}]\n\n'
        'All services: [{2}]'.format(
            text.Pluralize(len(requested_services), 'service was',
                           plural='services were'),
            ', '.join(requested_services),
            ', '.join(all_services)))


class Service(object):
  """Value class representing a service resource."""

  def __init__(self, project, id_, split=None):
    self.project = project
    self.id = id_
    self.split = split or {}

  def __eq__(self, other):
    return (type(other) is Service and
            self.project == other.project and self.id == other.id)

  def __ne__(self, other):
    return not self == other

  @classmethod
  def FromResourcePath(cls, path):
    parts = path.split('/')
    if len(parts) != 2:
      raise ServiceValidationError('[{0}] is not a valid resource path. '
                                   'Expected <project>/<service>.')
    return cls(*parts)

  # TODO(b/25662075): convert to use functools.total_ordering
  def __lt__(self, other):
    return (self.project, self.id) < (other.project, other.id)

  def __le__(self, other):
    return (self.project, self.id) <= (other.project, other.id)

  def __gt__(self, other):
    return (self.project, self.id) > (other.project, other.id)

  def __ge__(self, other):
    return (self.project, self.id) >= (other.project, other.id)

  def __repr__(self):
    return '{0}/{1}'.format(self.project, self.id)


def _ValidateServicesAreSubset(filtered_services, all_services):
  not_found_services = set(filtered_services) - set(all_services)
  if not_found_services:
    raise ServicesNotFoundError.FromServiceLists(not_found_services,
                                                 all_services)


def ParseServiceResourcePaths(paths, project):
  """Parse the list of resource paths specifying services.

  Args:
    paths: The list of resource paths by which to filter.
    project: The current project. Used for validation.

  Returns:
    list of Service

  Raises:
    ServiceValidationError: If not all services are valid resource paths for the
      current project.
  """
  if not all('/' in path for path in paths):
    raise ServiceValidationError('If you provide any resource path as an '
                                 'argument, all arguments must be resource '
                                 'paths.')
  services = map(Service.FromResourcePath, paths)

  for service in services:
    if service.project and service.project != project:
      raise ServiceValidationError(
          'All services must be in the current project.')
    service.project = project
  return services


def GetMatchingServices(all_services, args_services, project):
  """Return a list of services to act on based on user arguments.

  Args:
    all_services: list of Service representing all services in the project.
    args_services: list of string, service ID/resource paths to filter for.
      If empty, match all services.
    project: the current project ID

  Returns:
    list of matching Service

  Raises:
    ServiceValidationError: If an improper combination of arguments is given
      (ex. a resource path with an incorrect project is provided).
  """
  if not args_services:
    args_services = [s.id for s in all_services]
  # If resource path(s) are given, use those. Otherwise, filter all available
  # services based on the given service specifiers.
  if any('/' in service for service in args_services):
    services = ParseServiceResourcePaths(args_services, project)
    _ValidateServicesAreSubset([s.id for s in services],
                               [s.id for s in all_services])
  else:
    _ValidateServicesAreSubset(args_services, [s.id for s in all_services])
    services = [s for s in all_services if s.id in args_services]
  return services


def ParseTrafficAllocations(args_allocations, split_method):
  """Parses the user-supplied allocations into a format acceptable by the API.

  Args:
    args_allocations: The raw allocations passed on the command line. A dict
      mapping version_id (str) to the allocation (float).
    split_method: Whether the traffic will be split by ip or cookie. This
      affects the format we specify the splits in.

  Returns:
    A dict mapping version id (str) to traffic split (float).
  """
  # Splitting by IP allows 2 decimal places, splitting by cookie allows 3.
  max_decimal_places = 2 if split_method == 'ip' else 3
  sum_of_splits = sum([float(s) for s in args_allocations.values()])

  allocations = {}
  for version, split in args_allocations.iteritems():
    allocation = float(split) / sum_of_splits
    allocation = round(allocation, max_decimal_places)
    allocations[version] = allocation

  # The API requires that these sum to 1.0. This is hard to get exactly correct,
  # (think .33, .33, .33) so we take our difference and subtract it from a
  # random element.
  total_splits = sum(allocations.values())
  difference = total_splits - 1.0

  allocations[sorted(allocations.keys())[0]] -= difference
  return allocations
