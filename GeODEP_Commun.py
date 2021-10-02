# -*- coding: UTF-8 -*-

#-------------------------------------------------------------------------------
# Name:        GéODEP - Fonctions communes
# Purpose:
#
# Author:      François Landry
#
# Created:     02-10-2018
# Copyright:   (c) IRDA 2018
#-------------------------------------------------------------------------------


from __future__ import division
import arcpy, os, sys, time, traceback



#========================
#   Fonctions communes
#========================

#Décodage d'un string en unicode
def u(string):
    try:
        return string.decode("utf-8")

    except:
        return string


#Formatage d'un message d'erreur
def get_error():
    tb = sys.exc_info()[2]
    tb_info = traceback.format_tb(tb)[0]
    py_info = str(sys.exc_info()[1])
    arcpy_info = arcpy.GetMessages(2)

    msg = u"Traceback Info:" + u(arcpy_info)

    return msg


#Écriture d'un message dans un fichier texte
def write_msg(txt, msg, error, set_time):
    if set_time is True:
        timestamp = time.strftime("%Y-%m-%d @ %H:%M:%S") + ": "

    else:
        timestamp = ""

    msg_final = timestamp + msg

    if error is True:
        arcpy.AddError(msg_final.encode("cp1252"))

    else:
        arcpy.AddMessage(msg_final.encode("cp1252"))

    with open(txt, "a") as log:
        log.write(msg_final.encode("utf-8") + "\n")


def check_licence(lst_licences):
    try:
        product = arcpy.ProductInfo()

        if product in lst_licences:
            write_msg(log_txt, u"Licence ArcGIS en utilisation: " + u(product), False, True)

            return True

        elif product == "NotInitialized":
            for licence in lst_licences:
                dispo = arcpy.CheckProduct(licence)

                if dispo == "Available":
                    write_msg(log_txt, u"Licence ArcGIS disponible: " + u(licence), False, True)

                    return True

        else:
            write_msg(log_txt, u"Aucune licence ArcGIS disponible", True, True)

            return False

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)


#Ajout de champs si non existants
def add_fields(tbl, dct_fields):
    try:
        lst_fields_name = []

        lst_fields = arcpy.ListFields(tbl)

        for fld in lst_fields:
            lst_fields_name.append(fld.name)

        for idx in range(len(dct_fields)):
            fld_name, fld_type, fld_length, fld_alias = dct_fields[idx]

            if fld_name not in lst_fields_name:
                arcpy.AddField_management(tbl, fld_name, fld_type, "#", "#", fld_length, fld_alias.encode("cp1252"), "NULLABLE", "NON_REQUIRED", "#")

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)


#Trouve le workspace d'un jeu de données
def trouve_ws(item):
    try:
        desc = arcpy.Describe(item)
        datatype = desc.datatype

        if datatype == "FeatureClass":
            ws = "Workspace"

        elif datatype == "ShapeFile":
            ws = "Folder"

        else:
            write_msg(log_txt, u"Type de données invalid: " + u(datatype), True, True)
            sys.exit(1)

        while datatype <> ws:
            item = os.path.dirname(item)
            desc = arcpy.Describe(item)
            datatype = desc.datatype

        return item

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)


#Field Mapping à partir d'une liste de champs à garder
def fm_keep(lst_table, lst_fields):
    try:
        fld_mapping = arcpy.FieldMappings()

        for tbl in lst_table:
            fld_mapping.addTable(tbl)

        for fld in fld_mapping.fields:
            fld_name = fld.name

            if fld_name not in lst_fields:
                fld_mapping.removeFieldMap(fld_mapping.findFieldMapIndex(fld_name))

        return fld_mapping

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)


#Log
log_txt = os.path.join(sys.path[0], "GeODEP_Log.txt")
