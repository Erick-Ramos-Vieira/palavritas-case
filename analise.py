# %% Importar bibliotecas
import pandas as pd
import numpy as np
import glob

# %% Achar CSV
def achar(texto):
    hits = glob.glob(f'*{texto}*.csv')
    return hits[0]

# %% Definir tabela sessions

sessions = pd.read_csv(achar('sessions'))

# %% Conferir tabela sessions
sessions.shape

# %% Verificar as 5 primeiras linhas
sessions.head()

# %% Quantos usuários únicos?
sessions['user_id'].nunique()

# %% Tem linhas repetidas?
sessions.duplicated().sum()

# %% Verificar duplicatas
sessions[sessions.duplicated(keep=False)].sort_values('session_id').head(6)

# %% Criar tabela sem duplicatas
s = sessions.drop_duplicates()

# %% Verificar se a tabela foi limpa
print('Original:', sessions.shape)
print('Limpa:   ', s.shape)
print('Duplicatas na limpa:', s.duplicated().sum())

# %% Procurar celulas vazias em cada coluna
s.isna().sum()

# %% Verificar result vazios
s[s['result'].isna()].head(10)

# %% Tipos de device
s['device'].value_counts()

# %% padronizar todos como minúsculo 
s['device'].str.lower().value_counts()

# %% Padronizar o nomes do device
s['device'] = s['device'].str.lower().map({'ios': 'iOS', 'android': 'Android'})

# %% Verificar tipo de Device
s['device'].value_counts(dropna=False)

# %% Qntd. de word_date sem DD/MM/YYYY
s['word_date'].str.contains('/').value_counts()

# %% Tipos de word_date falsos
print('Sem barra (False):')
print(s.loc[~s['word_date'].str.contains('/'), 'word_date'].head().tolist())
print()
print('Com barra (True):')
print(s.loc[s['word_date'].str.contains('/'), 'word_date'].head().tolist())

# %% Transformar em datetime64
s['word_date'] = pd.to_datetime(s['word_date'], format='mixed', dayfirst=True)

# %% Confirmar a conversão
print('tipo da coluna:', s['word_date'].dtype)
print('nulos novos:', s['word_date'].isna().sum())
print('intervalo:', s['word_date'].min(), '→', s['word_date'].max())

# %% Ver linhas invalidas
fora_de_intervalo  = ~s['attempts'].between(1, 6)      # attempts não está entre 1 e 6
tempo_invalido = s['time_to_complete_sec'] <= 0    # tempo zero ou negativo
sem_resultado  = s['result'].isna()                # result vazio

impossivel = fora_de_intervalo | tempo_invalido | sem_resultado

print('attempts fora de 1-6:', fora_de_intervalo.sum())
print('tempo <= 0          :', tempo_invalido.sum())
print('result vazio        :', sem_resultado.sum())
print('total impossível (união):', impossivel.sum())

# %% Remover linhas impossíveis de concerto
s = s[~impossivel]

# %% Confirmar remoção
print('linhas agora:', s.shape[0], '(esperado: 39849)')
print('attempts fora de 1-6:', (~s['attempts'].between(1, 6)).sum())
print('tempo <= 0          :', (s['time_to_complete_sec'] <= 0).sum())
print('result vazio        :', s['result'].isna().sum())

# %% Comparar attempts com result
pd.crosstab(s['attempts'], s['result'])

# %% Definir tabela attempts
attempts = pd.read_csv(achar('attempts'))

# %% Conferir tamanho
attempts.shape

# %% Ver as 5 primeiras linhas
attempts.head()

# %% Verificar duplicatas
print('linha 100% idêntica            :', attempts.duplicated().sum())
print('mesmo (session_id, attempt_number):', attempts.duplicated(subset=['session_id','attempt_number']).sum())

# %% Confirmar as duplicatas

attempts[attempts.duplicated(subset=['session_id','attempt_number'], keep=False)] \
    .sort_values(['session_id','attempt_number']).head(8)

# %% Quantos lances a tabela deveria ter?
esperado = s['attempts'].sum()
print('esperado:', esperado)
print('real    :', attempts.shape[0])
print('excesso :', attempts.shape[0] - esperado)

# %% Remover órfãs (session_id que não existe em sessions)
ids_validos = set(s['session_id'])
orfa = ~attempts['session_id'].isin(ids_validos)
print('órfãs:', orfa.sum())
a = attempts[~orfa]

# %% Remover guess que não tem 5 letras
tam_ruim = a['guess'].str.len() != 5
print('tamanho errado:', tam_ruim.sum())
a = a[~tam_ruim]

# %% Conferir verde/amarelo com a palavra do dia
word_map = s.set_index('session_id')['word'].to_dict()

def verde_amarelo(palpite, palavra):
    palpite, palavra = palpite.upper(), palavra.upper()
    verdes = sum(p == w for p, w in zip(palpite, palavra))
    resto = [w for p, w in zip(palpite, palavra) if p != w]
    amarelos = 0
    for p, w in zip(palpite, palavra):
        if p != w and p in resto:
            amarelos += 1
            resto.remove(p)
    return verdes, amarelos

palavra_do_dia = a['session_id'].map(word_map)
res = [verde_amarelo(g, w) for g, w in zip(a['guess'], palavra_do_dia)]
v_calc  = pd.Series([r[0] for r in res], index=a.index)
am_calc = pd.Series([r[1] for r in res], index=a.index)
num_ruim = (v_calc != a['correct_positions']) | (am_calc != a['correct_letters'])
print('números impossíveis:', num_ruim.sum())
a = a[~num_ruim]

# %% Manter 1 linha por tentativa (tira cópias e conflitos)
antes = a.shape[0]
a = a.drop_duplicates(subset=['session_id','attempt_number'], keep='first')
print('removidas:', antes - a.shape[0])

# %% Confirmar limpeza
print('attempts limpa:', a.shape[0])
print('esperado      :', s['attempts'].sum())
print('session_id    :', a['session_id'].nunique(), '| sessions:', s['session_id'].nunique())

# %% Definir tabela user_profile
profile = pd.read_csv(achar('user_profile'))

# %% Conferir tamanho
profile.shape

# %% Ver as 5 primeiras linhas
profile.head()

# %% Procurar celulas vazias
profile.isna().sum()

# %% job_role: caixa misturada
profile['job_role'].value_counts()

# %% orders_food_delivery: booleano bagunçado
profile['orders_food_delivery'].value_counts()

# %% city: cidade combina com o estado?
cidade_uf = {'São Paulo':'SP','Rio de Janeiro':'RJ','Belo Horizonte':'MG',
             'Brasília':'DF','Curitiba':'PR','Porto Alegre':'RS'}
uf_correta = profile['city'].map(cidade_uf)
impossivel_cidade = uf_correta.notna() & (uf_correta != profile['state'])
print('cidades não-nulas        :', profile['city'].notna().sum())
print('geograficamente impossíveis:', impossivel_cidade.sum())

# %% Criar tabela limpa (sem duplicatas pra remover)
p = profile.copy()

# %% Padronizar job_role (caixa)
p['job_role'] = p['job_role'].str.title()

# %% Conferir
p['job_role'].nunique()

# %% Padronizar orders_food_delivery (texto -> booleano)
p['orders_food_delivery'] = p['orders_food_delivery'].map(
    {'True': True, 'False': False, 'sim': True, 'não': False})

# %% Conferir
p['orders_food_delivery'].value_counts(dropna=False)

# %% Descartar city (geograficamente impossível, sem sinal)
p = p.drop(columns='city')

# %% Conferir que saiu
p.shape

# %% Nulos em age_range / salary_range: manter (decisão documentada)
# Não removo linha nem imputo: o vazio é numa coluna, a pessoa segue útil
# nas demais variáveis. Trato o NaN localmente em cada análise.
p[['age_range','salary_range']].isna().sum()

# %% Criar coluna "jogou de manhã" (5h-11h)
s['manha'] = s['session_hour'].between(5, 11)

# %% Teste: começar de manhã afeta o D30? (qui-quadrado)
from scipy.stats import chi2_contingency

prim = s.sort_values('word_date').groupby('user_id').first()
tab = pd.crosstab(prim['manha'], prim['active_d30'])
chi2, pval, dof, esp = chi2_contingency(tab)

print(tab)
print('p-valor:', round(pval, 4), '| significativo' if pval < 0.05 else '| não significativo')
print('phi (efeito):', round((chi2 / tab.values.sum()) ** 0.5, 3))

# %% Streak prevê voltar amanhã? (nível partida, sem o efeito circular)
print('corr streak_day x played_next_day:', round(s['streak_day'].corr(s['played_next_day']), 3))

# %% Preditores acionáveis vs voltar amanhã (nível partida)
s['venceu'] = (s['result'] == 'win')
for col in ['manha', 'newsletter_open_before_game', 'venceu', 'device']:
    print(col)
    print(s.groupby(col)['played_next_day'].mean().round(3))
    print()

# %% Entrega 2: perfil explica retenção? (D30 coorte x perfil)
prim = s.sort_values('word_date').groupby('user_id').first()
d30 = prim['active_d30'].rename('d30').astype(int)
m = p.merge(d30, on='user_id', how='inner')   # p = user_profile limpa

for col in ['sector','salary_range','primary_device','orders_food_delivery','job_role','age_range','company_size']:
    sub = m.dropna(subset=[col])
    tab = pd.crosstab(sub[col], sub['d30'])
    chi2, pv, dof, esp = chi2_contingency(tab)
    phi = (chi2 / tab.values.sum()) ** 0.5
    print(f'{col:22s} p={pv:.3f}  phi={phi:.3f}', '<-- significativo' if pv < 0.05 else '')

# %% Entrega 3: dimensionar o alvo do lembrete (quem não joga de manhã)
print('% partidas fora da manhã:', round((~s['manha']).mean()*100, 1), '%')
prim = s.sort_values('word_date').groupby('user_id').first()
print('D30 manhã    :', round(prim[prim['manha']]['active_d30'].mean()*100, 1), '%')
print('D30 não-manhã:', round(prim[~prim['manha']]['active_d30'].mean()*100, 1), '%')

# %% Montar tabela final por usuário (base do dashboard)
s['venceu'] = (s['result'] == 'win')

# comportamento agregado por usuário
agg = s.groupby('user_id').agg(
    n_partidas=('session_id', 'size'),
    streak_max=('streak_day', 'max'),
    taxa_vitoria=('venceu', 'mean'),
    tempo_medio_seg=('time_to_complete_sec', 'mean'),
    pct_manha=('manha', 'mean'),
    pct_newsletter=('newsletter_open_before_game', 'mean'),
    taxa_volta_dia_seguinte=('played_next_day', 'mean'),
    device=('device', lambda x: x.mode().iloc[0]),
).reset_index()

# alvo e comportamento da PRIMEIRA partida (coorte)
prim = s.sort_values('word_date').groupby('user_id').agg(
    reteve_d30=('active_d30', 'first'),
    comecou_manha=('manha', 'first'),
).reset_index()

base = agg.merge(prim, on='user_id')
base['reteve_d30'] = base['reteve_d30'].astype(int)
base['comecou_de_manha'] = base['comecou_manha'].map({True: 'Manhã', False: 'Outro horário'})
base = base.drop(columns='comecou_manha')

# juntar perfil (left join: mantém os 1200, perfil fica vazio pra quem não respondeu)
base = base.merge(
    p[['user_id', 'sector', 'salary_range', 'age_range', 'company_size', 'orders_food_delivery']],
    on='user_id', how='left')

# salvar pra alimentar o dashboard
base.to_csv('dashboard_dados.csv', index=False)
print('tabela do dashboard:', base.shape)
base.head()

# %% RESUMO: testes de significância
# Consolidação dos testes estatísticos feitos ao longo da análise.
from scipy.stats import chi2_contingency

print('=== 1. Começar de manhã x retenção D30 ===')
prim = s.sort_values('word_date').groupby('user_id').first()
tab = pd.crosstab(prim['manha'], prim['active_d30'])
chi2, pval, dof, esp = chi2_contingency(tab)
phi = (chi2 / tab.values.sum()) ** 0.5
print(f'p-valor = {pval:.4f} | phi = {phi:.3f} | {"significativo" if pval < 0.05 else "não significativo"}')
print('-> efeito real porém pequeno\n')

print('=== 2. Perfil x retenção D30 (7 variáveis) ===')
d30 = prim['active_d30'].astype(int).rename('d30')
m = p.merge(d30, on='user_id', how='inner')
for col in ['sector','salary_range','primary_device','orders_food_delivery','job_role','age_range','company_size']:
    sub = m.dropna(subset=[col])
    t = pd.crosstab(sub[col], sub['d30'])
    c, pv, _, _ = chi2_contingency(t)
    ph = (c / t.values.sum()) ** 0.5
    print(f'  {col:22s} p={pv:.3f} phi={ph:.3f}', '<-- significativo' if pv < 0.05 else '')
print('-> só salário é significativo, mas cautela: amostra parcial + múltiplas comparações\n')

print('=== 3. Circularidade do streak (não é teste, é diagnóstico) ===')
corr_partida = s['streak_day'].corr(s['played_next_day'])
usuarios = s.groupby('user_id').agg(streak_max=('streak_day','max'),
                                    taxa_next=('played_next_day','mean'))
corr_usuario = usuarios['streak_max'].corr(usuarios['taxa_next'])
print(f'corr nível-partida = {corr_partida:.3f} | corr nível-usuário = {corr_usuario:.3f}')
print('-> a discrepância (0,02 vs 0,82) revela que o streak é circular, não preditor')

# %%
