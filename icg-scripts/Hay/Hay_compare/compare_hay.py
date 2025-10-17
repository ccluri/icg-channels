import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib import gridspec
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

plt.rcParams.update({
    
    'xtick.labelsize': 15,
    'xtick.major.size': 10,
    'ytick.labelsize': 15,
    'ytick.major.size': 10,
    'font.size': 12,
    'axes.labelsize': 15,
    'axes.titlesize': 20,
    'axes.titlepad' : 30,
    'legend.fontsize': 15,
    # 'figure.subplot.wspace': 0.4,
    # 'figure.subplot.hspace': 0.4,
    # 'figure.subplot.left': 0.1,
})

rc('font', **{'family': 'serif', 'serif': ['Arial']})
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Arial']})
rc('text', usetex=True)

filenames = ['BAC_firing.npz', 'Step_current_firing.npz', 'critical_freq.npz']
folders = ['orig', 'sm']

fig = plt.figure(figsize=(17, 8))
gs = gridspec.GridSpec(2, 3, hspace=0.25)

def ax_prune(ax):
    ax.set_ylim([-85, 40])
    #for ii in ['right', 'bottom', 'top', 'left']:
    for ii in ['top', 'right']:
        ax.spines[ii].set_visible(False)
    #ax.set_axis_off()
    return ax


def add_sizebar(ax, size, loc=8, size_vertical=1):
    # bar1 = AnchoredSizeBar(ax.transData, 100, 'filled',
    #                        frameon=False, size_vertical=100)
    # ax.add_artist(bar1)
    # return ax
    asb = AnchoredSizeBar(ax.transData,
                          size,
                          str(size) + ' ms',
                          loc=loc,
                          pad=-0.2, borderpad=.0, sep=5,
                          frameon=False, size_vertical=size_vertical)
    asb.size_bar._children[0].set_fill(True)
    ax.add_artist(asb)
    return ax
    


for ii,fold in enumerate(folders):
    BAC = np.load(fold+'/'+filenames[0])
    ax = plt.subplot(gs[ii, 0])
    ax.plot(BAC['time'], BAC['soma'], c='k')
    ax.plot(BAC['time'], BAC['dend'], c='orange')
    ax.plot(BAC['time'], BAC['dend2'], c='r')
    ax_prune(ax)
    ax.set_xlim([250, 400])
    # ax.set_ylabel('Membrane potential (mV)', fontsize=14)
    # if ii == 0:
    #     ax.set_title('bAP firing', fontsize=14)
    # if ii == 1:
    #     ax.set_xlabel('Time (ms)', fontsize=14)

    ax.set_ylabel('Membrane potential (mV)', )
    if ii == 0:
        ax.set_title('bAP firing', )
    if ii == 1:
        ax.set_xlabel('Time (ms)', )
    # else:
    #     ax.set_ylabel('Standardised ion channel model')
    Step = np.load(fold+'/'+filenames[1])
    ax = plt.subplot(gs[ii, 1])
    ax.plot(Step['time'], Step['soma'])
    if ii == 0:
        ax.set_title('Step current')
    if ii == 1:
        ax.set_xlabel('Time (ms)')
    freq = np.load(fold+'/'+filenames[2])
    ax_prune(ax)
    ax = plt.subplot(gs[ii, 2])
    ax.plot(freq['time'], freq['soma'], c='k')
    ax.plot(freq['time'], freq['vdend'], c='r')
    ax.set_xlim([200, 400])
    if ii == 0:
        ax.set_title('Critical frequency')
    if ii == 1:
        ax.set_xlabel('Time (ms)')
    ax_prune(ax)
    #add_sizebar(ax, 50., loc=3)
    #add_sizebar(ax, 1, loc=3, size_vertical=50)
# ax.set_ylabel('Standardised ion channel model')
rr = plt.gcf()
rr.text(0.07, 0.95, 'A', fontsize=20, weight='bold')
rr.text(0.33, 0.95, 'B',  fontsize=20, weight='bold')
rr.text(0.62, 0.95, 'C',  fontsize=20, weight='bold')
plt.text(x=0.5, y=0.97, s='Original ion channel model', fontsize=20, transform=fig.transFigure,  horizontalalignment='center')
plt.text(x=0.5, y=0.45, s='Standardised ion channel model', fontsize=20, transform=fig.transFigure,  horizontalalignment='center')

# rr.text(0.07, 0.89, 'A', weight='bold')
# rr.text(0.33, 0.891, 'B'  , weight='bold')
# rr.text(0.62, 0.891, 'C'  , weight='bold')
# plt.text(x=0.5, y=0.93, s='Original ion channel model',
#          transform=fig.transFigure,  horizontalalignment='center')
# plt.text(x=0.5, y=0.48, s='Standardised ion channel model',
#          transform=fig.transFigure,  horizontalalignment='center')
    
# with PdfPages('fig2_Hay.pdf') as pdf:
#     pdf.savefig(fig, bbox_inches='tight', dpi=300)
plt.savefig('fig4_Hay_2025.pdf', bbox_inches='tight', dpi=300)
    
#plt.show()
    
