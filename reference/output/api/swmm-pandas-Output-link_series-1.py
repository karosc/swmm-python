import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from swmm.pandas import Output,test_out_path

out = Output(test_out_path)
df = out.link_series('COND6',['flow_rate','groundwater','pol_rainfall','sewage'])

# set up figure
fig,ax = plt.subplots(figsize=(8,4))

# plot flow rate on primary yaxis
ax.plot(df.flow_rate,label="flow rate")

# plot pollutant concentrations on secondary axis
# rainfall, DWF, and groundwater were given 100 mg/L pollutant
# concentrations to serve as tracers
ax1 = ax.twinx()
ax1.plot(df.groundwater,ls = '--',label="groundwater tracer")
ax1.plot(df.pol_rainfall,ls = '--',label="rainfall tracer")
ax1.plot(df.sewage,ls = '--',label="sewage tracer")

# style axes
ax.set_ylabel("Flow Rate (cfs)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
ax1.set_ylabel("Percent")

# add legend and show figure
fig.legend(bbox_to_anchor=(1,1),bbox_transform=ax.transAxes)
fig.tight_layout()

fig.show()