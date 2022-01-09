=========
Output
=========
.. currentmodule:: swmm.pandas

Constructor
~~~~~~~~~~~
.. autosummary::
   :nosignatures:
   :toctree: api/

   Output


Properties
~~~~~~~~~~~

.. autosummary::
   :nosignatures:
   :toctree: api/

   Output.subcatchments
   Output.links
   Output.nodes
   Output.pollutants
   Output.timeIndex
   Output.project_size
   Output.report
   Output.start
   Output.end
   Output.period
   

Time Series Data
~~~~~~~~~~~~~~~~~
Get time series data for one or more elements and one or more variables.

.. autosummary::
   :nosignatures:
   :toctree: api/

   Output.link_series
   Output.node_series   
   Output.subcatch_series
   Output.system_series
   
Element Attribute Data
~~~~~~~~~~~~~~~~~~~~~~~
Get attribute for a given time step for all elements of a give type.

.. autosummary::
   :nosignatures:
   :toctree: api/

   Output.link_attribute
   Output.node_attribute   
   Output.subcatch_attribute
   Output.system_attribute

Element Result Data
~~~~~~~~~~~~~~~~~~~~
Get all attributes for a given set time steps for given set of elements.

.. autosummary::
   :nosignatures:
   :toctree: api/
   
   Output.link_result
   Output.node_result   
   Output.subcatch_result
   Output.system_result

Helper Methods
~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :nosignatures:
   :toctree: api/

   Output.getStructure