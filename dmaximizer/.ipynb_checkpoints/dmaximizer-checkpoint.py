#Duty cycle maximize by energy neutrality
import pulp
import matplotlib.pyplot as plt

#Harvested energy for each epoch
hraw = [0, 0, 0, 0, 0, 0, 0.01, 0.33, 0.57, 0.82, 1.58, 1.3, 
        1.19, 1.02, 0.71, 0.2, 0.03, 0, 0, 0, 0, 0, 0, 0]
henergy = [i *0.0165*1000000*0.15*1000/(60*60) for i in hraw]
HMAX = 3000 #Maximum harvested energy

SLOTS = len(hraw)

DMIN = 1 #20% duty cycle = 100 mWhr
DMAX = 5 #100% duty cycle = 500 mWhr
DSCALE = 100 #scale to convert action value to actual power consumption
NMAX = DMAX * DSCALE #max energy consumption

BMIN = 1000.0
BMAX = 40000.0
BOPT = 0.6 * BMAX
BINIT = 0.6 * BMAX

model = pulp.LpProblem('ENO', pulp.LpMinimize)

#the epochs in a window of SLOTS numbers of slots
epoch = ['epoch_%d' %i for i in range(1, SLOTS + 1, 1)]

# create a dictionary of pulp LpVariables with keys corresponding to values in the list epoch
action_dict = pulp.LpVariable.dicts('action', epoch , 
                                   lowBound=DMIN, upBound=DMAX, 
                                   cat=pulp.LpInteger)

#Create dictionary of harvested energy
henergy_dict = dict(zip(epoch, henergy))

total_consumed_energy = pulp.lpSum([action_dict[key] for key in epoch]) * DSCALE
deviation = (BOPT - (BINIT + sum(henergy) - total_consumed_energy))

#Objective function is to minimize the deviation from optimal batteyr level
#Create a variable t such that |deviation|<=t
# -t <= deviation <= t
t = pulp.LpVariable('t', lowBound=0, cat='Continuous')
model += t


#Constraints A
model += deviation <= t
model += deviation >= -t

#Constraints B
#Create a dummy list of lists with entries [[epoch_1], [epoch_1, epoch_2], .... ]
dummy = [epoch[0:i] for i in range(1,len(epoch)+1)]

#dictionary of cumulative action variables [[a1], [a1 + a2],....]
a_var_cum = {}

#dictionary of cumulative harvested energy constants [[h1], [h1 + h2],....]
henergy_cum = {} 

for i in range(0 , len(epoch)):
    a_var_cum[epoch[i]] = pulp.lpSum([action_dict[key]*DSCALE for key in dummy[i]])
    henergy_cum[epoch[i]] = sum([henergy_dict[key] for key in dummy[i]])
    #henergy_cum = dict(zip(epoch, np.add.accumulate(henergy)))

for key in epoch:
    model += BINIT + henergy_cum[key] - a_var_cum[key] <= BMAX
    model += BINIT + henergy_cum[key] - a_var_cum[key] >= BMIN

model.solve()
print(pulp.LpStatus[model.status])

#Create dictionary for optimized actions
opt_act = {}
for var in epoch:
    opt_act[var] = action_dict[var].varValue
#    print ("The energy consumption for {0} is {1}".format(var, opt_act[var]*DSCALE))

#Create dictionary for node energy consumption from optimized actions
a_val = opt_act.values()
n_val = [x*DSCALE for x in a_val] #convert action -> energy consumed
node_consumption_dict = dict(zip(epoch,n_val))

#Create battery dictionary
batt_dict = {}
previous_batt = BINIT
for x in epoch[0:]:
    batt_dict[x] = previous_batt + henergy_dict[x] - node_consumption_dict[x]
    previous_batt = batt_dict[x]
    
#DISPLAY OUTPUT
print("The total harvested energy is {}".format(sum(henergy)))

total_consumption = sum(node_consumption_dict.values())
print ("The total energy consumption is {}".format(total_consumption))

t_val = pulp.value(model.objective)
print ("The total deviation from BOPT is {}".format(t_val))

#PERFORMANCE LOG
print("BINIT = {}".format(BINIT))
print("[epoch, battery, henergy, nenergy]")
for x in epoch:
    print([x, batt_dict[x], henergy_dict[x], node_consumption_dict[x] ])
    
#PLOT GRAPHS    
plt.plot([batt_dict[key]/BMAX for key in epoch])
plt.plot([henergy_dict[key]/HMAX for key in epoch])
plt.plot([node_consumption_dict[key]/NMAX for key in epoch])
plt.plot([BOPT/BMAX]*SLOTS)
plt.show





    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    