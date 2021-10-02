# -*- coding: UTF-8 -*-

#-------------------------------------------------------------------------------
# Name:        GéODEP - Scénario alternatif
# Purpose:
#
# Author:      François Landry
#
# Created:     02-10-2018
# Copyright:   (c) IRDA 2018
#-------------------------------------------------------------------------------


from __future__ import division
import arcpy, os, re, sys
from GeODEP_Commun import *
from GeODEP_URH_ID import *
from GeODEP_Dom_Val import *
from GeODEP_Export import *



#===========================
#   Fonctions principales
#===========================


def init_dict_fields():
    try:

        #{Ordre de traitement: [Nom du champ, Type de données, Nombre de charactères maximal, Alias]}
        dct_fields = {
        0: ["Qsurf3", "DOUBLE", "#", u"Ruissellement (mm/an)"],
        1: ["Qsout2", "DOUBLE", "#", u"Écoulement aux drains (mm/an)"],
        2: ["Sed2", "DOUBLE", "#", u"Sédiments (kg/ha/an)"],
        3: ["PTotalTOUT", "DOUBLE", "#", u"Phosphore total - Tous les secteurs (kg/ha/an)"],
        4: ["VolQsurf", "DOUBLE", "#", u"Volume de ruissellement (mm/an)"],
        5: ["VolQsout", "DOUBLE", "#", u"Volume d’écoulement aux drains (mm/an) "],
        6: ["Qtesediment", "DOUBLE", "#", u"Volume de sédiments (kg/an)"],
        7: ["QtePTotalTOUT", "DOUBLE", "#", u"Volume de phosphore total - Tous les secteurs (kg/an)"]
        }

        return dct_fields

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)


def add_fields_dif(fc_dif, dct_fields):
    try:
        for idx in dct_fields:
            fld_name, fld_type, fld_length, fld_alias = dct_fields[idx]

            #Remplacement des unités de l'alias pour le ratio
            fld_alias_ratio = re.sub(r"\(.*\)", "(%)", fld_alias)

            #{Ordre de traitement: [Nom du champ, Type de données, Nombre de charactères maximal, Alias]}
            dct_fields_dif = {}

            dct_fields_dif[0] = [fld_name + "_Ref", fld_type, fld_length, fld_alias + u" (Référence)"]
            dct_fields_dif[1] = [fld_name + "_Alt", fld_type, fld_length, fld_alias + u" (Alternatif)"]
            dct_fields_dif[2] = [fld_name + "_Dif", fld_type, fld_length, fld_alias + u" (Différence)"]
            dct_fields_dif[3] = [fld_name + "_Ratio", fld_type, fld_length, fld_alias_ratio + u" (Différence)"]

            add_fields(fc_dif, dct_fields_dif)

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)


def calc_dif_export(fc_ref, fc_alt, fc_dif, fld_id, dct_fields):
    try:
        for idx in dct_fields:
            fld_name = dct_fields[idx][0]

            #{Identifiant: Valeur totale de référence}
            dct_ref = {}

            with arcpy.da.SearchCursor(fc_ref, [fld_id, fld_name]) as cursor:
                for row in cursor:
                    fid, val_ref = row

                    if fid in dct_ref:
                        val_ref += dct_ref[fid]

                    dct_ref[fid] = val_ref

            #{Identifiant: Valeur totale alternative}
            dct_alt = {}

            with arcpy.da.SearchCursor(fc_alt, [fld_id, fld_name]) as cursor:
                for row in cursor:
                    fid, val_alt = row

                    if fid in dct_alt:
                        val_alt += dct_alt[fid]

                    dct_alt[fid] = val_alt

            #{Identifiant: [Référence total, Alternatif total, Différence, Ratio]}
            dct_dif = {}

            for fid in dct_alt:
                val_alt = dct_alt[fid]
                val_ref = dct_ref[fid]

                if (val_alt and val_ref) is not None:
                    val_dif = round(val_alt - val_ref, 2)

                else:
                    val_dif = None

                if val_ref <> 0:
                    val_ratio = round((val_dif / val_ref) * 100, 2)

                else:
                    val_ratio = None

                dct_dif[fid] = [val_ref, val_alt, val_dif, val_ratio]

            with arcpy.da.UpdateCursor(fc_dif, [fld_id, fld_name + "_Ref", fld_name + "_Alt", fld_name + "_Dif", fld_name + "_Ratio"]) as cursor:
                for row in cursor:
                    fid = row[0]

                    row[-4:] = dct_dif[fid]

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
    urh_ref_lyr = arcpy.GetParameterAsText(0)
    urh_ref_desc = arcpy.Describe(urh_ref_lyr)
    urh_ref_path = urh_ref_desc.catalogPath

    urh_alt_lyr = arcpy.GetParameterAsText(1)
    urh_alt_desc = arcpy.Describe(urh_alt_lyr)
    urh_alt_path = urh_alt_desc.catalogPath

    urh_field_id = arcpy.GetParameterAsText(2)

    bool_calc_par = arcpy.GetParameterAsText(3)
    par_field_id = arcpy.GetParameterAsText(4)

    bool_calc_prod = arcpy.GetParameterAsText(5)
    prod_field_id = arcpy.GetParameterAsText(6)


    #Environnement
    arcpy.env.overwriteOutput = True


    #Recalcul du ruissellement
    write_msg(log_txt, u"Recalcul du ruissellement", False, True)
    add_fields_ruis(urh_alt_path)
    calc_ruis_export(urh_alt_path)


    #Recalcul de l'exportation des sédiments
    write_msg(log_txt, u"Recalcul de l'exportation des sédiments", False, True)
    add_fields_sed(urh_alt_path)
    calc_sed_export(urh_alt_path)


    #Recalcul de l'exportation du phosphore
    write_msg(log_txt, u"Recalcul de l'exportation du phosphore", False, True)
    add_fields_phos(urh_alt_path)
    calc_phos_export(urh_alt_path)


    #Workspace des URH
    urh_ref_ws = trouve_ws(urh_ref_path)
    urh_alt_ws = trouve_ws(urh_alt_path)


    #Initialisation
    urh_alt_name = os.path.basename(urh_alt_path)
    dict_fields = init_dict_fields()


    #Comparaison des deux scénarios
    write_msg(log_txt, u"Comparaison des deux scénarios", False, True)

    list_fields = [urh_field_id, par_field_id, prod_field_id]

    for field in list_fields:
        if field == "":
            list_fields.remove(field)

    field_mapping = fm_keep([urh_alt_path], list_fields)
    urh_dif_path = arcpy.FeatureClassToFeatureClass_conversion(urh_alt_path, urh_alt_ws, urh_alt_name + "_DIF_URH", "#", field_mapping, "#")

    add_fields_dif(urh_dif_path, dict_fields)
    calc_dif_export(urh_ref_path, urh_alt_path, urh_dif_path, urh_field_id, dict_fields)


    #Sommation des comparaisons par parcelle
    if bool_calc_par == "true":
        write_msg(log_txt, u"Sommation des comparaisons par parcelle", False, True)

        list_fields = [par_field_id, prod_field_id]

        for field in list_fields:
            if field == "":
                list_fields.remove(field)

        par_dif_path = arcpy.Dissolve_management(urh_alt_path, os.path.join(urh_alt_ws, urh_alt_name + "_DIF_PAR"), list_fields, "#", "MULTI_PART", "DISSOLVE_LINES")

        add_fields_dif(par_dif_path, dict_fields)
        calc_dif_export(urh_ref_path, urh_alt_path, par_dif_path, par_field_id, dict_fields)


    #Sommation des comparaisons par producteur
    if bool_calc_prod == "true":
        write_msg(log_txt, u"Sommation des comparaisons par producteur", False, True)
        prod_dif_path = arcpy.Dissolve_management(urh_alt_path, os.path.join(urh_alt_ws, urh_alt_name + "_DIF_PROD"), prod_field_id, "#", "MULTI_PART", "DISSOLVE_LINES")

        add_fields_dif(prod_dif_path, dict_fields)
        calc_dif_export(urh_ref_path, urh_alt_path, prod_dif_path, prod_field_id, dict_fields)


    #Appliquation des domaines de valeurs
    write_msg(log_txt, u"Appliquation des domaines de valeurs", False, True)
    dom_val(urh_alt_path, urh_alt_ws)


    #Fin du script
    write_msg(log_txt, u"Fin du script" + "\n", False, True)
