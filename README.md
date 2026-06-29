# Palavritas: análise de retenção

Case técnico para a vaga de Analista de Dados (Produto e Growth) do the news. A pergunta que move o trabalho: o que determina se um usuário volta a jogar o Palavritas, e o que dá para fazer para aumentar isso.

## Arquivos

- `analise.py`: todo o código, da limpeza à análise. Está em formato de células (`# %%`), pensado para rodar passo a passo no VS Code ou Jupyter, mas também roda de cima a baixo de uma vez.
- `documento_analise.md`: o documento de análise escrito para leitura não técnica, com as três entregas (limpeza e diagnóstico, análise, proposta). Os números estatísticos exatos estão numa nota no final.
- Os três CSVs do dataset (`*sessions*.csv`, `*attempts*.csv`, `*user_profile*.csv`) devem ficar na mesma pasta do `analise.py`. O script localiza cada um pelo nome.

## Como rodar

Requer Python 3 com as bibliotecas:

```
pip install pandas numpy scipy
```

Depois, abra `analise.py` no VS Code (extensão Python) e rode célula por célula, ou execute o arquivo inteiro. O código foi escrito para rodar na ordem, de cima para baixo: a limpeza de sessões vem primeiro, porque as etapas seguintes dependem da tabela já limpa.

## Como o código está organizado

O método é o mesmo em toda a limpeza: diagnostico o problema, olho os dados antes de mexer, trato, e confirmo o resultado. A regra que segui o tempo todo: dado bagunçado mas real eu padronizo, dado impossível eu descarto.

1. **Sessões** (`sessions` -> `s`): remoção de duplicatas, padronização de aparelho e data, descarte de partidas impossíveis.
2. **Tentativas** (`attempts` -> `a`): tratamento de duplicatas e conflitos, validação dos palpites contra a palavra do dia, remoção de órfãs.
3. **Perfil** (`profile` -> `p`): padronização de cargo e food delivery, descarte da coluna de cidade, decisão sobre nulos.
4. **Análise**: agregação por usuário, definição de retenção por coorte, e testes de significância dos fatores que poderiam explicar a retenção.

## Principais achados

- A retenção de 30 dias é de 30,4% (de cada 10 que começam, cerca de 3 seguem ativos um mês depois).
- Voltar no dia seguinte é dominado por hábito já formado. Nenhum fator sobre o qual o time pode agir move esse número.
- O único fator acionável associado a mais retenção é o ritual matinal (jogar de manhã, que nos dados é inseparável de receber a newsletter). Efeito real, porém pequeno.
- Perfil demográfico (setor, aparelho, cargo, idade) não explica retenção.

A proposta, detalhada no documento, é um lembrete de fim de dia para quem não jogou de manhã, testado como experimento A/B.

O detalhe de cada decisão está no `documento_analise.md`.
