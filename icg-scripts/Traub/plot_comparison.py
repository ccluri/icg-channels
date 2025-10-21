
import numpy as np
import matplotlib.pyplot as plt


def main():
	
	colors = ['black', 'blue', 'red']

	f, axs = plt.subplots(nrows=6, ncols=2, figsize=(6,5))

	for i, fignum in enumerate(['fig_21', 'fig_22']):
		for j, k in enumerate(['default', 'model1', 'model2']):
			time = np.loadtxt(f"{k}/output/{fignum}/time.txt")
			voltage = np.loadtxt(f"{k}/output/{fignum}/voltage.txt")
			voltage2 = np.loadtxt(f"{k}/output/{fignum}/voltage2.txt")
			axs[j, i].plot(time, voltage, linewidth=0.75, color=colors[j])
			axs[j+3, i].plot(time, voltage2, linewidth=0.75, color=colors[j])
			axs[j, i].set_axis_off()
			axs[j+3, i].set_axis_off()

	plt.tight_layout()
	f.savefig("traub_panel_b.pdf")

	f2, axs2 = plt.subplots(nrows=12, ncols=1, figsize=(3,7))

	for i, fignum in enumerate(['fig_41', 'fig_42', 'fig_43', 'fig_44']):
		for j, k in enumerate(['default', 'model1', 'model2']):
			time = np.loadtxt(f"{k}/output/{fignum}/time.txt")
			voltage = np.loadtxt(f"{k}/output/{fignum}/voltage.txt")
			axs2[i*3 + j].plot(time, voltage, linewidth=0.75, color=colors[j])
			axs2[i*3 + j].set_axis_off()

	plt.tight_layout()
	f.savefig("traub_panel_c.pdf")

	plt.show()






if __name__ == "__main__":
	main()
