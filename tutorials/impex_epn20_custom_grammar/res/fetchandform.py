#!/usr/bin/python

import math, urllib2, os, httplib
from datetime import time, datetime
from xml.dom.minidom import parse

from gavo import api

value_sep = "  "
value_null = "NULL"
float_null = "9999.9999"
date_null = "1900-01-01"
int_null = "-1"

# data mappings for dataproduct_type, measuerement_type and target_class respectively
dataproduct_types = { "2DCuts" : "im", "3DCubes" : "vo", "Spectra" : "sp", "TimeSeries" : "ts" }
measurement_types = { "Current" : "phys.electField", "ElectricField" : "phys.electField", "IonComposition" : "phys.abund", "MagneticField" : "phys.magField", "Spectrum" : "phys.abund", "ThermalPlasma" : "phys.density#phys.veloc#phys.temperature" }
target_classes = { "Comet" : "comet", "Mercury" : "planet", "Venus" : "planet", "Earth" : "planet", "Mars" : "planet", "Jupiter" : "planet", "Saturn" : "planet" }


# helper function to convert to julian days (rquires gcal2jd)
def convertToJD(date):
	return api.dateTimeToJdn(date)

def getNumOut (anID, anOutputArray):
  for num_out in anOutputArray:
    if num_out.getElementsByTagName("ResourceID")[0].childNodes[0].nodeValue == anID:
      return num_out
  return None

def getObsId (anId):
  sep = "_"
  tmp_arr = anId.split("/")
  return tmp_arr[4] + sep + tmp_arr[5] + sep + tmp_arr[6]

def getFileHeader(aHost, aPath):
  conn = httplib.HTTPConnection(aHost)
  conn.request("HEAD", aPath)
  header_res = conn.getresponse()
  return { "content-length": str( int(header_res.getheader("content-length")) / 1024 ), "content-type" : header_res.getheader("content-type") }

def generate(sourceURL):
  try:
    config_dom = parse (urllib2.urlopen(sourceURL))
  except:
    raise api.DataError("ERROR: IMPEx configuration file could not be retrieved!")

  impex_trees = [] # all trees of type 'simulation' will be included				

  for database in config_dom.getElementsByTagName('database'):
    if database.attributes["type"].value == "simulation":
      impex_trees.append ( [ database.getElementsByTagName('name')[0].childNodes[0].nodeValue, database.getElementsByTagName('protocol')[0].childNodes[0].nodeValue + "://" + database.getElementsByTagName('dns')[0].childNodes[0].nodeValue + database.getElementsByTagName('tree')[0].childNodes[0].nodeValue ] )

  impex_trees = impex_trees[2:3]

  row_count = 1;

  for tree in impex_trees:
      
    print ("Processing tree: " + tree[0] + " (" + tree[1] + ") ..." )
    try:
      tree_dom =  parse ( urllib2.urlopen( urllib2.Request( tree[1] ) ) )
    except:
      import traceback; traceback.print_exc()
      print ("WARNING: Tree of '" + tree[0] + "' could not be retrieved and/or parsed!")
    else:		
      numerical_outputs = tree_dom.getElementsByTagName("NumericalOutput")		
      granules = tree_dom.getElementsByTagName("Granule")
      repository = tree_dom.getElementsByTagName("Repository")
      if len(repository) > 1:
        print ("WARNING: Tree contains " + len(repository) + " repositories - only first one will be evaluated!")
      # only first repository will be considered!
      resource_name = repository[0].getElementsByTagName("ResourceName")[0].childNodes[0].nodeValue
          
      if len(granules) > 0:
        # tree file inlcudes granule elements - data in granules supersedes equivalent data in NumericalOutput elements!
        for granule in granules:

          param_obj = { "granule_uid": row_count, "granule_gid": resource_name, "dataproduct_type": value_null, "target_name": value_null, "target_class": value_null, "time_min": float_null, "time_max": float_null, "c1min": float_null, "c1max": float_null, "c2min": float_null, "c2max": float_null, "c3min": float_null, "c3max": float_null, "spatial_frame_type": value_null, "release_date": date_null, "access_url": value_null, "access_estsize": "1024", "file_name": value_null, "publisher": value_null }
                  
          # get the NumericalOutput corresponding to processed granule
          num_out = getNumOut(granule.getElementsByTagName("ParentID")[0].childNodes[0].nodeValue, numerical_outputs)
          if num_out == None:
            print "WARNING: NumericalOutput with ID '" + granule.getElementsByTagName("ParentID")[0].childNodes[0].nodeValue + "' does not exist!"
            break; # no numerical output with given ID!
          
          param_obj["dataproduct_type"] = dataproduct_types [ num_out.getElementsByTagName("SimulationProduct")[0].childNodes[0].nodeValue ]
          param_obj["target_name"] = num_out.getElementsByTagName("SimulatedRegion")[0].childNodes[0].nodeValue.split(".")[0]
          param_obj["target_class"] = target_classes [ param_obj["target_name"] ]
                  
          tmp_start = granule.getElementsByTagName("StartDate")
          tmp_stop = granule.getElementsByTagName("StopDate")
          if ( (len(tmp_start) > 0) and (len(tmp_stop) > 0) ):
            param_obj["time_min"] = str ( convertToJD ( datetime.strptime( tmp_start[0].childNodes[0].nodeValue, '%Y-%m-%dT%H:%M:%S.%f') ) )
            param_obj["time_max"] = str ( convertToJD ( datetime.strptime( tmp_stop[0].childNodes[0].nodeValue, '%Y-%m-%dT%H:%M:%S.%f') ) )
                  
          if ( len( num_out.getElementsByTagName("CoordinateRepresentation") ) > 0 ):
            param_obj["spatial_frame_type"] = num_out.getElementsByTagName("CoordinateRepresentation")[0].childNodes[0].nodeValue
          
          param_obj["measurement_type"] = measurement_types [ num_out.getElementsByTagName("MeasurementType")[0].childNodes[0].nodeValue ]
          param_obj["release_date"] = granule.getElementsByTagName("ReleaseDate")[0].childNodes[0].nodeValue.split("T")[0]
          param_obj["obs_id"] = getObsId( granule.getElementsByTagName("ResourceID")[0].childNodes[0].nodeValue )

          tmp_min = granule.getElementsByTagName("RegionBegin")
          tmp_max = granule.getElementsByTagName("RegionEnd")
          
          tmp_spatial = num_out.getElementsByTagName("SpatialDescription")
          if ( ( len(tmp_spatial) > 0 ) and ( tmp_spatial[0].getElementsByTagName("Units")[0].childNodes[0].nodeValue == "m" ) ):
              factor = 1000 # values are in meters
          else:
              factor = 1 # values already in KM (only m and KM are consdered for IMPEx)
          
          if ( (len(tmp_min) > 0) and (len(tmp_max) > 0) ):
            param_obj["c1min"] = str ( float ( tmp_min[0].childNodes[0].nodeValue.split()[0] ) / factor )
            param_obj["c1max"] = str ( float ( tmp_max[0].childNodes[0].nodeValue.split()[0] ) / factor )
            param_obj["c2min"] = str ( float ( tmp_min[0].childNodes[0].nodeValue.split()[1] ) / factor )
            param_obj["c2max"] = str ( float ( tmp_max[0].childNodes[0].nodeValue.split()[1] ) / factor )
            param_obj["c3min"] = str ( float ( tmp_min[0].childNodes[0].nodeValue.split()[2] ) / factor )
            param_obj["c3max"] = str ( float ( tmp_max[0].childNodes[0].nodeValue.split()[2] ) / factor )				
                    
          tmp_url = granule.getElementsByTagName("URL")
          if ( ( len(tmp_url) > 0 ) and ( len(tmp_url[0].childNodes) ) ) > 0:
            param_obj["access_url"] = tmp_url[0].childNodes[0].nodeValue
            segments = param_obj["access_url"].replace("http://", "").split("/")
            if ( (param_obj["access_url"].find("?") == -1) and (len(segments) > 1) ):
              param_obj["file_name"] = segments [ len(segments)-1 ]

          if ( param_obj["file_name"] != value_null ):
            segments = param_obj["access_url"].replace("http://", "").split("/")
            header = getFileHeader( segments[0], "/" + "/".join(segments[1:len(segments)]) )
            param_obj["access_estsize"] = header["content-length"]
            if ( header["content-type"] == "text/xml" ): 
              param_obj["access_format"] = "application/x-votable+xml"
            else:
              param_obj["access_format"] = header["content-type"]
          else:						
            param_obj["access_format"] = value_null
            quantity = num_out.getElementsByTagName("Quantity") 
            if ( len(quantity) > 0 ):
              param_obj["access_estsize"] = str( int(quantity[0].childNodes[0].nodeValue) / 1024 )
          
          param_obj["publisher"] =  num_out.getElementsByTagName("PersonID")[0].childNodes[0].nodeValue
          
          yield param_obj
          row_count = row_count + 1				
      else:
        # tree file does NOT inlcudes granule elements 
        for num_out in numerical_outputs:
          
          param_obj = { "granule_uid": row_count, "granule_gid": resource_name, "obs_id": value_null, "dataproduct_type": value_null, "target_name": value_null, "target_class": value_null, "c1min": float_null, "c1max": float_null, "c2min": float_null, "c2max": float_null, "c3min": float_null, "c3max": float_null, "spatial_frame_type": value_null, "release_date": date_null, "access_url": value_null, "access_estsize": "1024", "file_name": value_null, "publisher": value_null }

          param_obj["dataproduct_type"] = dataproduct_types [ num_out.getElementsByTagName("SimulationProduct")[0].childNodes[0].nodeValue ]
          param_obj["target_name"] = num_out.getElementsByTagName("SimulatedRegion")[0].childNodes[0].nodeValue.split(".")[0]
          param_obj["target_class"] = target_classes [ param_obj["target_name"] ]
          param_obj["time_min"] = float_null 
          param_obj["time_max"] = float_null
          param_obj["spatial_frame_type"] = num_out.getElementsByTagName("CoordinateRepresentation")[0].childNodes[0].nodeValue
          param_obj["measurement_type"] = measurement_types [ num_out.getElementsByTagName("MeasurementType")[0].childNodes[0].nodeValue ]
          param_obj["release_date"] = num_out.getElementsByTagName("ReleaseDate")[0].childNodes[0].nodeValue.split("T")[0]
          param_obj["obs_id"] = getObsId( num_out.getElementsByTagName("ResourceID")[0].childNodes[0].nodeValue )
          
          tmp_min = num_out.getElementsByTagName("RegionBegin")
          tmp_max = num_out.getElementsByTagName("RegionEnd")

          tmp_spatial = num_out.getElementsByTagName("SpatialDescription")
          if ( ( len(tmp_spatial) > 0 ) and ( tmp_spatial[0].getElementsByTagName("Units")[0].childNodes[0].nodeValue == "m" ) ):
              factor = 1000 # values are in meters
          else:
              factor = 1 # values already in KM (only m and KM are consdered for IMPEx)

          if ( (len(tmp_min) > 0) and (len(tmp_max) > 0) ):
            param_obj["c1min"] = str ( float ( tmp_min[0].childNodes[0].nodeValue.split()[0] ) / factor )
            param_obj["c1max"] = str ( float ( tmp_max[0].childNodes[0].nodeValue.split()[0] ) / factor )
            param_obj["c2min"] = str ( float ( tmp_min[0].childNodes[0].nodeValue.split()[1] ) / factor )
            param_obj["c2max"] = str ( float ( tmp_max[0].childNodes[0].nodeValue.split()[1] ) / factor )
            param_obj["c3min"] = str ( float ( tmp_min[0].childNodes[0].nodeValue.split()[2] ) / factor )
            param_obj["c3max"] = str ( float ( tmp_max[0].childNodes[0].nodeValue.split()[2] ) / factor )				

          tmp_url = num_out.getElementsByTagName("URL")
          if ( ( len(tmp_url) > 0 ) and ( len(tmp_url[0].childNodes) ) ) > 0:
            param_obj["access_url"] = tmp_url[0].childNodes[0].nodeValue
            segments = param_obj["access_url"].replace("http://", "").split("/")
            if ( (param_obj["access_url"].find("?") == -1) and (len(segments) > 1) ):
              param_obj["file_name"] = segments [ len(segments)-1 ]

          if ( param_obj["file_name"] != value_null ):
            segments = param_obj["access_url"].replace("http://", "").split("/")
            header = getFileHeader( segments[0], "/" + "/".join(segments[1:len(segments)]) )
            param_obj["access_estsize"] = header["content-length"]
            if ( header["content-type"] == "text/xml" ): 
              param_obj["access_format"] = "application/x-votable+xml"
            else:
              param_obj["access_format"] = header["content-type"]
          else: 
            param_obj["access_format"] = value_null
            quantity = num_out.getElementsByTagName("Quantity")
            if ( len(quantity) > 0 ):
              param_obj["access_estsize"] = str(int(quantity[0].childNodes[0].nodeValue) / 1024)
          
          param_obj["publisher"] =  num_out.getElementsByTagName("PersonID")[0].childNodes[0].nodeValue

          yield param_obj
          row_count = row_count + 1

      print ("Done.\n")	

from gavo.grammars.customgrammar import CustomRowIterator

class RowIterator(CustomRowIterator):
  def _iterRows(self):
    for row in generate(self.sourceToken):
      yield row


if __name__=="__main__":
	pass
