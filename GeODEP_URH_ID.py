# -*- coding: UTF-8 -*-

#-------------------------------------------------------------------------------
# Name:        GéODEP - Identifiant unique des URH
# Purpose:
#
# Author:      François Landry
#
# Created:     23-10-2018
# Copyright:   (c) IRDA 2018
#-------------------------------------------------------------------------------


from __future__ import division
import arcpy, os, sys, uuid
from GeODEP_Commun import *



#===========================
#   Fonctions principales
#===========================


#Ajout du champ d'identifiant unique des URH
def add_field_id(urh, fld_id):
    try:

        #{Ordre de traitement: [Nom du champ, Type de données, Nombre de charactères maximal, Alias]}
        dct_field = {0: [fld_id, "TEXT", 38, u"Identifiant de l'URH"]}

        add_fields(urh, dct_field)

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)


#Calcul du champ d'identifiant unique des URH
def calc_field_id(urh, fld_id):
    try:
        with arcpy.da.UpdateCursor(urh, [fld_id]) as cursor:
            for row in cursor:
                row[0] = str(uuid.uuid4())

                cursor.updateRow(row)

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)



#=========================
#   Programme principal
#=========================


#Programme principal
if __name__ == "__main__":


    #Log
    log_txt = os.path.join(sys.path[0], "GeODEP_Log.txt")


    #Validation de la licence
    dispo_licence = check_licence(["ArcView", "ArcEditor", "ArcInfo"])

    if dispo_licence is False:
        sys.exit(1)


    #Input
    urh_lyr = arcpy.GetParameterAsText(0)
    urh_desc = arcpy.Describe(urh_lyr)
    urh_path = urh_desc.catalogPath

    metho_field_id = arcpy.GetParameterAsText(1)
    urh_field_id = arcpy.GetParameterAsText(2)
    new_field_id = arcpy.GetParameterAsText(3)


    #Calcul d'un identifiant unique
    if metho_field_id == "Utiliser un nouveau champ":
        write_msg(log_txt, u"Ajout d'un identifiant unique aux URH", False, True)
        add_field_id(urh_path, new_field_id)
        calc_field_id(urh_path, new_field_id)

    else:
        write_msg(log_txt, u"Recalcul de l'identifiant unique des URH", False, True)
        calc_field_id(urh_path, urh_field_id)


    #Fin du script
    write_msg(log_txt, u"Fin du script" + "\n", False, True)
