-entender os datasets dos artigos
eles tem as mesmas colunas,

 'time/s', 'control/V/mA', 'Ecell/V', '<I>/mA', 'Q discharge/mA.h', 'Q charge/mA.h', 'control/V', 'control/mA', 'cycle number'

 O estudo utilizou 130 células comerciais de três químicas diferentes: NCA (LiNi0.86​Co0.11​Al0.03​O2​), NCM (LiNi0.83​Co0.11​Mn0.07​O2​) e uma mistura de NCM+NCA.

- entender como foi feita a extração das features nesses datasets
foi feita das curvas de decaimento
- verificar os tipos de falhas que estão presentes nos datasets -> não tem falhas, só trata sobre ciclos

- verificar a semelhança dessas falhas com as falhas do gabriel -> não tem 



















































Features Nativas (Medições Diretas):

voltage_measured: Tensão medida
current_measured: Corrente medida
temperature_measured: Temperatura medida

Features de Engenharia (Temporais/Derivativas):

 4. dV: Diferença de tensão entre o instante atual e o anterior (first difference / derivada curta). 
 5. dT: Diferença de temperatura entre o instante atual e o anterior.
 6. V_roll_mean: Média móvel da tensão considerando uma janela dos últimos 5 registros (sliding window). 
 7. T_roll_mean: Média móvel da temperatura considerando uma janela dos últimos 5 registros.
8. I_roll_mean: Média móvel da corrente considerando uma janela dos últimos 5 registros. 
9. dV_long: Diferença de tensão de longo prazo, calculada entre o instante atual e o instante de 20 passos de tempo atrás (diff(20)).