##
#  This Script creates a GCP resource reservation for each RUNNING compute engine in your project. 
#  WARNING: It will delete all existing reservation and loop through each machine in a given project to create a new reservation.
#  Usage: 
#       Takes 2 variables:
#                        projectName- GCP Project Name.
#                        onlyDelete- If set to true will only delete reservations, will not create new ones (Useful after reservation event is over). 
#
#  Requirements: gcloud cli
#  Author: Alex Dymanis
#  Date: 11-14-19
##

import os
import json

projectName="MY_GCP_PROJECT"
onlyDelete="false"

#------Stuff-Happens-Below----
instanceList=os.popen('gcloud compute instances list --filter="status:RUNNING" --format=json --project='+projectName)
reservationList=os.popen('gcloud compute reservations list --format=json --project='+projectName)

json_instanceList = json.loads(instanceList.read())
json_reservationList = json.loads(reservationList.read())

#Delete all existing reservations
for reservation in json_reservationList:
    reservationName=reservation["name"]
    reservationZone=reservation["zone"].rsplit('/', 1)[-1]
    os.system('gcloud compute reservations delete '+reservationName+' --zone='+reservationZone+' --quiet --project='+projectName)
    
#Create a reservation for each machine
for instance in json_instanceList:
    instanceName=instance["name"]
    instanceZone=instance["zone"].rsplit('/', 1)[-1]
    instanceType=instance["machineType"].rsplit('/', 1)[-1]

    if onlyDelete != "true":
        os.system('gcloud compute reservations create res-'+instanceName+' --machine-type='+instanceType+' --vm-count=1 --project='+projectName+' --zone='+instanceZone)

