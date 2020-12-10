/*
 *  solver_docs.i - Documentation for swmm-solver
 *
 *  Created:    12/10/2020
 *  
 *  Author:     See AUTHORS
 *
*/


%define SOLVER_MODULE_DOCS
"Solver Module
"
%enddef


// PUBLIC STRUCTS
%feature("autodoc", 
"Node Statistics

Attributes
----------
avgDepth: double
    average node depth (level)
maxDepth: double
    max node depth (level) (from routing step)
maxDepthDate: DateTime
    date of maximum depth
maxRptDepth: double
    max node depth (level) (from reporting step)
volFlooded: double
    total volume flooded (volume)
timeFlooded: double
    total time flooded
timeSurcharged: double
    total time surcharged
timeCourantCritical: double
    total time courant critical
totLatFlow: double
    total lateral inflow (volume)
maxLatFlow: double
    maximum lateral inflow (flowrate)
maxInflow: double
    maximum total inflow (flowrate)
maxOverflow: double
    maximum flooding (flowrate)
maxPondedVol: double
    maximum ponded volume (volume)
maxInflowDate: DateTime
    date of maximum inflow
maxOverflowDate: DateTime
    date of maximum overflow
" 
) SM_NodeStats();


%feature("autodoc", 
"Storage Statistics

Attributes
----------
initVol: double
    initial volume (volume)
avgVol: double
    average volume (volume) (from routing step)
maxVol: double
    maximum volume (volume) (from routing step)
maxFlow: double
    maximum total inflow (flowrate) (from routing step)
evapLosses: double
    evaporation losses (volume)
exfilLosses: double
    exfiltration losses (volume)
maxVolDate: datetime
    date of maximum volume
" 
) SM_StorageStats();


%feature("autodoc", 
"Outfall Statistics

Attributes
----------
avgFlow: double
    average flow (flowrate)
maxFlow: double
    maximum flow (flowrate) (from routing step)
totalLoad: double *
    total pollutant load (mass)
totalPeriods: double
    total simulation steps (from routing step)
" 
) SM_OutfallStats(int);


%feature("autodoc", 
"Link Statistics

.. rubric:: 'Flow Classes'

===========   ===========================
Flow Class    Description                
===========   ===========================
DRY           dry conduit
UP_DRY        upstream end is dry
DN_DRY        downstream end is dry
SUBCRITICAL   sub-critical flow
SUPCRITICAL   super-critical flow
UP_CRITICAL   free-fall at upstream end
DN_CRITICAL   free-fall at downstream end
===========   ===========================

Attributes
----------
maxFlow: double
    maximum flow (flowrate) (from routing step)
maxFlowDate: double
    date of maximum flowrate
maxVeloc: double
    maximum velocity (from routing step)
maxDepth: double
    maximum depth (level)
timeNormalFlow: double
    time in normal flow
timeInletControl: double
    time under inlet control
timeSurcharged: double
    time surcharged
timeFullUpstream: double
    time full upstream
timeFullDnstream: double
    time full downstream
timeFullFlow: double
    time full flow
timeCapacityLimited: double
    time capacity limited
timeInFlowClass: double[7]
    time in flow class (See: 'Flow Classes')
timeCourantCritical: double
    time courant critical
flowTurns: double
    number of flow turns
flowTurnSign: double
    number of flow turns sign
" 
) SM_LinkStats();


%feature("autodoc", 
"Pump Statistics

Attributes
----------
utilized: double
    time utilized
minFlow: double
    minimum flowrate
avgFlow: double
    average flowrate
maxFlow: double
    maximum flowrate
volume: double
    total pumping volume (volume)
energy: double
    total energy demand
offCurveLow: double
    hysteresis low (off depth wrt curve)
offCurveHigh: double
    hysteresis high (on depth wrt curve)
startUps: int
    number of start ups
totalPeriods: int
    total simulation steps (from routing step)
" 
) SM_PumpStats();


%feature("autodoc", 
"Subcatchment Statistics

Attributes
----------
precip: double
    total precipication (length)
runon: double
    total runon (volume)
evap: double
    total evaporation (volume)
infil: double
    total infiltration (volume)
runoff: double
    total runoff (volume)
maxFlow: double
    maximum runoff rate (flowrate)
" 
) SM_SubcatchStats();


%feature("autodoc", 
"System Flow Routing Totals

Attributes
----------
dwInflow: double
    dry weather inflow
wwInflow: double
    wet weather inflow
gwInflow: double
    groundwater inflow
iiInflow: double
    RDII inflow
exInflow: double
    direct inflow
flooding: double
    internal flooding
outflow: double
    external outflow
evapLoss: double
    evaporation loss
seepLoss: double
    seepage loss
reacted: double
    reaction losses
initStorage: double
    initial storage volume
finalStorage: double
    final storage volume
pctError: double
    continuity error
" 
) SM_RoutingTotals();


%feature("autodoc", 
"System Runoff Totals

Attributes
----------
rainfall: double
    rainfall total (depth)
evap: double
    evaporation loss (volume)
infil: double
    infiltration loss (volume)
runoff: double
    runoff volume (volume)
drains: double
    LID drains (volume)
runon: double
    runon from outfalls (volume)
initStorage: double
    inital surface storage (depth)
finalStorage: double
    final surface storage (depth)
initSnowCover: double
    initial snow cover (depth)
finalSnowCover: double
    final snow cover (depth)
snowRemoved: double
    snow removal (depth)
pctError: double
    continuity error (%)
" 
) SM_RunoffTotals();


// CANONICAL API
%feature("autodoc", 
"Opens SWMM input file, reads in network data, runs, and closes

Parameters
----------
f1: char const *
f2: char const *
f3: char const *
"
) swmm_run;

%feature("autodoc",
"Opens SWMM input file & reads in network data

Parameters
----------
f1: char const *
f2: char const *
f3: char const *
"
) swmm_open;

%feature("autodoc",
"Start SWMM simulation

Parameters
----------
saveFlag: int
"
) swmm_start;

%feature("autodoc",
"Step SWMM simulation forward
"
) swmm_step;

%feature("autodoc",
"End SWMM simulation   
"
) swmm_end;

%feature("autodoc",
"Write text report file
"
) swmm_report;

%feature("autodoc",
"Get routing errors
"
) swmm_getMassBalErr;

%feature("autodoc",
"Frees all memory and files used by SWMM
"
) swmm_close;

%feature("autodoc",
"Get Legacy SWMM version number
"
) swmm_getVersion;


// TOOLKIT API
%feature("autodoc",
"Get full semantic version number info
"
) swmm_getVersionInfo;

%feature("autodoc",
"Finds the index of an object given its ID.

Parameters
----------
type: SM_ObjectType
id: char *
"
) swmm_project_findObject;

%feature("autodoc", 
"Gets Object ID

Parameters
----------
type: SM_ObjectType
index: int
"
) swmm_getObjectId;

%feature("autodoc", 
"Gets Object Count

Parameters
----------
type: SM_ObjectType
"
) swmm_countObjects;


%feature("autodoc", 
"Get the simulation datetime information

Parameters
----------
type: SM_TimePropety
"
) swmm_getSimulationDateTime;

%feature("autodoc", 
"Get the current simulation datetime information.
"
) swmm_getCurrentDateTime;

%feature("autodoc", 
"Set simulation datetime information.

Parameters
----------
type: SM_TimePropety
year: int
month: int
day: int
hour: int
minute: int
second: int
"
) swmm_setSimulationDateTime;

%feature("autodoc", 
"Gets Simulation Analysis Setting

Parameters
----------
type: SM_SimOption
"
) swmm_getSimulationAnalysisSetting;

%feature("autodoc", 
"Gets Simulation Analysis Setting

Parameters
----------
type: SM_SimSetting
"
) swmm_getSimulationParam;

%feature("autodoc",
"Gets Simulation Unit

Parameters
----------
type: SM_Units
"
) swmm_getSimulationUnit;


%feature("autodoc", 
"Get the type of node with specified index.

Parameters
----------
index: int
"
) swmm_getNodeType;

%feature("autodoc", 
"Get a property value for specified node.

Parameters
----------
index: int
param: SM_NodeProperty
"
) swmm_getNodeParam;

%feature("autodoc", 
"Set a property value for specified node.

Parameters
----------
index: int
param: SM_NodeProperty
value: double
"
) swmm_setNodeParam;

%feature("autodoc", 
"Get a result value for specified node.

Parameters
----------
index: int
type: SM_NodeResult
"
) swmm_getNodeResult;

%feature("autodoc", 
"Gets pollutant values for a specified node.

Parameters
----------
index: int
type: SM_NodePollut
"
) swmm_getNodePollut;

%feature("autodoc", 
"Get the cumulative inflow for a node.

Parameters
----------
index: int
"
) swmm_getNodeTotalInflow;

%feature("autodoc", 
"Set an inflow rate to a node. The inflow rate is held constant until the 
caller changes it.

Parameters
----------
index: int
flowrate: double
"
) swmm_setNodeInflow;

%feature("autodoc", 
"Get a node statistics.

Parameters
----------
index: int
"
) swmm_getNodeStats;


%feature("autodoc", 
"Get a storage statistics.

Parameters
----------
index: int
"
) swmm_getStorageStats;


%feature("autodoc", 
"Set outfall stage.

Parameters
----------
index: int
stage: double
"
) swmm_setOutfallStage;

%feature("autodoc", 
"Get outfall statistics.

Parameters
----------
index: int
"
) swmm_getOutfallStats;


%feature("autodoc", 
"Get the type of link with specified index.

Parameters
----------
index: int
"
) swmm_getLinkType;

%feature("autodoc", 
"Get the link Connection Node Indeces. If the conduit has a negative slope, 
the dynamic wave solver will automatically reverse the nodes. 

Parameters
----------
index: int
"
) swmm_getLinkConnections;

%feature("autodoc", 
"Get the link flow direction

Parameters
----------
index: int
"
) swmm_getLinkDirection;

%feature("autodoc", 
"Get a property value for specified link.

Parameters
----------
index: int
param: SM_LinkProperty
"
) swmm_getLinkParam;

%feature("autodoc", 
"Set a property value for specified link.

Parameters
----------
index: int
param: SM_LinkProperty
value: double
"
) swmm_setLinkParam;

%feature("autodoc", 
"Get a result value for specified link.

Parameters
----------
index: int
type: SM_LinkResult
"
) swmm_getLinkResult;

%feature("autodoc", 
"Gets pollutant values for a specified link.

Parameters
----------
index: int
type: SM_LinkPollut
"
) swmm_getLinkPollut;

%feature("autodoc", 
"Set a link setting (pump, orifice, or weir). Setting for an orifice and a 
weir should be [0, 1]. A setting for a pump can range from [0, inf). However, 
if a pump is set to 1, it will pump at its maximum curve setting.

Parameters
----------
index: int
setting: double
"
) swmm_setLinkSetting;

%feature("autodoc", 
"Get link statistics.

Parameters
----------
index: int
"
) swmm_getLinkStats;


%feature("autodoc", 
"Get pump statistics.

Parameters
----------
index: int
"
) swmm_getPumpStats;


%feature("autodoc", 
"Get the Subcatchment connection. Subcatchments can load to a node, another 
subcatchment, or itself.

Parameters
----------
index: int
"
) swmm_getSubcatchOutConnection;

%feature("autodoc", 
"Get a property value for specified subcatchment.

Parameters
----------
index: int
param: SM_SubcProperty
"
) swmm_getSubcatchParam;

%feature("autodoc", 
"Set a property value for specified subcatchment.

Parameters
----------
index: int
param: SM_SubcProperty
value: double
"
) swmm_setSubcatchParam;

%feature("autodoc", 
"Get a result value for specified subcatchment.

Parameters
----------
index: int
type: SM_SubcResult
"
) swmm_getSubcatchResult;

%feature("autodoc", 
"Gets pollutant values for a specified subcatchment.

Parameters
----------
index: int
type: SM_SubcPollut
"
) swmm_getSubcatchPollut;

%feature("autodoc", 
"Get subcatchment statistics.

Parameters
----------
index: int
"
) swmm_getSubcatchStats;


%feature("autodoc", 
"Get system routing totals.
"
) swmm_getSystemRoutingTotals;

%feature("autodoc", 
"Get system runoff totals.
"
) swmm_getSystemRunoffTotals;


%feature("autodoc", 
"Get the number of lid units on a subcatchment.

Parameters
----------
index: int
"
) swmm_getLidUCount;

%feature("autodoc", 
"Get a property value for a specified lid unit on a specified subcatchment

Parameters
----------
index: int
lidIndex: int
param: SM_LidUProperty
"
) swmm_getLidUParam;

%feature("autodoc", 
"Set a property value for a specified lid unit on a specified subcatchment

Parameters
----------
index: int
lidIndex: int
param: SM_LidUProperty
value: double
"
) swmm_setLidUParam;

%feature("autodoc", 
"Get the lid option for a specified lid unit on a specified subcatchment

Parameters
----------
index: int
lidIndex: int
param: SM_LidUOptions
"
) swmm_getLidUOption;

%feature("autodoc", 
"Set the lid option for a specified lid unit on a specified subcatchment

Parameters
----------
index: int
lidIndex: int
param: SM_LidUOptions
value: int
"
) swmm_setLidUOption;

%feature("autodoc", 
"Get the lid unit water balance simulated value at current time

Parameters
----------
index: int
lidIndex: int
layerIndex: SM_LidLayer
"
) swmm_getLidUFluxRates;

%feature("autodoc", 
"Get the lid unit of a specified subcatchment result at current time

Parameters
----------
index: int
lidIndex: int
type: SM_LidResult
"
) swmm_getLidUResult;

%feature("autodoc", 
"Get the lid control surface immediate overflow condition

Parameters
----------
lidControlIndex: int
"
) swmm_getLidCOverflow;

%feature("autodoc", 
"Get a property value for specified lid control

Parameters
----------
lidControlIndex: int
layerIndex: SM_LidLayer
param: SM_LidLayerProperty
"
) swmm_getLidCParam;

%feature("autodoc", 
"Set a property value for specified lid control

Parameters
----------
lidControlIndex: int
layerIndex: SM_LidLayer
param: SM_LidLayerProperty
value: double
"
) swmm_setLidCParam;

%feature("autodoc", 
"Get the lid group of a specified subcatchment result at current time

Parameters
----------
index: int
type: SM_LidResult
"
) swmm_getLidGResult;


%feature("autodoc", 
"Get precipitation rates for a gage.

Parameters
----------
index: int
type: SM_GagePrecip
"
) swmm_getGagePrecip;

%feature("autodoc", 
"Set a total precipitation intensity to the gage.

Parameters
----------
index: int
total_precip: double
"
) swmm_setGagePrecip;
