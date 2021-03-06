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
"""Module for miscellaneous utility functions."""

import functools
import httplib
import pickle
import re

from googlecloudsdk.core import log
from googlecloudsdk.third_party.apis.iam.v1 import iam_v1_messages as msgs
from googlecloudsdk.third_party.apitools.base.py import exceptions


CREATE_KEY_TYPES = (msgs.CreateServiceAccountKeyRequest
                    .PrivateKeyTypeValueValuesEnum)
KEY_TYPES = (msgs.ServiceAccountKey.PrivateKeyTypeValueValuesEnum)
MANAGED_BY = (msgs.IamProjectsServiceAccountsKeysListRequest
              .KeyTypesValueValuesEnum)


def ManagedByFromString(managed_by):
  """Parses a string into a MANAGED_BY enum.

  MANAGED_BY is an enum of who manages a service account key resource. IAM
  will rotate any SYSTEM_MANAGED keys by default.

  Args:
    managed_by: A string representation of a MANAGED_BY. Can be one of *user*,
    *system* or *any*.

  Returns:
    A KeyTypeValueValuesEnum (MANAGED_BY) value.
  """
  if managed_by == 'user':
    return [MANAGED_BY.USER_MANAGED]
  elif managed_by == 'system':
    return [MANAGED_BY.SYSTEM_MANAGED]
  elif managed_by == 'any':
    return []
  else:
    return [MANAGED_BY.KEY_TYPE_UNSPECIFIED]


def KeyTypeFromString(key_str):
  """Parses a string into a KeyType enum.

  Args:
    key_str: A string representation of a KeyType. Can be either *p12* or
    *json*.

  Returns:
    A PrivateKeyTypeValueValuesEnum value.
  """
  if key_str == 'p12':
    return KEY_TYPES.TYPE_PKCS12_FILE
  elif key_str == 'json':
    return KEY_TYPES.TYPE_GOOGLE_CREDENTIALS_FILE
  else:
    return KEY_TYPES.TYPE_UNSPECIFIED


def KeyTypeToString(key_type):
  """Get a string version of a KeyType enum.

  Args:
    key_type: An enum of either KEY_TYPES or CREATE_KEY_TYPES.

  Returns:
    The string representation of the key_type, such that
    parseKeyType(keyTypeToString(x)) is a no-op.
  """
  if (key_type == KEY_TYPES.TYPE_PKCS12_FILE or
      key_type == CREATE_KEY_TYPES.TYPE_PKCS12_FILE):
    return 'p12'
  elif (key_type == KEY_TYPES.TYPE_GOOGLE_CREDENTIALS_FILE or
        key_type == CREATE_KEY_TYPES.TYPE_GOOGLE_CREDENTIALS_FILE):
    return 'json'
  else:
    return 'unspecified'


def KeyTypeToCreateKeyType(key_type):
  """Transforms between instances of KeyType enums.

  Transforms KeyTypes into CreateKeyTypes.

  Args:
    key_type: A ServiceAccountKey.PrivateKeyTypeValueValuesEnum value.

  Returns:
    A IamProjectsServiceAccountKeysCreateRequest.PrivateKeyTypeValueValuesEnum
    value.
  """
  # For some stupid reason, HTTP requests generates different enum types for
  # each instance of an enum in the proto buffer. What's worse is that they're
  # not equal to one another.
  if key_type == KEY_TYPES.TYPE_PKCS12_FILE:
    return CREATE_KEY_TYPES.TYPE_PKCS12_FILE
  elif key_type == KEY_TYPES.TYPE_GOOGLE_CREDENTIALS_FILE:
    return CREATE_KEY_TYPES.TYPE_GOOGLE_CREDENTIALS_FILE
  else:
    return CREATE_KEY_TYPES.TYPE_UNSPECIFIED


def KeyTypeFromCreateKeyType(key_type):
  """The inverse of *toCreateKeyType*."""
  if key_type == CREATE_KEY_TYPES.TYPE_PKCS12_FILE:
    return KEY_TYPES.TYPE_PKCS12_FILE
  elif key_type == CREATE_KEY_TYPES.TYPE_GOOGLE_CREDENTIALS_FILE:
    return KEY_TYPES.TYPE_GOOGLE_CREDENTIALS_FILE
  else:
    return KEY_TYPES.TYPE_UNSPECIFIED


def CatchServiceAccountErrors(func):
  """Decorator to automatically manage HTTP errors related to api calls."""

  @functools.wraps(func)

  # pylint:disable=invalid-name
  def wrapper(*args, **kwargs):
    self = args[0]
    try:
      return func(*args, **kwargs)
    except exceptions.HttpError as error:
      error_msg = None
      if error.status_code == httplib.NOT_FOUND:
        error_msg = 'Not found'
      elif error.status_code == httplib.FORBIDDEN:
        error_msg = 'Permission denied'

      if error_msg:
        if self.key_id:
          log.error('{0}: key [{1}] for service account [{2}]'.format(
              error_msg, self.key_id, self.address))
        else:
          log.error(
              '{0}: service account [{1}]'.format(error_msg, self.address))
        return
      raise

  return CatchHttpErrors(wrapper)


def CatchHttpErrors(func):
  """Decorator to gracefully quit when any unhandled HTTP error occurs."""

  @functools.wraps(func)

  # pylint:disable=invalid-name
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except exceptions.HttpError as error:
      log.error('Error:\n' + error.content)
      raise

  return wrapper


def ValidateEmail(email):
  """Super basic, ultra-permissive validator for emails."""
  # EMails have a . somewhere after a @
  return re.match(r'[^@]+@[^.]+\..+', email)


def ValidateKeyId(key_id):
  """Ensures a key id is well structured."""
  # Keys are hexadecimal
  return re.match(r'[a-z0-9]+', key_id)


def ValidateAccountId(account_id):
  """Ensures an account id is well structured."""
  if len(account_id) > 63:
    return False

  # This regex is from the protobuffer
  return re.match(r'[a-z]([-a-z0-9]*[a-z0-9])', account_id)


def ProjectToProjectResourceName(project):
  """Turns a project id into a project resource name."""
  return 'projects/{0}'.format(project)


def EmailToAccountResourceName(email):
  """Turns an email into a service account resource name."""
  return 'projects/-/serviceAccounts/{0}'.format(email)


def EmailAndKeyToResourceName(email, key):
  """Turns an email and key id into a key resource name."""
  return 'projects/-/serviceAccounts/{0}/keys/{1}'.format(email, key)


def GetKeyIdFromResourceName(name):
  """Gets the key id from a resource name. No validation is done."""
  return name.split('/')[5]


def DeepCopy(obj):
  return pickle.loads(pickle.dumps(obj))
