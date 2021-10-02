# -*- coding: UTF-8 -*-

#-------------------------------------------------------------------------------
# Name:        GéODEP - Domaines de valeurs du scénario
# Purpose:
#
# Author:      François Landry
#
# Created:     23-10-2018
# Copyright:   (c) IRDA 2018
#-------------------------------------------------------------------------------


from __future__ import division
import arcpy, os, sys
from GeODEP_Commun import *



#===========================
#   Fonctions principales
#===========================


def dom_val(fc, ws):
    try:

        #{Code: Description}
        dom_culture = {
        "AUC": u"Autre culture",
        "AVO": u"Avoine",
        "BLE": u"Blé, triticale, épeautre",
        "Brsh": u"Broussailles",
        "CNL": u"Canola",
        "EAU": u"Plan d'eau",
        "F": u"Forêt",
        "FOI": u"Foin",
        "ILE": u"Île",
        "MAI": u"Maïs",
        "MAR": u"Maraîcher",
        "MIX": u"Culture multiple",
        "NON": u"Culture inconnue",
        "NPv": u"Route non-pavée",
        "ORG": u"Orge",
        "PTF": u"Petits fruits",
        "Pve": u"Route pavée",
        "ResL": u"Zone urbaine - Densité faible",
        "ResM": u"Zone urbaine - Densité élevée",
        "SOY": u"Soya",
        "Wet": u"Milieu humide"
        }

        #{Code: Description}
        dom_indpardra = {
        "N": u"Non",
        "O": u"Oui"
        }

        #{Code: Description}
        dom_couv = {
        0: u"Non",
        1: u"Oui"
        }

        #{Code: Description}
        dom_drain_sout = {
        1: u"Systématique",
        2: u"Partiel",
        3: u"Absent"
        }

        #{Code: Description}
        dom_drain_surf = {
        1: u"Bon",
        2: u"Moyen",
        3: u"Déficient"
        }

        #{Code: Description}
        dom_cond_hydro = {
        1: u"Bonne",
        2: u"Présence de zone à risque",
        3: u"Dominance de zone à risque"
        }

        #{Code: Description}
        dom_bande_riv = {
        1: u"Ne s''applique pas",
        2: u"Inférieure à 1 mètre",
        3: u"De 1 à 3 mètres",
        4: u"Supérieure à 3 mètres"
        }

        #{Code: Description}
        dom_avaloir = {
        1: u"Absente",
        2: u"Captage partiel",
        3: u"Captage systématique"
        }

        #{Code: Description}
        dom_trav_sol = {
        1: u"Labour à l'automne",
        2: u"Chisel ou pulvériseur à l'automne",
        3: u"Déchaumage au printemps",
        4: u"Semi-direct ou billons"
        }

        #{Code: Description}
        dom_engrais_per = {
        1: u"Pré-semi",
        2: u"Post-levée",
        3: u"Automne hâtif",
        4: u"Automne tardif"
        }

        #{Code: Description}
        dom_engrais_delai = {
        1: u"Inférieur à 48h",
        2: u"De 48h à une semaine",
        3: u"Supérieur à une semaine",
        4: u"Non incorporé"
        }

        #[Domaine, Nom du domaine, Description du domaine, Type de champ, Liste de champs]
        lst_traitement = [
        [dom_culture, u"Culture_Agricole", u"Culture agricole", "TEXT", ["util_terr", "cult_ante"]],
        [dom_indpardra, u"Indicateur_Drainage", u"Indicateur de parcelle agricole drainée", "TEXT", ["INDPARDRA"]],
        [dom_couv, u"Indicateur_Couverture", u"Indicateur de couverture", "LONG", ["Couv_ass", "Couv_derob"]],
        [dom_drain_sout, u"Drainage_Souterrain", u"Aménagement du drainage souterrain", "LONG", ["Drai_Sout"]],
        [dom_drain_surf, u"Ecoulement_Surface", u"Classe d’écoulement de surface", "LONG", ["Drai_surf"]],
        [dom_cond_hydro, u"Profil_Cultural", u"Condition du profil cultural", "LONG", ["Cond_hydro"]],
        [dom_bande_riv, u"Bande_Riveraine", u"Indicateur de bande riveraine","LONG", ["Bande_riv"]],
        [dom_avaloir, u"Avaloir", u"Aménagements de structure de contrôle", "LONG", ["Avaloir"]],
        [dom_trav_sol, u"Travail_Sol", u"Travail du sol", "LONG", ["Trav_sol"]],
        [dom_engrais_per, u"Periode_Engrais", u"Période d'épandage de l'engrais", "DOUBLE", ["Fum1_per", "Fum2_per", "Fum3_per"]],
        [dom_engrais_delai, u"Delai_Engrais", u"Délai d’incorporation de l'engrais", "DOUBLE", ["Fum1_delai", "Fum2_delai", "Fum3_delai"]]
        ]

        ws_desc = arcpy.Describe(ws)
        ws_datatype = ws_desc.datatype

        if ws_datatype == "Workspace":

            #Liste des nom de domaine du workspace
            lst_domains_ws_name = []

            for domain_ws in arcpy.da.ListDomains(ws):
                lst_domains_ws_name.append(domain_ws.name)

            #Création des domaines
            for lst_param in lst_traitement:
                dct_dom, dom_name, dom_desc, fld_type, lst_fields = lst_param

                #Création du domaine
                if dom_name not in lst_domains_ws_name:
                    write_msg(log_txt, "\t" + u"Création du domaine " + u(dom_name), False, False)
                    arcpy.CreateDomain_management(ws, dom_name, dom_desc.encode("cp1252"), fld_type, "CODED", "DUPLICATE", "DEFAULT")

                    #Ajout des valeurs
                    for code in dct_dom:
                        desc = dct_dom[code]
                        arcpy.AddCodedValueToDomain_management(ws, dom_name, code, desc.encode("cp1252"))

                    #Tri en ordre croissant
                    arcpy.SortCodedValueDomain_management(ws, dom_name, "CODE", "ASCENDING")

                #Assignation du domaine
                for fld_name in lst_fields:
                    for fld_fc in arcpy.ListFields(fc):
                        if fld_fc.name.upper() == fld_name.upper():
                            if fld_fc.domain == "" or fld_fc.domain <> dom_name:
                                write_msg(log_txt, "\t" + u"Assignation du domaine " + u(dom_name) + u" au champ " + u(fld_name), False, False)
                                arcpy.AssignDomainToField_management(fc, fld_name, dom_name, "#")

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


    #Workspace des URH
    urh_ws = trouve_ws(urh_path)


    #Appliquation des domaines de valeurs
    write_msg(log_txt, u"Appliquation des domaines de valeurs", False, True)
    dom_val(urh_path, urh_ws)


    #Fin du script
    write_msg(log_txt, u"Fin du script" + "\n", False, True)
