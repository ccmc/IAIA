
# Description
Hi Asher,

This is the resource descriptor (q.rd) including the custom grammar written in (ugly) python in the res directory called "fetchandform.py" that export the data directly out of the xml IMPEx tree containing data according to the IMPEx/SPASE DM. If you use the "Imp" command of DaCHS (see >> http://docs.g-vo.org/DaCHS/) this will import all data from the tree into DaCHS. You will need some tweaking of course, i.e. you will not use the IMPEx configuration file to get to your trees but directly access them etc...

Basically this is all you need to expose your data in a way compatible with VESPA (>> http://voparis-europlanet-dev.obspm.fr/planetary/data/epn/query/all/).

Cheers,
Tarek