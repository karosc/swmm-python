import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from swmm.pandas import Output,test_out_path

# read output file in Output object
out = Output(test_out_path)

# pull runoff_rate timeseries for all cathments and plot them
ax = out.subcatch_series(out.subcatchments, 'runoff_rate', columns='elem').plot(figsize=(8,4))
plt.title("Runoff Rate")
plt.tight_layout()
plt.show()