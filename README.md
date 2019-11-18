# GCP_Compute_Engine_Reservation
Script to create a GCP resource reservation for every GCE in your GCP project. 
  This Script creates a GCP resource reservation for each compute engine in your project. 
### WARNING: It will delete all existing reservations and loop through each machine in a given project to create a new reservation.
##### Notes: Script is re-runable and every run will sync reservations against GCE resources.
##### Usage: 
######       Takes 3 variables:
######                        projectName- GCP Project Name.
######                        onlyDelete- If set to true will only delete reservations, will not create new ones (Useful after reservation event is over). 
######                       onlyRunning- If set to true will only create reservations for Running instances. 
