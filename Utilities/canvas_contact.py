'''
This module was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen, and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python module ---

This module is intended to do provide feedback to the participants in
our learning modules, using the Canvas API - which is documented at
https://canvas.instructure.com/doc/api/index.html - to send messages
to each participant.

Written by Alvin Gavel,
https://github.com/Alvin-Gavel/Demodigi
'''

import os

import requests as r

class UnexpectedResponseError(Exception):
    def __init__(self, msg):
        self.msg = msg
        return


def account_name_user_id_mapping(token):
   """
   Canvas uses short user IDs that differ from the account names. This
   finds the mapping between the two.
   
   Note that this will include "users" like 'Outcomes Service API' and
   'Quizzes.Next Service API', so some filtering is necessary
   afterwards.
   """
   def find_next_link(link_long_string):
      """
      The get requests return a string which can be broken up into a comma-
      separated list, where each entry is a link to the first, current, next
      and previous (where a next and previous exist). This picks out which 
      one is the next.
      """
      link_strings = link_long_string.split(',')
      found = False
      for link_string in link_strings:
         if '; rel="next"' in link_string:
            link = link_string.split('>')[0].split('<')[1]
            found = True
            break
      if not found:
         link = None
      return link
   
   header = {
      'Authorization': 'Bearer {}'.format(token)
   }
   response = r.get('https://af.instructure.com/api/v1/accounts/1/users', headers=header)
   if not 'OK' in response.headers['Status']:
      raise UnexpectedResponseError('When accessing user list, canvas returned status "{}"'.format(response.headers['Status']))
      
   users = response.json()
      
   link = find_next_link(response.headers['Link'])
   while link != None:
      response = r.get(link, headers=header)
      users += response.json()
      link = find_next_link(response.headers['Link'])
   
   mapping = {}
   for user in users:
      mapping[user['name']] = user['id']
   return mapping


def send_file_contents(file_path, user_id, subject, token):
   """
   Send a message to a participant, where the message containing text read
   from a file.
   """
   f = open(file_path, 'r')
   contents = f.read()
   f.close()
   
   payload = {
      'subject': subject,
      'force_new': True,
      'recipients': [user_id],
      'body': contents,
      'group_conversation':False
   }
   header = {
      'Authorization': 'Bearer {}'.format(token)
   }
   
   response = r.post('https://af.instructure.com/api/v1/conversations', data = payload, headers=header)
   response_content = response.json()
   if not type(response_content) == list:
      raise UnexpectedResponseError('When uploading, canvas returned error message "{}"'.format(response_content['errors'][0]['message']))
   return


def upload_file(file_path, canvas_path, user_id, token):
   """
   Upload a file to a particular path, in the Canvas API, while acting
   as a specific user - possibly yourself
   """
   header = {
      'Authorization': 'Bearer {}'.format(token)
   }

   file_name = file_path.split('/')[-1]
   sz = os.stat(file_path).st_size
   payload = {
      'name': file_name,
      'size': sz,
      'as_user_id': user_id
   }

   response_1 = r.post(canvas_path, data = payload, headers=header)
   if not 'OK' in response_1.headers['Status']:
      raise UnexpectedResponseError('When preparing for upload, canvas returned status "{}"'.format(response_1.headers['Status']))
   response_1_content = response_1.json()
   upload_url = response_1_content['upload_url']

   f = open(file_path, 'rb')
   response_2 = r.post(upload_url, files = {file_name: f})
   response_2_content = response_2.json()
   if not response_2_content['upload_status'] == 'success':
      raise UnexpectedResponseError('When uploading, canvas returned status "{}"'.format(response_2.headers['Status']))
   return response_2_content['id']


def upload_conversation_attachment(file_path, user_id, token):
   """
   Upload a conversation attachment to user file area. Typically, this
   would be your own, in preparation for sending a message to another
   user with that file attached.
   """
   header = {
      'Authorization': 'Bearer {}'.format(token)
   }
   
   response_1 = r.get('https://af.instructure.com/api/v1/users/{}/folders'.format(user_id), headers = {'Authorization': 'Bearer {}'.format(token)})
   if not 'OK' in response_1.headers['Status']:
      raise UnexpectedResponseError('When locating conversation attachment folder, canvas returned status "{}"'.format(response_1.headers['Status']))
   response_1_content = response_1.json()
   
   found = False
   for item in response_1_content:
      if item['full_name'] == 'my files/conversation attachments':
         found = True
         folder_id = item['id']
         break
   if not found:
      raise UnexpectedResponseError("Could not locate 'conversation attachments' folder")
   
   file_id = upload_file(file_path, 'https://af.instructure.com/api/v1/folders/{}/files'.format(folder_id), user_id, token)
   return file_id


def send_file(file_path, self_id, target_id, subject, message, token):
   """
   Send a message to a participant, containing an attached file
   """
   file_id = upload_conversation_attachment(file_path, self_id, token)
   
   payload = {
      'subject': subject,
      'force_new': True,
      'recipients': [target_id],
      'attachment_ids[]':[file_id],
      'body': message,
      'mode':'sync'
   }
   header = {
      'Authorization': 'Bearer {}'.format(token)
   }

   response = r.post('https://af.instructure.com/api/v1/conversations', data = payload, headers=header)
   response_content = response.json()
   if not type(response_content) == list:
      raise UnexpectedResponseError('When uploading, canvas returned error message "{}"'.format(response_content['errors'][0]['message']))
   return

