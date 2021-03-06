# -*- coding: utf-8 -*-
"""ece498icc_lab4

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MeNxvVDUeYmfrZuVv0U9xIx3YY-UGmjs
"""

from google.colab import files
uploaded = files.upload()

import requests
import json
import smtplib

# References: https://rohitmidha23.github.io/Colab-Tricks/

# Part 1: Request Real-time Data of COVID

# get json response
covid_data_url = 'https://covidtracking.com/api/v1/states/daily.json'
covid_data_response = requests.get(covid_data_url)
# directly map response into a dictionary
covid_data_dict = json.loads(covid_data_response.text)
copy_covid_data_dict = json.loads(covid_data_response.text)
# keep track of today's date
current_date = covid_data_dict[0]['date']

# reformat dictionary to date -> state -> else structure
new_dict = {}
for i in range(0, len(covid_data_dict)):
  date = covid_data_dict[i]['date']
  state = covid_data_dict[i]['state']
  # create date item in dictionary if not present
  if date not in new_dict:
    new_dict[date] = {}
  # assign all data
  new_dict[date][state] = copy_covid_data_dict[i]
  # delete duplicate info
  del new_dict[date][state]['date']
  del new_dict[date][state]['state']
# reassign values of covid_data_dict
covid_data_dict = new_dict

# print the most up-to-date data of Illinois fetched from the online database
print(str(current_date))
print('IL')
for data in covid_data_dict[current_date]['IL']:
  print(("%s: %s")%(data, covid_data_dict[current_date]['IL'][data]))
print()

# Part 2: Receive and Interpret Commands from Users

# from google.colab import files
# uploaded = files.upload()
# Run ^^above two lines in a separate cell and import intents.json file.

# {"intents": [
#               {"intent": "ReportIntent"},
#               {"intent": "AnswerIntent", "slots": [{"name": "NY", "type": "STATES"},
#                                                    {"name": "positive", "type": "METRICS"},
#                                                    {"name": "20200418", "type": "DATES"}]},
#               {"intent": "AnswerIntent", "slots": [{"name": "IL", "type": "STATES"},
#                                                    {"name": "negative", "type": "METRICS"},
#                                                    {"name": "20200419", "type": "DATES"}]},
#               {"intent": "AnswerIntent", "slots": [{"name": "WA", "type": "STATES"},
#                                                    {"name": "recovered", "type": "METRICS"},
#                                                    {"name": "20200420", "type": "DATES"}]},
#               {"intent": "AnswerIntent", "slots": [{"name": "CA", "type": "STATES"},
#                                                    {"name": "death", "type": "METRICS"},
#                                                    {"name": "20200421", "type": "DATES"}]},
#               {"intent": "AnswerIntent", "slots": [{"name": "GA", "type": "STATES"},
#                                                    {"name": "hospitalized", "type": "METRICS"},
#                                                    {"name": "20200422", "type": "DATES"}]},
#               {"intent": "AnalysisIntent", "slots": [{"name": "TX", "type": "STATES"},
#                                                      {"name": "death rate", "type": "STATISTICS"}]},
#               {"intent": "AnalysisIntent", "slots": [{"name": "FL", "type": "STATES"},
#                                                      {"name": "recover rate", "type": "STATISTICS"}]},
#               {"intent": "AnalysisIntent", "slots": [{"name": "PA", "type": "STATES"},
#                                                      {"name": "hospitalized rate", "type": "STATISTICS"}]}
#             ]}

# get json and map to a dictionary
intents_json = uploaded['intents.json'].decode('utf-8')
intents_dict = json.loads(intents_json)['intents']

# reformat dictionary to intent/slots -> type/name structure
for i in range(0, len(intents_dict)):
  # organize 'slots' if intent is Answer or Analysis
  if intents_dict[i]['intent'] == 'AnswerIntent' or intents_dict[i]['intent'] == 'AnalysisIntent':
    new_dict = {}
    current_intent_slots = intents_dict[i]['slots']
    # make (type, name) dictionary and assign to 'slots'
    for j in range(0, len(current_intent_slots)):
      new_dict[current_intent_slots[j]['type']] = current_intent_slots[j]['name']
    intents_dict[i]['slots'] = new_dict

for i in range(0, len(intents_dict)):
  print(intents_dict[i])
print()

# create list of strings requested by user intents
email_message = ""
for i in range(0, len(intents_dict)):
  intent = intents_dict[i]
  # template response for report intent
  if intent['intent'] == 'ReportIntent':
    date = current_date
    positive_USA = 0
    # find total positive cases in the United States
    for state in covid_data_dict[date]:
      positive_USA += covid_data_dict[date][state]['positive']
    # create template response
    new_string = ("According to the latest data on %d, there are %d positive cases in the United States.")%(date, positive_USA)

  # template response for answer intent
  elif intent['intent'] == 'AnswerIntent':
    date = int(intent['slots']['DATES'])
    metric = intent['slots']['METRICS']
    state = intent['slots']['STATES']
    value = covid_data_dict[date][state][metric]

    # create template response based on metric
    new_string = ("According to the latest data on %d, ")%(date)
    if metric == 'positive' or metric == 'negative' or metric == 'recovered' or metric == 'hospitalized':
      if value is not None:      
        new_string += ("there are %d %s cases in %s.")%(value, metric, state)
      else:
        new_string += ("the number of %s cases in %s is unavailable.")%(metric, state)
    elif metric == 'death':
      if value is not None:
        new_string += ("there are %d %ss in %s.")%(value, metric, state)
      else:
        new_string += ("the number of %ss in %s is unavailable.")%(metric, state)

  # template response for analysis intent
  elif intent['intent'] == 'AnalysisIntent':
    date = current_date
    statistic = intent['slots']['STATISTICS']
    state = intent['slots']['STATES']

    # find first value for requested statistic
    if statistic == 'death rate':
      value = covid_data_dict[date][state]['death']
    elif statistic == 'recover rate':
      value = covid_data_dict[date][state]['recovered']
    elif statistic == 'hospitalized rate':
      value = covid_data_dict[date][state]['hospitalized']
    
    # find total positive cases
    total_cases = covid_data_dict[date][state]['positive']
    
    # create template response
    new_string = ("According to the latest data on %d, the %s in %s is ")%(date, statistic, state)
    if value is None or total_cases is None:
      new_string += "unavailable."
    else:
      # divide statistic by total cases to find rate
      value /= total_cases
      value *= 100
      new_string += ("%.2f")%(value) + "%."
  
  # append new string to email message body
  email_message += new_string + '\n'

print(email_message)

# Part 3: Send Notifications from Email

# identify sender credientials
sender = 'ece498icc@gmail.com'
password = 'ece498icc_sp20'
# identify recipient
to = 'nnathan2@illinois.edu'

#initialize and start server
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
# log in using sender credentials
server.login(sender, password)
# send email from sender to recipient with email_message as body
server.sendmail(sender, to, email_message)
# close server
server.quit()