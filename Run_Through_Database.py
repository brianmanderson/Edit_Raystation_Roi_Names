__author__ = 'Brian M Anderson'
# Created on 7/7/2020

from connect import *
import os


def ChangePatient_8B(patient_db, MRN):
    info_all = patient_db.QueryPatientInfo(Filter={"PatientID": MRN})
    # If it isn't, see if it's in the secondary database
    if not info_all:
        info_all = patient_db.QueryPatientInfo(Filter={"PatientID": MRN}, UseIndexService=True)
    patient = None
    for info_temp in info_all:
        if info_temp['PatientID'] == MRN:
            info = info_temp
            patient = patient_db.LoadPatient(PatientInfo=info, AllowPatientUpgrade=True)
            break
    return patient


def ChangePatient_PT(patient_db, MRN):
    first_name, last_name = MRN.split(' ')
    info_all = patient_db.QueryPatientInfo(Filter={"LastName": last_name, 'FirstName':first_name}, UseIndexService=False)
    # If it isn't, see if it's in the secondary database
    if not info_all:
        info_all = patient_db.QueryPatientInfo(Filter={"LastName": last_name, 'FirstName':first_name}, UseIndexService=True)
    patient = None
    for info in info_all:
        patient = patient_db.LoadPatient(PatientInfo=info, AllowPatientUpgrade=True)
        break
    return patient


patient_db = get_current("PatientDB")
patients = []
base_path = r'H:\Modular_Projects\Edit_Raystation_Roi_Names'
fid = open(os.path.join(base_path, 'Patient_List.txt'))
base_success = os.path.join(base_path, 'Success')
base_fail = os.path.join(base_path, 'Failed')
for p in [base_success, base_fail]:
    if not os.path.exists(p):
        os.makedirs(p)
for line in fid:
    line = line.strip('\n')
    patients.append(line)
fid.close()
for patient_id in patients:
    success_path = os.path.join(base_success, '{}.txt'.format(patient_id))
    if os.path.exists(success_path):
        continue
    try:
        if patient_id.find('PT') != -1:
            patient = ChangePatient_PT(patient_db, patient_id)
        else:
            patient = ChangePatient_8B(patient_db, patient_id)
    except:
        print('Failed to load')
        continue
    if patient is None:
        fid = open(os.path.join(base_fail, '{}.txt'.format(patient_id)), 'w+')
        fid.close()
        continue
    for case in patient.Cases:
        rois_in_case = []
        for roi in case.PatientModel.RegionsOfInterest:
            if roi.Name.find(':') != -1:
                case.PatientModel.RegionsOfInterest[roi.Name].Name = roi.Name.replace(':','')
    patient.Save()
    fid = open(success_path, 'w+')
    fid.close()