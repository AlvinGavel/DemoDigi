"""
This script is intended to take the results from the learning module
Kartläggning and transform them into a format that can be handled by
the module factorial_experiment, which is stored one directory further
up. It assumes that the results are in the XML format, rather than
raw_analytics.

This course module is unusual in that it only has one session. Hence
there is no point in plotting how participants improve over
successive sessions.

This will create a directory named 'Results', with another directory
named 'Kartläggning' inside.
"""

import os
import preprocessing as pp

competencies = {'Hitta och tolka digital information':['SearchingForInfo', 'MapServices', 'EvaluateInformation', 'SpotDeepFake', 'OrganisingFiles', 'SharingFiles'],
		'Kommunikation och samarbete':['EmailFunctions', 'SharingPictures', 'SharingEvents', 'CollaborationInDocuments',  'CreatingPresentations', 'SharingLargeFiles'],
		'Skapa och bearbeta digitalt innehåll':['ImageEditingSoftware', 'InfoGraphics', 'TextFormating', 'Templates', 'ChangingPDFs', 'FreeImages'],
		'IT-säkerhet':['SafePasswords', 'Phishing', 'Malware', 'Backup', 'PortableDeviceSafety', 'GDPR'],
		'Problemlösning i digitala miljöer':['SoftwareFreeze', 'FindingSolutions', 'LearningAboutFunctions', 'WifiProblems', 'OnlineMeetingProblems', 'SolvingCrash']}
		
mod = pp.learning_module(competencies, n_sessions = 1)
mod.import_datashop('OLI_analytics/Kartläggning/2022_09_06/Datashop_af_kartlggning_av_digital_komp.xml') # This is temporary. It should not actually target a specific date.
mod.infer_participants_from_full_results()
mod.read_participants_results()
mod.describe_module()

try:
   os.mkdir('Results')
except FileExistsError:
   pass
try:
   os.mkdir('Results/Kartläggning')
except FileExistsError:
   pass
try:
   os.mkdir('Results/Kartläggning/Individer_XML')
except FileExistsError:
   pass
mod.export_results('Results/Kartläggning/Individer_XML')
mod.export_IDs('Results/Kartläggning/XML_IDs.json')
mod.export_SCB_data('Results/Kartläggning/SCB_data.csv')
mod.export_full_results('Results/Kartläggning/XML_to_csv.csv')
