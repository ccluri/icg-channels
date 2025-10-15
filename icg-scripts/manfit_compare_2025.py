import pickle
import matplotlib
from matplotlib import rc
import matplotlib.pyplot as plt
import numpy as np

rc('font', **{'family': 'serif', 'serif': ['Helvetica']})
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
rc('text', usetex=True)

iontypes = ["K", "Na", "Ca", "IH", "KCa"]
data_dict = {}
for ion in iontypes:
    f = open("/home/chchinta/icg-channels/icg-channels-"+ion+".pkl", "rb")
    data_dict[ion] = pickle.load(f)


# plot a comparison of different ion types for the different supermodel types as well
# *** also plot how many files were not fit for each
# maybe bar plots would be better???

cmap1 = ['#542788','#4575b4']
cmap2 = ['#000000','#253494','#1d91c0','#7fcdbb']

ss_mean_err = np.zeros((2,len(iontypes)))
ss_stdev_err = np.zeros((2,len(iontypes)))
ss_no_fit_pct = np.zeros((2,len(iontypes)))
tau_mean_err = np.zeros((5,len(iontypes)))
tau_stdev_err = np.zeros((5,len(iontypes)))
tau_no_fit_pct = np.zeros((5,len(iontypes)))

for i in range(len(iontypes)):
    ion = iontypes[i]
    n_files = len([1 for x in data_dict[ion].keys() if data_dict[ion][x]['RATES']])
    for j in range(2):
        sm_str = "SM"+str(j+1)
        err_str = "ERROR"+str(1)
        ss_errors = [list(data_dict[ion][x][sm_str+'_'+err_str+'_SS'].values()) for x in data_dict[ion].keys()
                     if (data_dict[ion][x]['RATES'] and data_dict[ion][x][sm_str+'_FIT'])]
        ss_errors = np.array([item for sublist in ss_errors for item in sublist])
        ss_mean_err[j,i] = np.mean(ss_errors)
        ss_stdev_err[j,i] = np.std(ss_errors)
        no_fit = len([1 for x in data_dict[ion].keys() if (data_dict[ion][x]['RATES'] and not data_dict[ion][x][sm_str+'_FIT'])])
        ss_no_fit_pct[j,i] = 100.0*no_fit/n_files
        
    for j in range(5):
        sm_str = "SM"+str(j+1)
        err_str = "ERROR"+str(1)
        tau_errors = [list(data_dict[ion][x][sm_str+'_'+err_str+'_TAU'].values()) for x in data_dict[ion].keys()
                      if (data_dict[ion][x]['RATES'] and data_dict[ion][x][sm_str+'_FIT'])]
        tau_errors = np.array([item for sublist in tau_errors for item in sublist])
        tau_errors = tau_errors[tau_errors<1e20]
        tau_mean_err[j,i] = np.mean(tau_errors)
        tau_stdev_err[j,i] = np.std(tau_errors)
        no_fit = len([1 for x in data_dict[ion].keys() if (data_dict[ion][x]['RATES'] and not data_dict[ion][x][sm_str+'_FIT'])])
        tau_no_fit_pct[j,i] = 100.0*no_fit/n_files
        
bar_width = 0.2        
fig = plt.figure(figsize=(12, 2.85))
matplotlib.rcParams.update({'font.size': 14})
#fig=plt.figure(figsize=(7,7))
ax = plt.subplot(1, 2, 1)
plt.bar(np.arange(5)-bar_width/2,ss_mean_err[0,:],bar_width,color=cmap2[0],label='sigmoid') # ,yerr=ss_stdev_err[0,:])
plt.bar(np.arange(5)+bar_width/2,ss_mean_err[1,:],bar_width,color=cmap2[2],label='mod. sigmoid') #,yerr=ss_stdev_err[1,:])
plt.legend(frameon=False, loc='upper left', ncol=2)
plt.ylabel(r'Mean error',fontsize=14)
#plt.xlabel('Membrane potential (mV)',fontsize=16)
# plt.xticks([0,1,2,3,4],[])
plt.yticks(np.linspace(0,0.02,3),np.linspace(0,0.02,3))
ax.set_xlim([-0.5,5])
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.set_xlabel('Ion type',fontsize=14)
ax.set_xticks([0,1, 2, 3, 4],['K','Na','Ca','IH', 'KCa'], fontsize=14)

# ax=plt.subplot(4,1,2)
# plt.bar(np.arange(5)-bar_width/2,ss_no_fit_pct[0,:],bar_width,color=cmap2[0],label='sigmoid')
# plt.bar(np.arange(5)+bar_width/2,ss_no_fit_pct[1,:],bar_width,color=cmap2[2],label='mod. sigmoid')
# plt.legend()
# plt.ylabel(r'No fit pct.',fontsize=16)
# plt.xticks([0,1,2,3,4],[])
# plt.yticks(np.arange(0,31,10),np.arange(0,31,10))
# ax.set_xlim([-0.5,5])
# ax.spines['right'].set_visible(False)
# ax.spines['top'].set_visible(False)

bar_width = 0.1

ax=plt.subplot(1,2,2)
plt.bar(np.arange(5)-1.5*bar_width,tau_mean_err[3,:],bar_width,color=cmap2[0],label='order 1')#,yerr=tau_stdev_err[3,:])
plt.bar(np.arange(5)-bar_width/2,tau_mean_err[2,:],bar_width,color=cmap2[1],label='order 2')#,yerr=tau_stdev_err[2,:])
plt.bar(np.arange(5)+bar_width/2,tau_mean_err[1,:],bar_width,color=cmap2[2],label='order 3')#,yerr=tau_stdev_err[1,:])
plt.bar(np.arange(5)+1.5*bar_width,tau_mean_err[4,:],bar_width,color=cmap2[3],label='order 4')#,yerr=tau_stdev_err[4,:])
ax.set_yscale("log")
plt.legend(frameon=False, loc='upper right'); # plt.legend()
plt.ylabel(r'Mean error',fontsize=14)
#plt.xlabel('Membrane potential (mV)',fontsize=16)
# plt.xticks([0,1,2,3,4],[])
plt.yticks([10**-1,10**0,10**1, 10**2, 10**3],[10**-1,10**0, 10**1, 10**2, 10**3])
ax.set_xlim([-0.5,5])
ax.set_xlabel('Ion type',fontsize=14)
ax.set_xticks([0,1, 2, 3, 4],['K','Na','Ca','IH', 'KCa'], fontsize=14)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# ax=plt.subplot(4,1,4)
# plt.bar(np.arange(5)-1.5*bar_width,tau_no_fit_pct[3,:],bar_width,color=cmap2[0],label='order 1')
# plt.bar(np.arange(5)-bar_width/2,tau_no_fit_pct[2,:],bar_width,color=cmap2[1],label='order 2')
# plt.bar(np.arange(5)+bar_width/2,tau_no_fit_pct[1,:],bar_width,color=cmap2[2],label='order 3')
# plt.bar(np.arange(5)+1.5*bar_width,tau_no_fit_pct[4,:],bar_width,color=cmap2[3],label='order 4')
# plt.legend()
# plt.ylabel(r'No fit pct.',fontsize=16)
# plt.xlabel('Ion type',fontsize=16)
# plt.xticks([0,1, 2, 3, 4],['K','Na','Ca','IH', 'KCa'],fontsize=16)
# plt.yticks(np.arange(0,31,10),np.arange(0,31,10))
# ax.set_xlim([-0.5,5])
# ax.spines['right'].set_visible(False)
# ax.spines['top'].set_visible(False)

rr = plt.gcf()
rr.text(0.008, 0.9, 'D', fontsize=16, weight='bold')
rr.text(0.49, 0.9, 'H',  fontsize=16, weight='bold')

plt.tight_layout()
#plt.show()
fig.savefig("fig3_manfit_compare_2025.pdf", bbox_inches='tight', dpi=300)
