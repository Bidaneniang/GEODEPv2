# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        GéODEP - Calcul des exportations
# Purpose:
# Mise a jour 18/12/2019- Facteurs CMais en sillage et Forets
# Author:      François Landry, Mohamed Niang
#
# Created:     27-09-2018
# Copyright:   (c) IRDA 2018
#-------------------------------------------------------------------------------


from __future__ import division
import arcpy, math, os, sys
from GeODEP_Commun import *
from GeODEP_URH_ID import *



#========================================
#   Calcul de la superficie en hectare
#========================================


#Ajout du champ de superficie en hectare
def add_field_ha(urh):
    try:

        #{Ordre de traitement: [Nom du champ, Type de données, Nombre de charactères maximal, Alias]}
        dct_field = {0: ["Zone_ha2", "DOUBLE", "#", u"Superficie (Ha)"]}

        add_fields(urh, dct_field)

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)


#Calcul du champ de superficie en hectare
def calc_Zone_ha2(urh):
    try:
        with arcpy.da.UpdateCursor(urh, ["SHAPE@", "Zone_ha2"]) as cursor:
            for row in cursor:
                shape = row[0]

                row[1] = shape.getArea("PLANAR", "HECTARES")

                cursor.updateRow(row)

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)



#==========================
#   Calcul des quantités
#==========================


def calc_Qte(Zone_ha2, Indice):
    return Zone_ha2 * Indice



#==============================
#   Calculs du ruissellement
#==============================


def calc_Modif_GHDRAIN(Drai_sout):
    if Drai_sout == 1:
        return -2
    elif Drai_sout == 2:
        return -1
    elif Drai_sout == 3:
        return 0
    else:
        return 0


def calc_Gr_hydroDRAIN(Drai_Sout, GR_HYDROs, Modif_GHDRAIN):
    if Drai_Sout in (1, 2, 3):
        return GR_HYDROs + Modif_GHDRAIN
    else:
        return GR_HYDROs


def calc_Modif_GrHySURF(Drai_surf):
    if Drai_surf == 1:
        return -1
    elif Drai_surf == 2:
        return 0
    elif Drai_surf == 3:
        return 1
    else:
        return 0


def calc_Modif_GrHyPROFIL(Cond_hydro, GR_HYDROs):
    if Cond_hydro == 1:
        return 0
    elif Cond_hydro == 2:
        return 1
    elif Cond_hydro == 3:
        return 2
    else:
        return 0


def calc_Gr_hydroF(GR_HYDROs, Modif_GrHySURF, Modif_GrHyPROFIL):
    return GR_HYDROs + Modif_GrHySURF + Modif_GrHyPROFIL


def calc_Gr_hydroF2(Gr_hydroF):
    if Gr_hydroF > 9:
        return 9
    else:
        return Gr_hydroF


def calc_Qsurf(Util_terr, Gr_hydroDRAIN):
    if Util_terr in ("MAI", "MAR"):
        return 4.8571 * math.pow(Gr_hydroDRAIN, 2) - 12.171 * Gr_hydroDRAIN + 66.77
    elif Util_terr in ("FOI", "NON"):
        return 3.4175 * math.pow(Gr_hydroDRAIN, 2) - 7.9543 * Gr_hydroDRAIN + 60
    elif Util_terr in ("SOY", "CNL"):
        return 4.9858 * math.pow(Gr_hydroDRAIN, 2) - 13.82 * Gr_hydroDRAIN + 66.88
    elif Util_terr in ("AVO", "ORG", "BLE", "AUC", "MIX", "PTF"):
        return 4.6351 * math.pow(Gr_hydroDRAIN, 2) - 11.73 * Gr_hydroDRAIN + 62.95
    else:
        return 3.4175 * math.pow(Gr_hydroDRAIN, 2) - 7.9543 * Gr_hydroDRAIN + 30.76


def calc_Qsurf2pre(Util_terr, Gr_hydroDRAIN, Cond_hydro, Drai_surf, Qsurf):
 if Util_terr == "MAI" or Util_terr == "MAR" and Cond_hydro == 1 and Drai_surf == 1 and Gr_hydroDRAIN == 1:
  return 0 + 0 + Qsurf
 elif Util_terr == "MAI" or Util_terr == "MAR" and Cond_hydro == 1 and Drai_surf == 1 and Gr_hydroDRAIN > 1:
  return 0 - 56.2 + Qsurf
 elif Util_terr == "MAI" or Util_terr == "MAR" and Cond_hydro == 1 and Drai_surf == 2:
  return 0 + 0 + Qsurf
 elif Util_terr == "MAI" or Util_terr == "MAR" and Cond_hydro == 1 and Drai_surf == 3: 
  return 0 + 56.2 + Qsurf
 elif Util_terr == "MAI" or Util_terr == "MAR" and Cond_hydro == 2 and Drai_surf == 1 and Gr_hydroDRAIN == 1:
  return 28.1 + 0 + Qsurf
 elif Util_terr == "MAI" or Util_terr == "MAR" and Cond_hydro == 2 and Drai_surf == 1 and Gr_hydroDRAIN > 1:
  return 28.1 - 56.2 + Qsurf
 elif Util_terr == "MAI" or Util_terr == "MAR" and Cond_hydro == 2 and Drai_surf == 2:
  return 28.1 + 0 + Qsurf
 elif Util_terr == "MAI" or Util_terr == "MAR" and Cond_hydro == 2 and Drai_surf == 3:
  return 28.1 + 56.2 + Qsurf
 elif Util_terr == "MAI" or Util_terr == "MAR" and Cond_hydro == 3 and Drai_surf == 1 and Gr_hydroDRAIN == 1:
  return 56.2 + 0 + Qsurf
 elif Util_terr == "MAI" or Util_terr == "MAR" and Cond_hydro == 3 and Drai_surf == 1 and Gr_hydroDRAIN > 1:
  return 56.2 - 56.2 + Qsurf
 elif Util_terr == "MAI" or Util_terr == "MAR" and Cond_hydro == 3 and Drai_surf == 2:
  return 56.2 + 0 + Qsurf
 elif Util_terr == "MAI" or Util_terr == "MAR" and Cond_hydro == 3 and Drai_surf == 3:
  return 56.2 + 56.2 + Qsurf
 elif Util_terr == "FOI" or Util_terr == "NON" and Cond_hydro == 1 and Drai_surf == 1 and Gr_hydroDRAIN == 1:
  return 0 + 0 + Qsurf
 elif Util_terr == "FOI" or Util_terr == "NON" and Cond_hydro == 1 and Drai_surf == 1 and Gr_hydroDRAIN > 1:
  return 0 - 52.4 + Qsurf
 elif Util_terr == "FOI" or Util_terr == "NON" and Cond_hydro == 1 and Drai_surf == 2:
  return 0 + 0 + Qsurf
 elif Util_terr == "FOI" or Util_terr == "NON" and Cond_hydro == 1 and Drai_surf == 3:
  return 0 + 52.4 + Qsurf
 elif Util_terr == "FOI" or Util_terr == "NON" and Cond_hydro == 2 and Drai_surf == 1 and Gr_hydroDRAIN == 1:
  return 26.2 + 0 + Qsurf
 elif Util_terr == "FOI" or Util_terr == "NON" and Cond_hydro == 2 and Drai_surf == 1 and Gr_hydroDRAIN > 1:
  return 26.2 - 52.4 + Qsurf
 elif Util_terr == "FOI" or Util_terr == "NON" and Cond_hydro == 2 and Drai_surf == 2:
  return 26.2 + 0 + Qsurf
 elif Util_terr == "FOI" or Util_terr == "NON" and Cond_hydro == 2 and Drai_surf == 3:
  return 26.2 + 52.4 + Qsurf
 elif Util_terr == "FOI" or Util_terr == "NON" and Cond_hydro == 3 and Drai_surf == 1 and Gr_hydroDRAIN == 1:
  return 52.4 + 0 + Qsurf
 elif Util_terr == "FOI" or Util_terr == "NON" and Cond_hydro == 3 and Drai_surf == 1 and Gr_hydroDRAIN > 1:
  return 52.4 - 52.4 + Qsurf
 elif Util_terr == "FOI" or Util_terr == "NON" and Cond_hydro == 3 and Drai_surf == 2:
  return 52.4 + 0 + Qsurf
 elif Util_terr == "FOI" or Util_terr == "NON" and Cond_hydro == 3 and Drai_surf == 3:
  return 52.4 + 52.4 + Qsurf
 elif Util_terr == "SOY" or Util_terr == "CNL" and Cond_hydro == 1 and Drai_surf == 1 and Gr_hydroDRAIN == 1:
  return 0 + 0 + Qsurf
 elif Util_terr == "SOY" or Util_terr == "CNL" and Cond_hydro == 1 and Drai_surf == 1 and Gr_hydroDRAIN > 1:
   return 0 - 55 + Qsurf
 elif Util_terr == "SOY" or Util_terr == "CNL" and Cond_hydro == 1 and Drai_surf == 2:
  return 0 + 0 + Qsurf
 elif Util_terr == "SOY" or Util_terr == "CNL" and Cond_hydro == 1 and Drai_surf == 3:
  return 0 + 55 + Qsurf
 elif Util_terr == "SOY" or Util_terr == "CNL" and Cond_hydro == 2 and Drai_surf == 1 and Gr_hydroDRAIN == 1:
  return 27.5 + 0 + Qsurf
 elif Util_terr == "SOY" or Util_terr == "CNL" and Cond_hydro == 2 and Drai_surf == 1 and Gr_hydroDRAIN > 1:
  return 27.5 - 55 + Qsurf 
 elif Util_terr == "SOY" or Util_terr == "CNL" and Cond_hydro == 2 and Drai_surf == 2:
  return 27.5 + 0 + Qsurf
 elif Util_terr == "SOY" or Util_terr == "CNL" and Cond_hydro == 2 and Drai_surf == 3:
  return 27.5 + 55 + Qsurf
 elif Util_terr == "SOY" or Util_terr == "CNL" and Cond_hydro == 3 and Drai_surf == 1 and Gr_hydroDRAIN == 1:
  return 55 + 0 + Qsurf
 elif Util_terr == "SOY" or Util_terr == "CNL" and Cond_hydro == 3 and Drai_surf == 1 and Gr_hydroDRAIN > 1:
  return 55 - 55 + Qsurf
 elif Util_terr == "SOY" or Util_terr == "CNL" and Cond_hydro == 3 and Drai_surf == 2:
  return 55 + 0 + Qsurf
 elif Util_terr == "SOY" or Util_terr == "CNL" and Cond_hydro == 3 and Drai_surf == 3:
  return 55 + 55 + Qsurf
 elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF" and Cond_hydro == 1 and Drai_surf == 1 and Gr_hydroDRAIN == 1:
  return 0 + 0 + Qsurf 
 elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF" and Cond_hydro == 1 and Drai_surf == 1 and Gr_hydroDRAIN > 1:
  return 0 - 53.4 + Qsurf
 elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF" and Cond_hydro == 1 and Drai_surf == 2:
  return 0 + 0 + Qsurf
 elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF" and Cond_hydro == 1 and Drai_surf == 3:
  return 0 + 53.4 + Qsurf
 elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF" and Cond_hydro == 2 and Drai_surf == 1 and Gr_hydroDRAIN == 1:
  return 26.7 + 0 + Qsurf
 elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF" and Cond_hydro == 2 and Drai_surf == 1 and Gr_hydroDRAIN > 1:
  return 26.7 - 53.4 + Qsurf
 elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF" and Cond_hydro == 2 and Drai_surf == 2:
  return 26.7 + 0 + Qsurf
 elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF" and Cond_hydro == 2 and Drai_surf == 3:
  return 26.7 + 53.4 + Qsurf
 elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF" and Cond_hydro == 3 and Drai_surf == 1 and  Gr_hydroDRAIN == 1:
  return 53.4 + 0 + Qsurf
 elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF" and Cond_hydro == 3 and Drai_surf == 1 and  Gr_hydroDRAIN > 1:
  return 53.4 - 53.4 + Qsurf
 elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF" and Cond_hydro == 3 and Drai_surf == 2:
  return 53.4 + 0 + Qsurf
 elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF" and Cond_hydro == 3 and Drai_surf == 3:
  return 53.4 + 53.4 + Qsurf
 else:
# 2016-10-13 AJOUT DE CETTE PTIE POUR PRENDRE EN COMPTE LES AUTRE UTIL_TERR NON PRESENT DANS MODELE
# [M]
# [CAR]
# [CU]
# [CUI]
# [DH]
# [DS]
# [GOL]
# [SKI]
# [VRG]

  return Qsurf


def calc_Qsurf2(Qsurf2pre, Qsurf):
    if Qsurf2pre < 0:
        return -26.2 + Qsurf
    else:
        return Qsurf2pre


def calc_Qsurf3(Qsurf2, FactQtot, Factruissm):
    if Qsurf2 < 25:
        return 25
    else:
        return Qsurf2 * FactQtot * Factruissm


def calc_Qsurf4(Util_terr, GR_HYDROs, Qsurf, Qsurf2):
 Qsurf4 = 0
 if Qsurf2 - Qsurf < 0 :
  if Util_terr == "MAI" or Util_terr == "MAR":
   return 4.8571 * math.pow((GR_HYDROs - 2), 2) - 12.171 * (GR_HYDROs - 2) + 66.77
  elif Util_terr == "FOI" or Util_terr == "NON":
   return 3.4175 * math.pow((GR_HYDROs - 2), 2) - 7.9543 * (GR_HYDROs - 2) + 30.76
  elif Util_terr == "SOY" or Util_terr == "CNL":
   return 4.9858 * math.pow((GR_HYDROs - 2), 2) - 13.82 * (GR_HYDROs - 2) + 66.88
  elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF":
   return 4.6351 * math.pow((GR_HYDROs - 2), 2) - 11.73 * (GR_HYDROs - 2) + 62.95
  else :
   return 4.8571 * math.pow((GR_HYDROs - 2) + 62.95, 2) - 12.171 * (GR_HYDROs - 2) + 66.771
 else:
  if Util_terr == "MAI" or Util_terr == "MAR":
   return (4.8571 * math.pow((GR_HYDROs - 2), 2) - 12.171 * (GR_HYDROs - 2) + 66.77) + (Qsurf2 - Qsurf)
  elif Util_terr == "FOI" or Util_terr == "NON":
   return (3.4175 * math.pow((GR_HYDROs - 2), 2) - 7.9543 * (GR_HYDROs - 2) + 30.76) + (Qsurf2 - Qsurf)
  elif Util_terr == "SOY" or Util_terr == "CNL":
   return (4.9858 * math.pow((GR_HYDROs - 2), 2) - 13.82 * (GR_HYDROs - 2) + 66.88) + (Qsurf2 - Qsurf)
  elif Util_terr == "AVO" or Util_terr == "ORG" or Util_terr == "BLE" or Util_terr == "AUC" or Util_terr == "MIX" or Util_terr == "PTF":
   return (4.6351 * math.pow((GR_HYDROs - 2), 2) - 11.73 * (GR_HYDROs - 2) + 62.95) + (Qsurf2 - Qsurf)
# AJOUT DE CETTE PTIE POUR INCLURE UTIL_TERR NON PRESENTS
# [M]
# [CAR]
# [CU]
# [CUI]
# [DH]
# [DS]
# [GOL]
# [SKI]
# [VRG]
  else :
   return 4.8571 * math.pow((GR_HYDROs - 2) + 62.95, 2) - 12.171 * (GR_HYDROs - 2) + 66.771
 
 

def calc_Qsout(Drai_Sout, Util_terr, GR_HYDROs, Qsurf2, Qsurf4):
    if Util_terr in ("MAI", "MAR"):
        if Drai_Sout < 3:
            return (2030.2 / math.pow(Qsurf2, 0.4124)) / Drai_Sout
        else:
            if GR_HYDROs == 3:
                return (2030.2 / math.pow(Qsurf4, 0.4124)) * 0.25
            elif GR_HYDROs == 5:
                return (2030.2 / math.pow(Qsurf4, 0.4124)) * 0.2
            else:
                return (2030.2 / math.pow(Qsurf4, 0.4124)) * 0.15
    elif Util_terr in ("FOI", "NON"):
        if Drai_Sout < 3:
            return (1483.6 / math.pow(Qsurf2, 0.4331)) / Drai_Sout
        else:
            if GR_HYDROs == 3:
                return (1483.6 / math.pow(Qsurf4, 0.4331)) * 0.25
            elif GR_HYDROs == 5:
                return (1483.6 / math.pow(Qsurf4, 0.4331)) * 0.2
            else:
                return (1483.6 / math.pow(Qsurf4, 0.4331)) * 0.15
    elif Util_terr in ("SOY", "CNL"):
        if Drai_Sout < 3:
            return (2030.2 / math.pow(Qsurf2, 0.4124)) / Drai_Sout
        else:
            if GR_HYDROs == 3:
                return (2030.2 / math.pow(Qsurf4, 0.4124)) * 0.25
            elif GR_HYDROs == 5:
                return (2030.2 / math.pow(Qsurf4, 0.4124)) * 0.2
            else:
                return (2030.2 / math.pow(Qsurf4, 0.4124)) * 0.15
    elif Util_terr in ("AVO", "ORG", "BLE", "AUC", "MIX", "PTF"):
        if Drai_Sout < 3:
            return (2519.1 / math.pow(Qsurf2, 0.4936)) / Drai_Sout
        else:
            if GR_HYDROs == 3:
                return (2519.1 / math.pow(Qsurf4, 0.4936))* 0.25
            elif GR_HYDROs == 5:
                return (2519.1 / math.pow(Qsurf4, 0.4936)) * 0.2
            else:
                return (2519.1 / math.pow(Qsurf4, 0.4936)) * 0.15
    else:
        if Drai_Sout < 3:
            return (2030.2 / math.pow(Qsurf2, 0.4124)) / Drai_Sout
        else:
            if GR_HYDROs == 3:
                return (2030.2 / math.pow(Qsurf4, 0.4124))* 0.25
            elif GR_HYDROs == 5:
                return (2030.2 / math.pow(Qsurf4, 0.4124)) * 0.2
            else:
                return (2030.2 / math.pow(Qsurf4, 0.4124)) * 0.15


def calc_Qsout2(Qsout, FactQtot):
    if Qsout * FactQtot < 300:
        return Qsout * FactQtot
    else:
        return 300


def calc_FactCa(Trav_sol, Couv_ass, Couv_derob, Util_terr):
    if Couv_ass == 1 or Couv_derob == 1:
        return 0.15
    else:
        if Util_terr in ("MAI", "MAR") :
            if Trav_sol == 1:
                return 0.45
            elif Trav_sol == 2:
                return 0.30
            elif Trav_sol == 3:
                return 0.20
            elif Trav_sol == 4:
                return 0.15
        elif Util_terr in ("SOY", "CNL") :
            if Trav_sol == 1:
                return 0.55
            elif Trav_sol == 2:
                return 0.50
            elif Trav_sol == 3:
                return 0.30
            elif Trav_sol == 4:
                return 0.25
        elif Util_terr in ("AVO", "ORG", "BLE", "AUC", "MIX", "PTF"):
            if Trav_sol == 1:
                return 0.30
            elif Trav_sol == 2:
                return 0.20
            elif Trav_sol == 3:
                return 0.15
            elif Trav_sol == 4:
                return 0.10
        elif Util_terr in ("FOI", "NON"):
            return 0.07
        elif Util_terr == "F":
            return 0.005
        elif Util_terr == "SN":
            return 1
        elif Util_terr in ("EAU", "URB", "ILE"):
            return 0
        elif Util_terr == "Wet":
            return 0.01
        elif Util_terr == "Brsh":
            return 0.05
        elif Util_terr == "NPv":
            return 0.12
        elif Util_terr == "Pve":
            return 0.06
        elif Util_terr == "ResM":
            return 0.06
        elif Util_terr == "ResL":
            return 0.06
        else:
            return 0.03


def calc_FactC(FactCa, Util_terr, Cult_Ante):
    if Cult_Ante in ("FOI", "NON"):
        return FactCa * 0.5
    elif Cult_Ante == "SOY":
        return FactCa * 1.2
    else:
        return FactCa * 1


def calc_Param_a(Trav_sol, Couv_ass, Couv_derob, Util_terr):
    if Couv_ass == 1 or Couv_derob == 1 :
        return 0.5236
    else:
        if Util_terr in ("MAI", "MAR"):
            if Trav_sol == 1:
                return 0.4175
            elif Trav_sol == 2:
                return 0.5158
            elif Trav_sol == 3:
                return 0.5326
            elif Trav_sol == 4:
                return 0.5347
        elif Util_terr in ("FOI", "NON"):
            return 0.5883
        elif  Util_terr in ("SOY", "CNL"):
            if Trav_sol == 1:
                return 0.4455
            elif Trav_sol == 2:
                return 0.5316
            elif Trav_sol == 3:
                return 0.5398
            elif Trav_sol == 4:
                return 0.5404
        elif  Util_terr in ("AVO", "ORG", "BLE", "AUC", "MIX", "PTF"):
            if Trav_sol == 1:
                return 0.4558
            elif Trav_sol == 2:
                return 0.4684
            elif Trav_sol == 3:
                return 0.447
            elif Trav_sol == 4:
                return 0.5163
        elif  Util_terr == "SN":
            return 0.4175
        elif  Util_terr in ("EAU", "CU", "URB", "INO"):
            return 0
        else:
            return 0.5883


def calc_Param_b(Trav_sol, Couv_ass, Couv_derob, Util_terr):
    if Couv_ass == 1 or Couv_derob == 1:
        return -14.892
    else:
        if Util_terr in ("MAI", "MAR") and Trav_sol == 1:
            return -9.6319
        elif Util_terr in ("MAI", "MAR") and Trav_sol == 2:
            return -15.61
        elif Util_terr in ("MAI", "MAR") and Trav_sol == 3:
            return -19.989
        elif Util_terr in ("MAI", "MAR") and Trav_sol == 4:
            return -20.249
        elif Util_terr in ("FOI", "NON") :
            return -13.637
        elif  Util_terr in ("SOY", "CNL") and Trav_sol == 1:
            return -12.89
        elif Util_terr in ("SOY", "CNL") and Trav_sol == 2:
            return -17.398
        elif Util_terr in ("SOY", "CNL") and Trav_sol == 3:
            return -21.345
        elif Util_terr in ("SOY", "CNL") and Trav_sol == 4:
            return -21.377
        elif  Util_terr in ("AVO", "ORG", "BLE", "AUC", "MIX", "PTF") and Trav_sol == 1:
            return -12.863
        elif Util_terr in ("AVO", "ORG", "BLE", "AUC", "MIX", "PTF") and Trav_sol == 2:
            return -12.39
        elif Util_terr in ("AVO", "ORG", "BLE", "AUC", "MIX", "PTF") and Trav_sol == 3:
            return -12.576
        elif Util_terr in ("AVO", "ORG", "BLE", "AUC", "MIX", "PTF") and Trav_sol == 4:
            return -14.659
        elif Util_terr == "SN":
            return  -9.6319
        elif Util_terr in ("EAU", "CU", "URB", "INO"):
            return  0
        else:
            return -13.637


def calc_VolQsurf(Qsurf3):
    return Qsurf3 * 1


def calc_VolQsout(Qsout2):
    return Qsout2 * 1


#Ajout des champs pour le calcul du ruissellement
def add_fields_ruis(urh):
    try:

        #{Ordre de traitement: [Nom du champ, Type de données, Nombre de charactères maximal, Alias]}
        dct_fields = {
        0: ["Modif_GHDRAIN", "SHORT", "#", u"Drainage souterrain"],
        1: ["Gr_hydroDRAIN", "SHORT", "#", u""],
        2: ["Modif_GrHySURF", "SHORT", "#", u"Drainage de surface"],
        3: ["Modif_GrHyPROFIL", "SHORT", "#", u"Hydro profil cultural"],
        4: ["Gr_hydroF", "SHORT", "#", u"Classe hydropédologique"],
        5: ["Gr_hydroF2", "SHORT", "#", u"Classe hydropédologique finale"],
        6: ["Qsurf", "DOUBLE", "#", u""],
        7: ["Qsurf2pre", "DOUBLE", "#", u""],
        8: ["Qsurf2", "DOUBLE", "#", u""],
        9: ["Qsurf3", "DOUBLE", "#", u"Ruissellement (mm/an)"],
        10: ["Qsurf4", "DOUBLE", "#", u""],
        11: ["Qsout", "DOUBLE", "#", u""],
        12: ["Qsout2", "DOUBLE", "#", u"Écoulement aux drains (mm/an)"],
        13: ["FactCa", "DOUBLE", "#", u""],
        14: ["FactC", "DOUBLE", "#", u"Facteur de couverture végétale"],
        15: ["Param_a", "DOUBLE", "#", u""],
        16: ["Param_b", "DOUBLE", "#", u""],
        17: ["VolQsurf", "DOUBLE", "#", u"Volume de ruissellement (mm/an)"],
        18: ["VolQsout", "DOUBLE", "#", u"Volume d’écoulement aux drains (mm/an) "]
        }

        add_fields(urh, dct_fields)

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)


#Calcul du ruissellement
def calc_ruis_export(urh):
    try:
        lst_fields = [
        "Drai_Sout", "GR_HYDROs", "Drai_surf", "Cond_hydro", "Util_terr", "FactQtot", "Factruissm", "Trav_sol", "Couv_ass", "Couv_derob", "Cult_Ante",
        "Modif_GHDRAIN", "Gr_hydroDRAIN", "Modif_GrHySURF", "Modif_GrHyPROFIL", "Gr_hydroF", "Gr_hydroF2", "Qsurf", "Qsurf2pre", "Qsurf2", "Qsurf3", "Qsurf4",
        "Qsout", "Qsout2", "FactCa", "FactC", "Param_a", "Param_b", "VolQsurf", "VolQsout"
        ]

        with arcpy.da.UpdateCursor(urh, lst_fields) as cursor:
            for row in cursor:
                (val_Drai_Sout, val_GR_HYDROs, val_Drai_surf, val_Cond_hydro, val_Util_terr, val_FactQtot, val_Factruissm, val_Trav_sol, val_Couv_ass, val_Couv_derob, val_Cult_Ante,
                val_Modif_GHDRAIN, val_Gr_hydroDRAIN, val_Modif_GrHySURF, val_Modif_GrHyPROFIL, val_Gr_hydroF, val_Gr_hydroF2, val_Qsurf, val_Qsurf2pre,
                val_Qsurf2, val_Qsurf4, val_Qsurf3, val_Qsout, val_Qsout2, val_FactCa, val_FactC, val_Param_a, val_Param_b, val_VolQsurf, val_VolQsout) = row

                new_Modif_GHDRAIN = calc_Modif_GHDRAIN(val_Drai_Sout)
                new_Gr_hydroDRAIN = calc_Gr_hydroDRAIN(val_Drai_Sout, val_GR_HYDROs, new_Modif_GHDRAIN)
                new_Modif_GrHySURF = calc_Modif_GrHySURF(val_Drai_surf)
                new_Modif_GrHyPROFIL = calc_Modif_GrHyPROFIL(val_Cond_hydro, val_GR_HYDROs)
                new_Gr_hydroF = calc_Gr_hydroF(val_GR_HYDROs, new_Modif_GrHySURF, new_Modif_GrHyPROFIL)
                new_Gr_hydroF2 = calc_Gr_hydroF2(new_Gr_hydroF)
                new_Qsurf = calc_Qsurf(val_Util_terr, new_Gr_hydroDRAIN)
                new_Qsurf2pre = calc_Qsurf2pre(val_Util_terr, new_Gr_hydroDRAIN, val_Cond_hydro, val_Drai_surf, new_Qsurf)
                new_Qsurf2 = calc_Qsurf2(new_Qsurf2pre, new_Qsurf)
                new_Qsurf3 = calc_Qsurf3(new_Qsurf2, val_FactQtot, val_Factruissm)
                new_Qsurf4 = calc_Qsurf4(val_Util_terr, val_GR_HYDROs, new_Qsurf, new_Qsurf2)
                new_Qsout = calc_Qsout(val_Drai_Sout, val_Util_terr, val_GR_HYDROs, new_Qsurf2, new_Qsurf4)
                new_Qsout2 = calc_Qsout2(new_Qsout, val_FactQtot)
                new_FactCa = calc_FactCa(val_Trav_sol, val_Couv_ass, val_Couv_derob, val_Util_terr)
                new_FactC = calc_FactC(new_FactCa, val_Util_terr, val_Cult_Ante)
                new_Param_a = calc_Param_a(val_Trav_sol, val_Couv_ass, val_Couv_derob, val_Util_terr)
                new_Param_b = calc_Param_b(val_Trav_sol, val_Couv_ass, val_Couv_derob, val_Util_terr)
                new_VolQsurf = calc_VolQsurf(new_Qsurf3)
                new_VolQsout = calc_VolQsout(new_Qsout2)

                row[-19:] = (
                new_Modif_GHDRAIN, new_Gr_hydroDRAIN, new_Modif_GrHySURF, new_Modif_GrHyPROFIL, new_Gr_hydroF, new_Gr_hydroF2, new_Qsurf, new_Qsurf2pre,
                new_Qsurf2, new_Qsurf3, new_Qsurf4,  new_Qsout, new_Qsout2, new_FactCa, new_FactC, new_Param_a, new_Param_b, new_VolQsurf, new_VolQsout)

                cursor.updateRow(row)

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)



#===========================================
#   Calculs des exportations de sédiments
#===========================================


def update_factK(factK):
    if factK is None:
        return 0.002
    else:
        return factK


def calc_LS1(LS):
    if LS is None:
        return 0.025
    else:
        return LS


def calc_Sed(Param_a, Param_b, factK, LS1, FactC, Qsurf3):
    if (Param_a * Qsurf3 + Param_b) * factK * LS1 * FactC * 7.59 < 0:
        return 0.001
    else:
        return (Param_a * Qsurf3 + Param_b) * factK * LS1 * FactC * 7.59


def calc_Bande_riv2(Bande_riv):
    if Bande_riv > 1:
        return 1 - (0.09 * (Bande_riv - 1) / 2)
    else:
        return 1


def calc_Avaloir2(Avaloir):
    if Avaloir > 1:
        return 1 - (0.145 * (Avaloir - 1) / 2)
    else:
        return 1

def calc_Sed2(Sed, Bande_riv2, Avaloir2):
    return Bande_riv2 * Avaloir2 * Sed * 1000


#Ajout des champs pour le calcul de l'exportation de sédiments
def add_fields_sed(urh):
    try:

        #{Ordre de traitement: [Nom du champ, Type de données, Nombre de charactères maximal, Alias]}
        dct_fields = {
        0: ["LS1", "DOUBLE", "#", u"Facteur LS"],
        1: ["Sed", "DOUBLE", "#", u""],
        2: ["Bande_riv2", "DOUBLE", "#", u""],
        3: ["Avaloir2", "DOUBLE", "#", u""],
        4: ["Sed2", "DOUBLE", "#", u"Sédiments (kg/ha/an)"],
        5: ["Qtesediment", "DOUBLE", "#", u"Volume de sédiments (kg/an)"]
        }

        add_fields(urh, dct_fields)

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)


#Calcul de l'exportation de sédiments
def calc_sed_export(urh):
    try:

        #Update du facteur K
        with arcpy.da.UpdateCursor(urh, ["factK"]) as cursor:
            for row in cursor:
                val_factK = row[0]

                row[0] = update_factK(val_factK)

                cursor.updateRow(row)

        #Calcul des champs
        lst_fields = [
        "LS", "Param_a", "Param_b", "factK", "FactC", "Qsurf3", "Bande_riv", "Avaloir", "Zone_ha2",
        "LS1", "Sed", "Bande_riv2", "Avaloir2", "Sed2", "Qtesediment"
        ]

        with arcpy.da.UpdateCursor(urh, lst_fields) as cursor:
            for row in cursor:
                (val_LS, val_Param_a, val_Param_b, val_factK, val_FactC, val_Qsurf3, val_Bande_riv, val_Avaloir, val_Zone_ha2,
                val_LS1, val_Sed, val_Bande_riv2, val_Avaloir2, val_Sed2, val_Qtesediment) = row

                new_LS1 = calc_LS1(val_LS)
                new_Sed = calc_Sed(val_Param_a, val_Param_b, val_factK, new_LS1, val_FactC, val_Qsurf3)
                new_Bande_riv2 = calc_Bande_riv2(val_Bande_riv)
                new_Avaloir2 = calc_Avaloir2(val_Avaloir)
                new_Sed2 = calc_Sed2(new_Sed, new_Bande_riv2, new_Avaloir2)
                new_Qtesediment = calc_Qte(val_Zone_ha2, new_Sed2)

                row[-6:] = (new_LS1, new_Sed, new_Bande_riv2, new_Avaloir2, new_Sed2, new_Qtesediment)

                cursor.updateRow(row)

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)



#===========================================
#   Calculs des exportations de phosphore
#===========================================

def calc_FactE1(Sed, Qsurf4):
    if Sed > 0 :
        return ((Sed * 1000) / (Qsurf4 * 100))
    else:
        return 0.001
    


def calc_FactE(FactE1):
    if FactE1 > 0:
        return 7.2511 / math.pow(FactE1, 0.25)
    else:
        return 0

def calc_PTOTnaturel(ATOT, STOT):
    if ATOT > 40:
        return 713
    elif ATOT <= 40 and ATOT < (85 - STOT):
        return 537
    else:
        return 634


def calc_PTOTactuel(P_naturel, PTOTnaturel, Pmehlich):
    if P_naturel is None:
        if PTOTnaturel is None:
            return 662
        else:
            return PTOTnaturel
    else:
        return P_naturel + (2.3 * ((Pmehlich / 2.24) - 20))


def calc_Ppartgha(PTOTactuel, FactE, Sed):
    return PTOTactuel * FactE * Sed


def calc_Ppartsurf(Bande_riv2, Avaloir2, Ppartgha):
    return (Bande_riv2 * Avaloir2 * Ppartgha) / 1000


def calc_Con_fermDx(Fum_dose, SatAl_pc, Fum_delai, Fum_per):
    if Fum_dose == 0:
        return 0
    else:
        if Fum_delai == 4 and Fum_per == 0:
            return (1.55 * (40 + 17.1 * SatAl_pc) + 182) * (Fum_dose * 0.4364 / 59) * 1
        elif Fum_delai == 4 and Fum_per == 1:
            return (1.55 * (40 + 17.1 * SatAl_pc) + 182) * (Fum_dose * 0.4364 / 59) * 1
        elif Fum_delai == 4 and Fum_per == 2:
            return (1.55 * (40 + 17.1 * SatAl_pc) + 182) * (Fum_dose * 0.4364 / 59) * 1
        elif Fum_delai == 4 and Fum_per == 3:
            return (1.55 * (40 + 17.1 * SatAl_pc) + 182) * (Fum_dose * 0.4364 / 59) * 1
        elif Fum_delai == 4 and Fum_per == 4:
            return (1.55 * (40 + 17.1 * SatAl_pc) + 182) * (Fum_dose * 0.4364 / 59) * 1
        else:
            return 0


def calc_Con_ferm(Con_fermD1, Con_fermD2, Con_fermD3):
    return Con_fermD1 + Con_fermD2 + Con_fermD3


def calc_PdissSURF(Qsurf3, SatAl_pc, Con_ferm):
    return (50 + SatAl_pc * 17.8 + Con_ferm) * Qsurf3 / 100000


def calc_CPslndrain(Util_terr, ATOT, STOT):
    if Util_terr in ("FOI", "NON"):
        if ATOT > 30:
            return 38
        else:
            if ATOT > 20 and STOT < 70:
                return 50
            else :
                if STOT > 70:
                    return 6
                else :
                    return 62
    else :
        if ATOT > 30:
            return 44
        else:
            if ATOT > 20 and STOT < 70:
                return 51
            else :
                if STOT > 70:
                    return 6
                else :
                    return 57


def calc_PdissDRAIN(Qsout2, CPslndrain):
    if CPslndrain is None:
        return 46 * Qsout2
    else:
        return CPslndrain * Qsout2 / 100000


def calc_CPpartdrain(Util_terr, ATOT, STOT):
    if Util_terr in ("FOI", "NON"):
        if ATOT > 30:
            return 125
        else:
            if ATOT > 20 and STOT < 70:
                return 78
            else:
                if STOT > 70:
                    return 10
                else:
                    return 38
    else:
        if ATOT > 30:
            return 210
        else:
            if ATOT > 20 and STOT < 70:
                return 120
            else:
                if STOT > 70:
                    return 10
                else:
                    return 38


def calc_PparticDRAIN(Qsout2, CPpartdrain):
    if CPpartdrain is None:
        return 230 * Qsout2
    else:
        return CPpartdrain * Qsout2 / 100000


def calc_CPreactdrain(Util_terr, ATOT, STOT):
    if Util_terr in ("FOI", "NON"):
        if ATOT > 30:
            return 25
        else:
            if ATOT > 20 and STOT <= 70:
                return 40
            else:
                if STOT > 70:
                    return 4
                else:
                    return 54
    else:
        if ATOT > 30:
            return 30
        else:
            if ATOT > 20 and STOT <= 70:
                return 42
            else:
                if STOT > 70:
                    return 4
                else:
                    return 54


def calc_PreactDRAIN(Qsout2, CPreactdrain):
    if CPreactdrain is None:
        return 46 * Qsout2
    else:
        return CPreactdrain * Qsout2 / 100


def calc_Eng_min(MINP_B, MINP_V, Util_terr, Trav_sol):
    if Util_terr in ("FOI", "NON") and MINP_B == 0 and MINP_V == 0:
        return (MINP_B * 3.077 * 0.25 / 2.3) + (MINP_V * 3.077 / 2.3) * 0.75
    elif Util_terr not in ("FOI", "NON") and Trav_sol == 4:
        return (MINP_B * 3.077 * 0.25 / 2.3) + (MINP_V * 3.077 / 2.3) * 1
    elif Util_terr not in ("FOI", "NON") and Trav_sol <> 4:
        return (MINP_B * 3.077 * 0.25 / 2.3) + (MINP_V * 3.077 / 2.3) * 0.25


def calc_Eng_fermDx(Fum_dose, Fum_delai, Fum_per):
    if Fum_dose == 0:
        return 0
    else:
        if Fum_per == 0:
            if Fum_delai == 0:
                return Fum_dose * 3.077 / 2.3 * 1 * 1
            elif Fum_delai == 1:
                return Fum_dose * 3.077 / 2.3 * 0.25 * 1
            elif Fum_delai == 2:
                return Fum_dose * 3.077 / 2.3 * 0.5 * 1
            elif Fum_delai == 3:
                return Fum_dose * 3.077 / 2.3 * 1 * 1
            elif Fum_delai == 4:
                return Fum_dose * 3.077 / 2.3 * 1 * 1
        elif Fum_per == 1:
            if Fum_delai == 0:
                return Fum_dose * 3.077 / 2.3 * 1 * 1
            elif Fum_delai == 1:
                return Fum_dose * 3.077 / 2.3 * 0.25 * 1
            elif Fum_delai == 2:
                return Fum_dose * 3.077 / 2.3 * 0.5 * 1
            elif Fum_delai == 3:
                return Fum_dose * 3.077 / 2.3 * 1 * 1
            elif Fum_delai == 4:
                return Fum_dose * 3.077 / 2.3 * 1 * 1
        elif Fum_per == 2:
            if Fum_delai == 0:
                return Fum_dose * 3.077 / 2.3 * 1 * 0.5
            elif Fum_delai == 1:
                return Fum_dose * 3.077 / 2.3 * 0.25 * 0.5
            elif Fum_delai == 2:
                return Fum_dose * 3.077 / 2.3 * 0.5 * 0.5
            elif Fum_delai == 3:
                return Fum_dose * 3.077 / 2.3 * 1 * 0.5
            elif Fum_delai == 4:
                return Fum_dose * 3.077 / 2.3 * 1 * 0.5
        elif Fum_per == 3:
            if Fum_delai == 0:
                return Fum_dose * 3.077 / 2.3 * 1 * 0.5
            elif Fum_delai == 1:
                return Fum_dose * 3.077 / 2.3 * 0.25 * 0.5
            elif Fum_delai == 2:
                return Fum_dose * 3.077 / 2.3 * 0.5 * 0.5
            elif Fum_delai == 3:
                return Fum_dose * 3.077 / 2.3 * 1 * 0.5
            elif Fum_delai == 4:
                return Fum_dose * 3.077 / 2.3 * 1 * 0.5
        elif Fum_per == 4:
            if Fum_delai == 0:
                return Fum_dose * 3.077 / 2.3 * 1 * 1
            elif Fum_delai == 1:
                return Fum_dose * 3.077 / 2.3 * 0.25 * 1
            elif Fum_delai == 2:
                return Fum_dose * 3.077 / 2.3 * 0.5 * 1
            elif Fum_delai == 3:
                return Fum_dose * 3.077 / 2.3 * 1 * 1
            elif Fum_delai == 4:
                return Fum_dose * 3.077 / 2.3 * 1 * 1


def calc_Eng_ferm(Eng_fermD1, Eng_fermD2, Eng_fermD3):
    return Eng_fermD1 + Eng_fermD2 + Eng_fermD3


def calc_Ptotactuel2(P_naturel, PTOTnaturel, Pmehlich, Eng_ferm, Eng_min):
    if P_naturel == 0:
        if PTOTnaturel == 0:
            return 662
        else:
            return PTOTnaturel
    else:
        if Eng_min == 0:
            if Eng_ferm == 0:
                return P_naturel + (2.3 * (((Pmehlich + 0 + 0) / 2.24) - 20))
            else:
                return P_naturel + (2.3 * (((Pmehlich + 0 + Eng_ferm) / 2.24) - 20))
        else:
            if Eng_ferm == 0:
                return P_naturel + (2.3 * (((Pmehlich + Eng_min + 0) / 2.24) - 20))
            else:
                return P_naturel + (2.3 * (((Pmehlich + Eng_min + Eng_ferm) / 2.24) - 20))


def calc_Pparthafert(Ptotactuel2, FactE, Sed, Ppartgha):
    return Ptotactuel2 * FactE * Sed - Ppartgha


def calc_Ppartfert(Bande_riv2, Avaloir2, Pparthafert):
    return Bande_riv2 * Avaloir2 * Pparthafert / 1000


def calc_TotPm3(Eng_min, Eng_ferm, Pmehlich):
    if Eng_min == 0:
        if Eng_ferm == 0:
            return Pmehlich + 0 + 0
        else:
            return Pmehlich + 0 + Eng_ferm
    else:
        if Eng_ferm == 0:
            return Pmehlich + Eng_min + 0
        else:
            return Pmehlich + Eng_min + Eng_ferm


def calc_TOTSatAL(TotPm3, Pmehlich, SatAl_pc):
    if (Pmehlich and SatAl_pc) > 0:
        return TotPm3 / (Pmehlich * 100 / SatAl_pc) * 100
    else:
        return 0


def calc_Pslnsurffert(TOTSatAl, PdissSURF, Qsurf3):
    if (((50 + 17.8 * TOTSatAl) * Qsurf3 / 100) - PdissSURF * 1000) < 0:
        return 0
    else:
        return (((50 + 17.8 * TOTSatAl) * Qsurf3 / 100) - (PdissSURF * 1000)) / 1000


def calc_Preactsurf(TOTSatAl, Qsurf4):
    return (40 + 17.1 * TOTSatAl) * Qsurf4 / 100


def calc_Ptotal(Ppartsurf, PdissSURF, PparticDRAIN, PdissDRAIN, Ppartfert, Pslnsurffert):
    return Ppartsurf + PdissSURF + PparticDRAIN + PdissDRAIN + Ppartfert + Pslnsurffert


def calc_PTotalTOUT(Util_terr, Ptotal):
    if Util_terr == "Brsh":
        return 0.18
    elif Util_terr in ("Wet", "ResM", "CU"):
        return 0.72
    elif Util_terr == "ResL":
        return 0.61
    elif Util_terr in ("F", "M", "R"):
        return 0.14
    elif Util_terr in ("DH", "INO"):
        return 0.72
    elif Util_terr in ("BHE", "ILE", "EAU"):
        return 0.00006
    elif Util_terr in ("CAR", "DEM", "GR", "GOL"):
        return 0.00006
    elif Util_terr == "NPv":
        return 0.78
    elif Util_terr == "Pve":
        return 1.17
    else:
        return Ptotal


def calc_Pbio1(Ppartgha, Pparthafert, PparticDRAIN, TotPm3, Preactsurf, PreactDRAIN):
    return ((Ppartgha + Pparthafert + (PparticDRAIN * 1000)) * (14.858 * (math.pow(TotPm3, 0.2814)) / 100) + Preactsurf + PreactDRAIN) / 1000


#Ajout des champs pour le calcul de l'exportation de phosphore
def add_fields_phos(urh):
    try:

        #{Ordre de traitement: [Nom du champ, Type de données, Nombre de charactères maximal, Alias]}
        dct_fields = {
        0: ["FactE1", "DOUBLE", "#",u"Facteur d’enrichissement du sol1"],
        1: ["FactE", "DOUBLE", "#", u"Facteur d’enrichissement du sol"],
        2: ["PTOTnaturel", "DOUBLE", "#", u""],
        3: ["PTOTactuel", "DOUBLE", "#", u""],
        4: ["Ppartgha", "DOUBLE", "#", u""],
        5: ["Ppartsurf", "DOUBLE", "#", u"Phosphore particulaire - Ruissellement (kg/ha/an)"],
        6: ["Con_fermD1", "DOUBLE", "#", u""],
        7: ["Con_fermD2", "DOUBLE", "#", u""],
        8: ["Con_fermD3", "DOUBLE", "#", u""],
        9: ["Con_ferm", "DOUBLE", "#", u""],
        10: ["PdissSURF", "DOUBLE", "#", u"Phosphore soluble - Ruissellement (kg/ha/an)"],
        11: ["CPslndrain", "DOUBLE", "#", u""],
        12: ["PdissDRAIN", "DOUBLE", "#", u"Phosphore soluble - Drains (kg/ha/an)"],
        13: ["CPpartdrain", "DOUBLE", "#", u""],
        14: ["PparticDRAIN", "DOUBLE", "#", u"Phosphore particulaire - Drains (kg/ha/an)"],
        15: ["CPreactdrain", "DOUBLE", "#", u""],
        16: ["PreactDRAIN", "DOUBLE", "#", u"Phosphore réactif dissous - Drains (kg/ha/an)"],
        17: ["Eng_min", "DOUBLE", "#", u"Enrichissement en P Mehlich-3 - Engrais minéraux"],
        18: ["Eng_fermD1", "DOUBLE", "#", u""],
        19: ["Eng_fermD2", "DOUBLE", "#", u""],
        20: ["Eng_fermD3", "DOUBLE", "#", u""],
        21: ["Eng_ferm", "DOUBLE", "#", u"Enrichissement en P Mehlich-3 - Engrais de ferme"],
        22: ["Ptotactuel2", "DOUBLE", "#", u""],
        23: ["Pparthafert", "DOUBLE", "#", u""],
        24: ["Ppartfert", "DOUBLE", "#", u"Phosphore particulaire - Fertilisation (kg/ha/an)"],
        25: ["TotPm3", "DOUBLE", "#", u""],
        26: ["TOTSatAl", "DOUBLE", "#", u""],
        27: ["Pslnsurffert", "DOUBLE", "#", u"Phosphore soluble - Fertilisation (kg/ha/an)"],
        28: ["Preactsurf", "DOUBLE", "#", u"Phosphore réactif dissous - Ruissellement (kg/ha/an)"],
        29: ["Ptotal", "DOUBLE", "#", u"Phosphore total - Secteurs en culture (kg/ha/an)"],
        30: ["PTotalTOUT", "DOUBLE", "#", u"Phosphore total - Tous les secteurs (kg/ha/an)"],
        31: ["Pbio1", "DOUBLE", "#", u"Phosphore biodisponible (kg/ha/an)"],
        32: ["QtePpartsurf", "DOUBLE", "#", u"Volume de phosphore particulaire - Ruissellement (kg/an)"],
        33: ["QtePdisssurf", "DOUBLE", "#", u"Volume de phosphore soluble - Ruissellement (kg/an)"],
        34: ["QtePpartdrain", "DOUBLE", "#", u"Volume de phosphore particulaire - Drains (kg/an)"],
        35: ["QtePslndrain", "DOUBLE", "#", u"Volume de phosphore soluble - Drains (kg/an)"],
        36: ["QtePpartfert", "DOUBLE", "#", u"Volume de phosphore particulaire - Fertilisation (kg/an)"],
        37: ["QtePslnfert", "DOUBLE", "#", u"Volume de phosphore soluble - Fertilisation (kg/an)"],
        38: ["QtePtotal", "DOUBLE", "#", u"Volume de phosphore total - Secteurs en culture (kg/an)"],
        39: ["QtePTotalTOUT", "DOUBLE", "#", u"Volume de phosphore total - Tous les secteurs (kg/an)"],
        40: ["QtePbio", "DOUBLE", "#", u"Volume de phosphore biodisponible (kg/an)"]
        }

        add_fields(urh, dct_fields)

    except:
        msg = get_error()
        write_msg(log_txt, msg, True, True)
        sys.exit(1)


#Calcul de l'exportation de phosphore
#Ajout des champs pour le calcul de l'exportation de phosphore
def calc_phos_export(urh):
    try:
    # Get a list of the featureclasses in the input folder


       arcpy.CalculateField_management(urh, "FactE1", "(!Sed! *1000 / !Qsurf4! *100)", "PYTHON_9.3", "")

       arcpy.CalculateField_management(urh, "FactE", "FactE (!FactE1!)", "PYTHON", "import math \\ndef FactE (FactE1):\\n return 7.2511 /math.pow(FactE1, 0.25)\\n")

       arcpy.CalculateField_management(urh, "PTOTnaturel", "PTOTnaturel(!ATOT!, !STOT!)", "PYTHON", "def PTOTnaturel(ATOT, STOT):\\n if ATOT > 40:\\n  return 713\\n elif ATOT <= 40 and ATOT < (85-STOT):\\n  return 537\\n else :\\n   return 634\\n")

       # Process: Ajouter un champ (11)
       arcpy.CalculateField_management(urh, "PTOTactuel", "PTOTactuel(!P_naturel!, !PTOTnaturel!, !Pmehlich!)", "PYTHON", "def PTOTactuel (P_naturel, PTOTnaturel, Pmehlich):\\n if P_naturel == None :\\n   if PTOTnaturel == None:\\n    return 662\\n   else : \\n    return PTOTnaturel\\n else : \\n  return P_naturel + (2.3 *((Pmehlich/2.24)-20))\\n")

       arcpy.CalculateField_management(urh, "Ppartgha", "[PTOTactuel] * [FactE] * [Sed]", "VB", "")




		# Process: Calculer un champ (27)

       arcpy.CalculateField_management(urh, "Ppartsurf", "(!Bande_riv2! * !Avaloir2! * !Ppartgha!) / 1000", "PYTHON", "")

		# Process: Calculer un champ (51)
       arcpy.CalculateField_management(urh, "Ppartsurf", "updateValue ( !Ppartsurf!)", "PYTHON_9.3", "def updateValue(value):\\n  if value == None:\\n   return '0'\\n  else: return value")


		# Process: Calculer un champ (70)
       arcpy.CalculateField_management(urh, "Con_fermD1", "Con_fermD1( !FUMP_DOSE! , !SatAl_pc! , !FUM1_DELAI!, !FUM1_PER! )", "PYTHON_9.3", "def Con_fermD1(FumP_dose,SatAl_pc, Fum1_delai, Fum1_per):\\n if FumP_dose == 0 :\\n  return 0\\n elif FumP_dose != 0 and Fum1_delai == 4 and Fum1_per == 0:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP_dose * 0.4364 / 59)*1\\n elif FumP_dose != 0 and Fum1_delai == 4 and Fum1_per == 1:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP_dose * 0.4364 / 59)*1\\n elif FumP_dose != 0 and Fum1_delai == 4 and Fum1_per == 2:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP_dose * 0.4364 / 59)*1\\n elif FumP_dose != 0 and Fum1_delai == 4 and Fum1_per == 3:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP_dose * 0.4364 / 59)*1\\n elif FumP_dose != 0 and Fum1_delai == 4 and Fum1_per == 4:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP_dose * 0.4364 / 59)*1\\n else :\\n  return 0")


		# Process: Calculer un champ (71)
       arcpy.CalculateField_management(urh, "Con_fermD2", "Con_fermD2( !FUMP2_DOSE! , !SatAl_pc! , !FUM2_DELAI! , !FUM2_PER! )", "PYTHON_9.3", "def Con_fermD2(FumP2_dose,SatAl_pc, Fum2_delai, Fum2_per):\\n if FumP2_dose == 0 :\\n  return 0\\n elif FumP2_dose != 0 and Fum2_delai == 4 and Fum2_per == 0:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP2_dose * 0.4364 / 59)*1\\n elif FumP2_dose != 0 and Fum2_delai == 4 and Fum2_per == 1:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP2_dose * 0.4364 / 59)*1\\n elif FumP2_dose != 0 and Fum2_delai == 4 and Fum2_per == 2:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP2_dose * 0.4364 / 59)*1\\n elif FumP2_dose != 0 and Fum2_delai == 4 and Fum2_per == 3:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP2_dose * 0.4364 / 59)*1\\n elif FumP2_dose != 0 and Fum2_delai == 4 and Fum2_per == 4:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP2_dose * 0.4364 / 59)*1\\n else :\\n  return 0")


		# Process: Calculer un champ (72)
       arcpy.CalculateField_management(urh, "Con_fermD3", "Con_fermD3(!FUMP3_DOSE! , !SatAl_pc! , !FUM3_DELAI! , !FUM3_PER! )", "PYTHON_9.3", "def Con_fermD3(FumP3_dose,SatAl_pc, Fum3_delai, Fum3_per):\\n if FumP3_dose == 0 :\\n  return 0\\n elif FumP3_dose != 0 and Fum3_delai == 4 and Fum3_per == 0:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP3_dose * 0.4364 / 59)*1\\n elif FumP3_dose != 0 and Fum3_delai == 4 and Fum3_per == 1:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP3_dose * 0.4364 / 59)*1\\n elif FumP3_dose != 0 and Fum3_delai == 4 and Fum3_per == 2:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP3_dose * 0.4364 / 59)*1\\n elif FumP3_dose != 0 and Fum3_delai == 4 and Fum3_per == 3:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP3_dose * 0.4364 / 59)*1\\n elif FumP3_dose != 0 and Fum3_delai == 4 and Fum3_per == 4:\\n  return (1.55*(40 + 17.1 * SatAl_pc)+182)*(FumP3_dose * 0.4364 / 59)*1\\n else :\\n  return 0\\n")


		# Process: Calculer un champ (73)
       arcpy.CalculateField_management(urh, "Con_ferm", "[Con_fermD1]+ [Con_fermD2]+ [Con_fermD3]", "VB", "")


		# Process: Calculer un champ (28)
       arcpy.CalculateField_management(urh, "PdissSURF", "(50 + !SatAl_pc! *17.8 + !Con_ferm! )* !Qsurf3! /100000 ", "PYTHON_9.3", "")

		# Process: Calculer un champ (65)
       arcpy.CalculateField_management(urh, "PdissSURF", "updateValue( !PdissSURF! )", "PYTHON_9.3", "def updateValue(value):\\n  if value == None:\\n   return '0'\\n  else: return value")


		# Process: Calculer un champ (30)
       arcpy.CalculateField_management(urh, "CPslndrain", "CPslndrain(!Util_terr!, !ATOT!, !STOT!)", "PYTHON", "def CPslndrain (Util_terr, ATOT, STOT):\\n if Util_terr == \"FOI\" or Util_terr == \"NON\":\\n  if ATOT > 30:\\n   return 38\\n  else: \\n   if ATOT > 20 and STOT < 70:\\n    return 50\\n   else : \\n    if STOT > 70 :\\n     return 6\\n    else :\\n     return 62\\n else :  \\n  if ATOT > 30:\\n   return 44\\n  else: \\n   if ATOT > 20 and STOT < 70:\\n    return 51\\n   else : \\n    if STOT > 70 :\\n     return 6\\n    else :\\n     return 57")


		# Process: Calculer un champ (29)
       arcpy.CalculateField_management(urh, "PdissDRAIN", "PdissDRAIN(!Qsout2!, !CPslndrain!)", "PYTHON", "def PdissDRAIN (Qsout2, CPslndrain):\\n if CPslndrain == None :\\n  return 46 * Qsout2 \\n else : \\n  return CPslndrain * Qsout2 / 100000")

		# Process: Calculer un champ (66)
       arcpy.CalculateField_management(urh, "PdissDRAIN", "updateValue( !PdissDRAIN! )", "PYTHON", "def updateValue(value):\\n  if value == None:\\n   return '0'\\n  else: return value")


		# Process: Calculer un champ (32)
       arcpy.CalculateField_management(urh, "CPpartdrain", "CPpartdrain(!Util_terr!, !ATOT!, !STOT!)", "PYTHON", "def CPpartdrain (Util_terr, ATOT, STOT):\\n if Util_terr == \"FOI\" or \"NON\":\\n  if ATOT > 30:\\n   return 125\\n  else: \\n   if ATOT > 20 and STOT < 70:\\n    return 78\\n   else : \\n    if STOT > 70 :\\n     return 10\\n    else :\\n     return 38\\n else :  \\n  if ATOT > 30:\\n   return 210\\n  else: \\n   if ATOT > 20 and STOT < 70:\\n    return 120\\n   else : \\n    if STOT > 70 :\\n     return 10\\n    else :\\n     return 38")


		# Process: Calculer un champ (31)
       arcpy.CalculateField_management(urh, "PparticDRAIN", "PparticDRAIN(!Qsout2!, !CPpartdrain!)", "PYTHON", "def PparticDRAIN (Qsout2, CPpartdrain):\\n if CPpartdrain == None :\\n  return 230 * Qsout2\\n else : \\n  return CPpartdrain * Qsout2 / 100000")

		# Process: Calculer un champ (67)
       arcpy.CalculateField_management(urh, "PparticDRAIN", "updateValue( !PparticDRAIN! )", "PYTHON", "def updateValue(value):\\n  if value == None:\\n   return '0'\\n  else: return value")


		# Process: Calculer un champ (34)
       arcpy.CalculateField_management(urh, "CPreactdrain", "CPreactdrain(!Util_terr!, !ATOT!, !STOT!)", "PYTHON", "def CPreactdrain (Util_terr, ATOT, STOT):\\n if Util_terr == \"FOI\" or Util_terr == \"NON\":\\n  if ATOT > 30:\\n   return 25\\n  else: \\n   if ATOT > 20 and STOT <= 70:\\n    return 40\\n   else : \\n    if STOT > 70 :\\n     return 4\\n    else :\\n     return 54\\n else :  \\n  if ATOT > 30:\\n   return 30\\n  else: \\n   if ATOT > 20 and STOT <= 70:\\n    return 42\\n   else : \\n    if STOT > 70 :\\n     return 4\\n    else :\\n     return 54")


		# Process: Calculer un champ (33)
       arcpy.CalculateField_management(urh, "PreactDRAIN", "PreactDRAIN(!Qsout2!, !CPreactdrain!)", "PYTHON", "def PreactDRAIN (Qsout2, CPreactdrain):\\n if CPreactdrain == None :\\n  return 46 * Qsout2\\n else : \\n  return CPreactdrain * Qsout2 / 100")


		# Process: Calculer un champ (35)
       arcpy.CalculateField_management(urh, "Eng_min", "Eng_min(!MINP_B!, !MINP_V!, !Util_terr!, !Trav_sol!)", "PYTHON_9.3", "def Eng_min(MINP_B, MINP_V, Util_terr, Trav_sol):\\n if Util_terr == \"FOI\" or Util_terr == \"NON\" and MINP_B == 0 and MINP_V == 0:\\n  return (MINP_B * 3.077 *0.25 / 2.3) + (MINP_V * 3.077 / 2.3)* 0.75\\n elif Util_terr != \"FOI\" or Util_terr != \"NON\" and Trav_sol == 4 :\\n  return (MINP_B * 3.077 *0.25 / 2.3) + (MINP_V * 3.077 / 2.3)* 1\\n elif Util_terr != \"FOI\" or Util_terr == \"NON\" and Trav_Sol != 4 :\\n  return (MINP_B * 3.077 *0.25 / 2.3) + (MINP_V * 3.077 / 2.3)* 0.25")


		# Process: Calculer un champ (36)
       arcpy.CalculateField_management(urh, "Eng_fermD1", "Eng_fermD1(!FumP_dose!, !Fum1_delai!, !Fum1_per!, !FumP2_dose!, !Fum2_delai!, !Fum2_per!,!FumP3_dose!, !Fum3_delai!, !Fum3_per!)", "PYTHON_9.3", "def Eng_fermD1(FumP_dose, Fum1_delai, Fum1_per, FumP2_dose, Fum2_delai, Fum2_per, FumP3_dose, Fum3_delai, Fum3_per):\\n if FumP_dose == 0 :\\n  return 0 \\n elif FumP_dose != 0 and Fum1_delai == 0 and Fum1_per == 0: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP_dose != 0 and Fum1_delai == 1 and Fum1_per == 0: \\n  return FumP_dose * 3.077 / 2.3 * 0.25 * 1\\n elif FumP_dose != 0 and Fum1_delai == 2 and Fum1_per == 0: \\n  return FumP_dose * 3.077 / 2.3 * 0.5 * 1\\n elif FumP_dose != 0 and Fum1_delai == 3 and Fum1_per == 0: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP_dose != 0 and Fum1_delai == 4 and Fum1_per == 0: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP_dose != 0 and Fum1_delai == 0 and Fum1_per == 1: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP_dose != 0 and Fum1_delai == 1 and Fum1_per == 1: \\n  return FumP_dose * 3.077 / 2.3 * 0.25 * 1\\n elif FumP_dose != 0 and Fum1_delai == 2 and Fum1_per == 1: \\n  return FumP_dose * 3.077 / 2.3 * 0.5 * 1\\n elif FumP_dose != 0 and Fum1_delai == 3 and Fum1_per == 1: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP_dose != 0 and Fum1_delai == 4 and Fum1_per == 1: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP_dose != 0 and Fum1_delai == 0 and Fum1_per == 2: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP_dose != 0 and Fum1_delai == 1 and Fum1_per == 2: \\n  return FumP_dose * 3.077 / 2.3 * 0.25 * 0.5\\n elif FumP_dose != 0 and Fum1_delai == 2 and Fum1_per == 2: \\n  return FumP_dose * 3.077 / 2.3 * 0.5 * 0.5\\n elif FumP_dose != 0 and Fum1_delai == 3 and Fum1_per == 2: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP_dose != 0 and Fum1_delai == 4 and Fum1_per == 2: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP_dose != 0 and Fum1_delai == 0 and Fum1_per == 3: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP_dose != 0 and Fum1_delai == 1 and Fum1_per == 3: \\n  return FumP_dose * 3.077 / 2.3 * 0.25 * 0.5\\n elif FumP_dose != 0 and Fum1_delai == 2 and Fum1_per == 3: \\n  return FumP_dose * 3.077 / 2.3 * 0.5 * 0.5\\n elif FumP_dose != 0 and Fum1_delai == 3 and Fum1_per == 3: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP_dose != 0 and Fum1_delai == 4 and Fum1_per == 3: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP_dose != 0 and Fum1_delai == 0 and Fum1_per == 4: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP_dose != 0 and Fum1_delai == 1 and Fum1_per == 4: \\n  return FumP_dose * 3.077 / 2.3 * 0.25 * 1\\n elif FumP_dose != 0 and Fum1_delai == 2 and Fum1_per == 4: \\n  return FumP_dose * 3.077 / 2.3 * 0.5 * 1\\n elif FumP_dose != 0 and Fum1_delai == 3 and Fum1_per == 4: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP_dose != 0 and Fum1_delai == 4 and Fum1_per == 4: \\n  return FumP_dose * 3.077 / 2.3 * 1 * 1")


		# Process: Calculer un champ (37)
       arcpy.CalculateField_management(urh, "Eng_fermD2", "Eng_fermD2(!FumP_dose!, !Fum1_delai!, !Fum1_per!, !FumP2_dose!, !Fum2_delai!, !Fum2_per!,!FumP3_dose!, !Fum3_delai!, !Fum3_per!)", "PYTHON", "def Eng_fermD2(FumP_dose, Fum1_delai, Fum1_per, FumP2_dose, Fum2_delai, Fum2_per, FumP3_dose, Fum3_delai, Fum3_per):\\n if FumP2_dose == 0 :\\n  return 0 \\n elif FumP2_dose != 0 and Fum2_delai == 0 and Fum2_per == 0: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 1 and Fum2_per == 0: \\n  return FumP2_dose * 3.077 / 2.3 * 0.25 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 2 and Fum2_per == 0: \\n  return FumP2_dose * 3.077 / 2.3 * 0.5 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 3 and Fum2_per == 0: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 4 and Fum2_per == 0: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 0 and Fum2_per == 1: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 1 and Fum2_per == 1: \\n  return FumP2_dose * 3.077 / 2.3 * 0.25 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 2 and Fum2_per == 1: \\n  return FumP2_dose * 3.077 / 2.3 * 0.5 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 3 and Fum2_per == 1: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 4 and Fum2_per == 1: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 0 and Fum2_per == 2: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP2_dose != 0 and Fum2_delai == 1 and Fum2_per == 2: \\n  return FumP2_dose * 3.077 / 2.3 * 0.25 * 0.5\\n elif FumP2_dose != 0 and Fum2_delai == 2 and Fum2_per == 2: \\n  return FumP2_dose * 3.077 / 2.3 * 0.5 * 0.5\\n elif FumP2_dose != 0 and Fum2_delai == 3 and Fum2_per == 2: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP2_dose != 0 and Fum2_delai == 4 and Fum2_per == 2: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP2_dose != 0 and Fum2_delai == 0 and Fum2_per == 3: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP2_dose != 0 and Fum2_delai == 1 and Fum2_per == 3: \\n  return FumP2_dose * 3.077 / 2.3 * 0.25 * 0.5\\n elif FumP2_dose != 0 and Fum2_delai == 2 and Fum2_per == 3: \\n  return FumP2_dose * 3.077 / 2.3 * 0.5 * 0.5\\n elif FumP2_dose != 0 and Fum2_delai == 3 and Fum2_per == 3: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP2_dose != 0 and Fum2_delai == 4 and Fum2_per == 3: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP2_dose != 0 and Fum2_delai == 0 and Fum2_per == 4: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 1 and Fum2_per == 4: \\n  return FumP2_dose * 3.077 / 2.3 * 0.25 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 2 and Fum2_per == 4: \\n  return FumP2_dose * 3.077 / 2.3 * 0.5 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 3 and Fum2_per == 4: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP2_dose != 0 and Fum2_delai == 4 and Fum2_per == 4: \\n  return FumP2_dose * 3.077 / 2.3 * 1 * 1")


		# Process: Calculer un champ (38)
       arcpy.CalculateField_management(urh, "Eng_fermD3", "Eng_fermD3(!FumP_dose!, !Fum1_delai!, !Fum1_per!, !FumP2_dose!, !Fum2_delai!, !Fum2_per!,!FumP3_dose!, !Fum3_delai!, !Fum3_per!)", "PYTHON", "def Eng_fermD3(FumP_dose, Fum1_delai, Fum1_per, FumP2_dose, Fum2_delai, Fum2_per, FumP3_dose, Fum3_delai, Fum3_per):\\n if FumP3_dose == 0 :\\n  return 0 \\n elif FumP3_dose != 0 and Fum3_delai == 0 and Fum3_per == 0: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 1 and Fum3_per == 0: \\n  return FumP3_dose * 3.077 / 2.3 * 0.25 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 2 and Fum3_per == 0: \\n  return FumP3_dose * 3.077 / 2.3 * 0.5 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 3 and Fum3_per == 0: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 4 and Fum3_per == 0: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 0 and Fum3_per == 1: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 1 and Fum3_per == 1: \\n  return FumP3_dose * 3.077 / 2.3 * 0.25 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 2 and Fum3_per == 1: \\n  return FumP3_dose * 3.077 / 2.3 * 0.5 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 3 and Fum3_per == 1: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 4 and Fum3_per == 1: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 0 and Fum3_per == 2: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP3_dose != 0 and Fum3_delai == 1 and Fum3_per == 2: \\n  return FumP3_dose * 3.077 / 2.3 * 0.25 * 0.5\\n elif FumP3_dose != 0 and Fum3_delai == 2 and Fum3_per == 2: \\n  return FumP3_dose * 3.077 / 2.3 * 0.5 * 0.5\\n elif FumP3_dose != 0 and Fum3_delai == 3 and Fum3_per == 2: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP3_dose != 0 and Fum3_delai == 4 and Fum3_per == 2: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP3_dose != 0 and Fum3_delai == 0 and Fum3_per == 3: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP3_dose != 0 and Fum3_delai == 1 and Fum3_per == 3: \\n  return FumP3_dose * 3.077 / 2.3 * 0.25 * 0.5\\n elif FumP3_dose != 0 and Fum3_delai == 2 and Fum3_per == 3: \\n  return FumP3_dose * 3.077 / 2.3 * 0.5 * 0.5\\n elif FumP3_dose != 0 and Fum3_delai == 3 and Fum3_per == 3: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP3_dose != 0 and Fum3_delai == 4 and Fum3_per == 3: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 0.5\\n elif FumP3_dose != 0 and Fum3_delai == 0 and Fum3_per == 4: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 1 and Fum3_per == 4: \\n  return FumP3_dose * 3.077 / 2.3 * 0.25 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 2 and Fum3_per == 4: \\n  return FumP3_dose * 3.077 / 2.3 * 0.5 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 3 and Fum3_per == 4: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 1\\n elif FumP3_dose != 0 and Fum3_delai == 4 and Fum3_per == 4: \\n  return FumP3_dose * 3.077 / 2.3 * 1 * 1")


		# Process: Calculer un champ (39)
       arcpy.CalculateField_management(urh, "Eng_ferm", "[Eng_fermD1] + [Eng_fermD2] + [Eng_fermD3]", "VB", "")


		# Process: Calculer un champ (40)
       arcpy.CalculateField_management(urh, "Ptotactuel2", "Ptotactuel2(!P_naturel!, !PTOTnaturel!, !Pmehlich!, !Eng_ferm!, !Eng_min!)", "PYTHON", "def Ptotactuel2 (P_naturel, PTOTnaturel, Pmehlich, Eng_ferm, Eng_min):\\n if P_naturel == 0:\\n   if PTOTnaturel == 0:\\n    return 662\\n   else : \\n    return PTOTnaturel\\n else : \\n  if Eng_min == 0 and Eng_ferm == 0:\\n   return P_naturel + (2.3 *(((Pmehlich+0+0)/2.24)-20))\\n  elif Eng_min == 0 and Eng_ferm != 0:\\n   return P_naturel + (2.3 *(((Pmehlich+0+Eng_ferm)/2.24)-20))\\n  elif Eng_min != 0 and Eng_ferm == 0:\\n   return P_naturel + (2.3 *(((Pmehlich+Eng_min+0)/2.24)-20))\\n  elif Eng_min != 0 and Eng_ferm != 0:\\n   return P_naturel + (2.3 *(((Pmehlich+Eng_min+Eng_ferm)/2.24)-20))")


		# Process: Calculer un champ (41)
       arcpy.CalculateField_management(urh, "Pparthafert", "!Ptotactuel2! * !FactE! * !Sed! - !Ppartgha!", "PYTHON_9.3", "")


		# Process: Calculer un champ (42)
       arcpy.CalculateField_management(urh, "Ppartfert", "!Bande_riv2! * !Avaloir2! * !Pparthafert! / 1000", "PYTHON", "")

		# Process: Calculer un champ (68)
       arcpy.CalculateField_management(urh, "Ppartfert", "updateValue( !Ppartfert! )", "PYTHON", "def updateValue(value):\\n  if value == None:\\n   return '0'\\n  else: return value")


		# Process: Calculer un champ (43)
       arcpy.CalculateField_management(urh, "TotPm3", "TotPm3(!Eng_min!, !Eng_ferm!, !Pmehlich!)", "PYTHON", "def TotPm3(Eng_min, Eng_ferm, Pmehlich):\\n if Eng_min != 0 and Eng_ferm != 0:\\n  return Pmehlich+Eng_min+Eng_ferm\\n elif Eng_min != 0 and Eng_ferm == 0:\\n  return Pmehlich+Eng_min+0\\n elif Eng_min == 0 and Eng_ferm != 0:\\n  return Pmehlich+0+Eng_ferm\\n else :\\n  return Pmehlich+0+0")


		# Process: Calculer un champ (44)
       arcpy.CalculateField_management(urh, "TOTSatAl", "!TotPm3! / (!Pmehlich! *100 / !SatAl_pc!)  * 100", "PYTHON_9.3", "")


		# Process: Calculer un champ (45)
       arcpy.CalculateField_management(urh, "Pslnsurffert", "Pslnsurffert(!TOTSatAl!, !Pdisssurf!, !Qsurf3!)", "PYTHON", "def Pslnsurffert(TOTSatAl, Pdisssurf, Qsurf3):\\n if (((50 + 17.8 * TOTSatAl) * Qsurf3/100) - Pdisssurf * 1000) < 0:\\n  return 0 \\n else :\\n  return (((50 + 17.8 * TOTSatAl) * Qsurf3/100) - (Pdisssurf * 1000)) / 1000")

		# Process: Calculer un champ (69)
       arcpy.CalculateField_management(urh, "Pslnsurffert", "updateValue( !Pslnsurffert! )", "PYTHON", "def updateValue(value):\\n  if value == None:\\n   return '0'\\n  else: return value")


		# Process: Calculer un champ (46)
       arcpy.CalculateField_management(urh, "Preactsurf", "(40 + 17.1 * !TOTSatAl!) * !Qsurf4! / 100", "PYTHON_9.3", "")


		# Process: Calculer un champ (50)
       arcpy.CalculateField_management(urh, "Ptotal", "[Ppartsurf] + [PdissSURF] + [PparticDRAIN] + [PdissDRAIN] + [Ppartfert] + [Pslnsurffert]", "VB", "")


		# Process: Calculer un champ (49)
       arcpy.CalculateField_management(urh, "PTotalTOUT", "PTotalTOUT( !util_terr!, !Ptotal! )", "PYTHON_9.3", "def PTotalTOUT(Util_terr,Ptotal):\\n if Util_terr == \"Brsh\" :\\n  return 0.18\\n elif Util_terr in  (\"WET\" ,  \"URB\", \"Res_M\",   \"HAB\" ,\"CU\" ):\\n  return 0.72\\n elif Util_terr == \"ResL\" :\\n  return 0.61\\n elif Util_terr in (\"F\",  \"M\" , \"R\") :\\n  return 0.14\\n elif Util_terr in  (\"DH\" , \"INO\") :\\n  return 0.72\\n elif Util_terr in ( \"BHE\" , \"ILE\" , \"EAU\") :\\n  return 0.00006\\n elif Util_terr in (\"CAR\" , \"DEM\" , \"GR\", \"GOL\"):\\n  return 0.00006\\n elif Util_terr == \"NPv\" :\\n  return 0.78\\n elif Util_terr == \"Pve\" :\\n  return 1.17\\n elif Util_terr == \"Res_L\" :\\n  return 0.61\\n else:\\n  return Ptotal")


		# Process: Calculer un champ (47)
       arcpy.CalculateField_management(urh, "Pbio1", "Pbio1(!Ppartgha!, !Pparthafert!, !PparticDRAIN!, !TotPm3!, !Preactsurf!, !PreactDRAIN!)", "PYTHON", "import math\\ndef Pbio1 (Ppartgha, Pparthafert, PparticDRAIN, TotPm3, Preactsurf, PreactDRAIN):\\n return ((Ppartgha + Pparthafert + (PparticDRAIN * 1000)) * (14.858 * (math.pow(TotPm3, 0.2814))/100) + Preactsurf + PreactDRAIN) / 1000")


		# Process: Ajouter un champ (48)
       arcpy.AddField_management(urh, "Zone_ha2", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

		# Process: Calculer un champ (52)
       arcpy.CalculateField_management(urh, "Zone_ha2", "!shape.area@hectares!", "PYTHON_9.3", "\\n")


		# Process: Calculer un champ (53)
       arcpy.CalculateField_management(urh, "VolQsurf", "!Qsurf3! * 1", "PYTHON_9.3", "")


		# Process: Calculer un champ (54)
       arcpy.CalculateField_management(urh, "VolQsout", "!Qsout2! * 1", "PYTHON_9.3", "")


		# Process: Calculer un champ (55)
       arcpy.CalculateField_management(urh, "Qtesediment", "!Zone_ha2! * !Sed2!", "PYTHON_9.3", "")


		# Process: Calculer un champ (56)
       arcpy.CalculateField_management(urh, "QtePpartsurf", "!Zone_ha2! * !Ppartsurf!", "PYTHON_9.3", "")


		# Process: Calculer un champ (57)
       arcpy.CalculateField_management(urh, "QtePdisssurf", "!Zone_ha2! * !PdissSURF!", "PYTHON_9.3", "")


		# Process: Calculer un champ (58)
       arcpy.CalculateField_management(urh, "QtePpartdrain", "!Zone_ha2! * !PparticDRAIN!", "PYTHON_9.3", "")


		# Process: Calculer un champ (59)
       arcpy.CalculateField_management(urh, "QtePslndrain", "!Zone_ha2! * !PdissDRAIN!", "PYTHON_9.3", "")


		# Process: Calculer un champ (60)
       arcpy.CalculateField_management(urh, "QtePpartfert", "!Zone_ha2! * !Ppartfert!", "PYTHON_9.3", "")


		# Process: Calculer un champ (61)
       arcpy.CalculateField_management(urh, "QtePslnfert", "[Zone_ha2] * [Pslnsurffert]", "VB", "")


		# Process: Calculer un champ (62)
       arcpy.CalculateField_management(urh, "QtePtotal", "!Zone_ha2! * !Ptotal!", "PYTHON_9.3", "")


		# Process: Calculer un champ (64)
       arcpy.CalculateField_management(urh, "QtePTotalTOUT", "!Zone_ha2! * !PTotalTOUT! ", "PYTHON_9.3", "")


		# Process: Calculer un champ (63)
       arcpy.CalculateField_management(urh, "QtePbio", "!Zone_ha2! * !Pbio1!", "PYTHON_9.3", "")

    except Exception as err:
       arcpy.AddError(err)
       print err





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


    #Calcul de la superficie en hectare
    write_msg(log_txt, u"Calcul de la superficie en hectare", False, True)
    add_field_ha(urh_path)
    calc_Zone_ha2(urh_path)


    #Calcul du ruissellement
    write_msg(log_txt, u"Calcul du ruissellement", False, True)
    add_fields_ruis(urh_path)
    calc_ruis_export(urh_path)


    #Calcul de l'exportation des sédiments
    write_msg(log_txt, u"Calcul de l'exportation des sédiments", False, True)
    add_fields_sed(urh_path)
    calc_sed_export(urh_path)


    #Calcul de l'exportation du phosphore
    write_msg(log_txt, u"Calcul de l'exportation du phosphore", False, True)
    add_fields_phos(urh_path)
    calc_phos_export(urh_path)


    #Fin du script
    write_msg(log_txt, u"Fin du script" + "\n", False, True)
