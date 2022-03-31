import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from swmm.pandas import Output,test_out_path

# read output file in Output object
out = Output(test_out_path)

# pull rainfall and runoff_rate timeseries and plot them
ax = out.subcatch_series('SUB1', ['rainfall', 'runoff_rate']).plot(figsize=(8,4))
plt.title("SUB1 Params")
plt.tight_layout()
plt.show()