##
#  This Script creates a GCP resource reservation for each compute engine in your project. 
#  WARNING: It will delete all existing reservations and loop through each machine in a given project to create a new reservation.
#  Usage: 
#       Takes 3 variables:
#                        projectName- GCP Project Name.
#                        onlyDelete- If set to true will only delete reservations, will not create new ones (Useful after reservation event is over). 
#                        onlyRunning- If set to true will only create reservations for Running instances. 
#
#  Requirements: gcloud cli
#  Author: Alex Dymanis
#  Date: 11-14-19
#  Version 1.2
#
#
#  Update 09-16-2021 by Khalid Maqsudi
#  Version 1.3
#  First argument will be your project name.  example:  
#  $ python GCP_Compute_Engine_Reservation.py my-dev-project-name
##

import os
import json
import sys

my_gcp_project=sys.argv[1]

#projectName="MY_GCP_PROJECT"
projectName=my_gcp_project
onlyDelete="false"
onlyRunning="true"


#------Stuff-Happens-Below----
if onlyRunning == "true":
    statusFilter="RUNNING"
else:
    statusFilter="*"

instanceList=os.popen('gcloud compute instances list --filter="status:'+statusFilter+'" --format=json --project='+projectName)
reservationList=os.popen('gcloud compute reservations list --format=json --project='+projectName)

#
if onlyDelete == "false":
    json_instanceList = json.loads(instanceList.read())
else:
    json_instanceList = ""
json_reservationList = json.loads(reservationList.read())

#Validates machines against reservations
def validateReservation(namePrefixed,instanceZone,instanceType,instanceLocalDiskCount,instanceLocalDiskInterface):
    for reservation in json_reservationList:
        reservationName=reservation["name"]
        reservationZone=reservation["zone"].rsplit('/', 1)[-1]
        reservationType=reservation["specificReservation"]["instanceProperties"]["machineType"]
        reservationLocalSSDCount=0
        reservationLocalSSDInterface=""

        if "localSsds" in reservation["specificReservation"]["instanceProperties"]:
            reservationLocalSSDCount = len(reservation["specificReservation"]["instanceProperties"]["localSsds"])
            reservationLocalSSDInterface = reservation["specificReservation"]["instanceProperties"]["localSsds"][0]["interface"]

        if reservationName == namePrefixed:
            if reservationZone == instanceZone and reservationType == instanceType and reservationLocalSSDCount == instanceLocalDiskCount and reservationLocalSSDInterface == instanceLocalDiskInterface:
                return(0, reservationName, reservationZone, reservationType)
            else:
                return(1, reservationName, reservationZone, reservationType)
    return(2, reservationName, reservationZone, reservationType)


namePrefixed_all = []
#Create reservation for each instance
for instance in json_instanceList:
    instanceName=instance["name"]
    instanceZone=instance["zone"].rsplit('/', 1)[-1]
    instanceType=instance["machineType"].rsplit('/', 1)[-1]
    namePrefixed="res-"+instanceName
    namePrefixed_all.append(namePrefixed)
    instanceDisks=instance["disks"]
    instanceLocalDiskCount = 0
    instanceLocalDiskInterface = ""
    localSSD = ""

    for instanceLocalDisk in instanceDisks:
        if instanceLocalDisk["type"] == "SCRATCH":
            instanceLocalDiskCount += 1
            instanceLocalDiskInterface=instanceLocalDisk["interface"]

    # Append local-ssd parameter to cli
    if instanceLocalDiskCount > 0:
        for _ in range(instanceLocalDiskCount):
            localSSD += " --local-ssd=interface="+ instanceLocalDiskInterface + ",size=375"

    if json_reservationList:
        validateResult = validateReservation(namePrefixed,instanceZone,instanceType,instanceLocalDiskCount,instanceLocalDiskInterface)
        if validateResult[0] == 0: 
            print("SKIPPING: "+namePrefixed)
            continue
        elif validateResult[0] == 1: #recreate
            print("RECREATING: "+namePrefixed)
            os.system('gcloud compute reservations delete '+namePrefixed+' --zone='+validateResult[2]+' --quiet --project='+projectName)
            os.system('gcloud compute reservations create '+namePrefixed+' --machine-type='+instanceType+' --vm-count=1 --project='+projectName+' --zone='+instanceZone+localSSD)
            continue

    print("CREATING: "+namePrefixed)
    os.system('gcloud compute reservations create '+namePrefixed+' --machine-type='+instanceType+' --vm-count=1 --project='+projectName+' --zone='+instanceZone+localSSD)

#Cleanup invalid reservations 
for reservation in json_reservationList:
        reservationName=reservation["name"]
        reservationZone=reservation["zone"].rsplit('/', 1)[-1]
        
        if reservationName not in namePrefixed_all:
           print("Deleting res: "+reservationName)
           os.system('gcloud compute reservations delete '+reservationName+' --zone='+reservationZone+' --quiet --project='+projectName)


