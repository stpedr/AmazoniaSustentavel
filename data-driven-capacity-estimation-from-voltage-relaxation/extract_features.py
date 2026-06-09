import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

# Set plotting style
plt.style.use('seaborn-v0_8-whitegrid')

dataset_dir = r"C:\Users\pedro\OneDrive\Documentos\pedro\projetps\AmazoniaSustentavel\data-driven-capacity-estimation-from-voltage-relaxation\Dataset_1_NCA_battery\Dataset_1_NCA_battery"
figures_dir = os.path.join(os.path.dirname(dataset_dir), "figures")

if not os.path.exists(figures_dir):
    os.makedirs(figures_dir)

# Load a representative CSV file (or glob all of them). For speed, we'll pick CY25-05_1-#1.csv
file_path = os.path.join(dataset_dir, "CY25-05_1-#1.csv")
print(f"Loading data from {file_path}")

df = pd.read_csv(file_path)

# Drop rows where cycle number is NaN
df = df.dropna(subset=['cycle number'])

features = []

# Group by cycle number
for cycle, group in df.groupby('cycle number'):
    if cycle == 0:
        continue # Skip initial resting cycle
        
    # Discharge is where current < 0 or Q discharge increases. In these datasets, usually I < 0
    discharge_phase = group[group['<I>/mA'] < 0]
    charge_phase = group[group['<I>/mA'] > 0]
    
    if len(discharge_phase) == 0:
        continue
        
    # Calculate Max Discharge Capacity for this cycle (this is our target/SOH proxy)
    max_discharge_capacity = discharge_phase['Q discharge/mA.h'].max()
    
    # 1. Total Discharge Energy (Trapezoidal integration of V * I dt)
    # Note: Power = V * I. Ecell/V is voltage, <I>/mA is current. time/s is time.
    # Convert mA to A for energy in Watt-seconds (Joules)
    times = discharge_phase['time/s'].values
    voltages = discharge_phase['Ecell/V'].values
    currents_A = np.abs(discharge_phase['<I>/mA'].values) / 1000.0  # Absolute current in Amperes
    
    if len(times) > 1:
        power = voltages * currents_A
        discharge_energy = np.trapz(power, times)
    else:
        discharge_energy = 0
        
    # 2. Average Discharge Voltage
    avg_discharge_voltage = discharge_phase['Ecell/V'].mean()
    
    # 3. Voltage Variance During Discharge (Indicates instability/changes in slope)
    voltage_variance = discharge_phase['Ecell/V'].var()
    
    # 4. Constant Current (CC) Charge Time
    # Usually the first part of charging where current is constant and max
    if len(charge_phase) > 0:
        max_curr = charge_phase['<I>/mA'].max()
        # threshold for CC phase (e.g. 95% of max current)
        cc_phase = charge_phase[charge_phase['<I>/mA'] >= max_curr * 0.95]
        cc_charge_time = cc_phase['time/s'].max() - cc_phase['time/s'].min() if len(cc_phase) > 0 else 0
    else:
        cc_charge_time = 0
        
    # 5. Internal Resistance estimate proxy (Voltage drop at start of discharge)
    # Look at the first few seconds of discharge
    initial_voltage_drop = voltages[0] - voltages[min(5, len(voltages)-1)] if len(voltages) > 0 else 0
    internal_resistance_proxy = initial_voltage_drop / max(0.001, currents_A[0]) if len(currents_A) > 0 else 0

    features.append({
        'Cycle': cycle,
        'SOH_Capacity': max_discharge_capacity,
        'Discharge_Energy': discharge_energy,
        'Avg_Discharge_Voltage': avg_discharge_voltage,
        'Voltage_Variance': voltage_variance,
        'CC_Charge_Time': cc_charge_time,
        'Internal_Resistance_Proxy': internal_resistance_proxy
    })

feature_df = pd.DataFrame(features)

# Normalize SOH Capacity to get SOH (State of Health) percentage
max_initial_capacity = feature_df['SOH_Capacity'].max()
feature_df['SOH'] = feature_df['SOH_Capacity'] / max_initial_capacity

# Plot 1: SOH Degradation
plt.figure(figsize=(10, 5))
plt.plot(feature_df['Cycle'], feature_df['SOH'], marker='o', linestyle='-', color='b')
plt.title('Degradação do SOH ao Longo dos Ciclos')
plt.xlabel('Ciclo')
plt.ylabel('SOH (Normalizado)')
plt.grid(True)
plt.savefig(os.path.join(figures_dir, 'SOH_degradation.png'), dpi=300, bbox_inches='tight')
plt.close()

# Plot 2: Correlation Heatmap
cols_to_correlate = ['SOH', 'Discharge_Energy', 'Avg_Discharge_Voltage', 
                     'Voltage_Variance', 'CC_Charge_Time', 'Internal_Resistance_Proxy']

corr_matrix = feature_df[cols_to_correlate].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
plt.title('Matriz de Correlação das Features com o SOH')
plt.savefig(os.path.join(figures_dir, 'correlation_heatmap.png'), dpi=300, bbox_inches='tight')
plt.close()

# Plot 3: Voltage & Current Curve of a Anomaly / Late Cycle (Last Cycle vs First Cycle)
first_cycle = feature_df['Cycle'].min()
last_cycle = feature_df['Cycle'].max()

plt.figure(figsize=(12, 6))
first_cycle_data = df[df['cycle number'] == first_cycle]
last_cycle_data = df[df['cycle number'] == last_cycle]

plt.plot(first_cycle_data['time/s'] - first_cycle_data['time/s'].min(), first_cycle_data['Ecell/V'], label=f'Ciclo {first_cycle} (Saudável)', color='g')
plt.plot(last_cycle_data['time/s'] - last_cycle_data['time/s'].min(), last_cycle_data['Ecell/V'], label=f'Ciclo {last_cycle} (Degradado)', color='r', alpha=0.7)

plt.title('Análise Exploratória: Tensão de Descarga/Carga (Ciclos Inicial vs Final)')
plt.xlabel('Tempo Relativo (s)')
plt.ylabel('Tensão (V)')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(figures_dir, 'voltage_current_anomaly.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"Features extraidas com sucesso. Tamanho do dataset de features: {len(feature_df)}")
print(f"Matriz de Correlação com SOH:")
print(corr_matrix['SOH'].sort_values(ascending=False))

# Salve as features caso o usuario queira treinar algoritmos depois
feature_df.to_csv(os.path.join(figures_dir, 'extracted_features_NCA.csv'), index=False)
print("Arquivos salvos em", figures_dir)
