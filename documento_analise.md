# Palavritas: análise de retenção

Documento preparado para a reunião com o Head de Produto. Responde à pergunta "o que está determinando se um usuário volta a jogar, e o que podemos fazer para aumentar isso?", em três partes: o que encontrei e limpei nos dados, o que a análise mostrou, e o que eu proporia testar. Os números estatísticos exatos estão reunidos numa nota no final, para quem quiser conferir.

---

## 1. Limpeza e diagnóstico

Antes de tentar responder o que faz um usuário voltar, precisei garantir que os dados eram confiáveis. Comecei sempre olhando cada coluna antes de mexer, e segui uma regra simples o tempo todo: dado bagunçado mas real eu padronizo, dado impossível eu descarto. Abaixo, o que encontrei em cada um dos três arquivos e o que decidi.

### Sessões (a base principal)

Parti de 41.157 linhas e cheguei a 39.849 partidas confiáveis.

A primeira coisa que achei foram 1.198 linhas duplicadas, partidas inteiras repetidas. Removi, porque a mesma partida contada duas vezes inflaria o engajamento e bagunçaria qualquer média.

O campo de aparelho vinha escrito de seis formas diferentes (iOS, ios, IOS, Android, android, ANDROID), mas eram só dois aparelhos. Unifiquei em iOS e Android, senão uma comparação entre os dois sairia errada, com o mesmo device espalhado em vários grupos.

A data do desafio aparecia em dois formatos: o brasileiro (dia/mês/ano) e o internacional (ano-mês-dia). Padronizei tudo para um formato de data único. Isso não é cosmético, porque a pergunta central depende de tempo ("o usuário voltou no dia seguinte?"), e isso é impossível de calcular enquanto as datas são texto misturado.

Por fim, descartei 110 partidas que simplesmente não podem existir: jogos com 0, 7 ou 8 tentativas (o jogo só vai de 1 a 6), tempo de jogo zero ou negativo, ou resultado em branco. Aqui não dava para consertar, é dado impossível, então saiu.

Um ponto que não é limpeza mas vale registrar, porque muda a análise: o número de tentativas praticamente entrega o resultado. Quem joga 1, 2 ou 3 tentativas sempre ganhou, quem chega a 6 sempre perdeu, sem nenhuma exceção. Ou seja, "tentativas" e "resultado" carregam a mesma informação. Não posso usar os dois como se fossem pistas independentes, e nenhum deles é uma causa de o usuário voltar. Os dois são o placar da partida, não comportamento.

### Tentativas (o lance-a-lance)

Essa tabela abre cada partida palpite por palpite, é o detalhe de dentro do jogo, uma tabela de apoio. Saí de 147.270 para 142.702 linhas.

O problema principal estava escondido: "duplicata" aqui tinha dois sentidos. Havia 752 linhas idênticas (cópia boba), mas também cerca de 3.500 casos em que a mesma tentativa tinha dois palpites diferentes, como se duas partidas tivessem sido empilhadas sob o mesmo jogo. Tentei descobrir qual era a verdadeira cruzando com a palavra do dia e com o que a tabela de sessões dizia da partida, mas provei que era impossível: as duas versões eram internamente válidas (mesmo tamanho, mesmo resultado, mesma palavra final). Como a cópia corrompida sempre tinha sido acrescentada depois, fiquei com a primeira ocorrência de cada tentativa, que é o registro original.

Aproveitei a palavra do dia para validar os palpites: recalculei quantos acertos cada chute deveria ter e comparei com o que estava na tabela. Praticamente toda a base se mostrou consistente, o que me deixou confiante na qualidade dela e isolou os poucos registros corrompidos. Também removi 220 partidas que não existiam na tabela de sessões e palpites que não tinham cinco letras (impossível num jogo de cinco letras).

O que mais me deu segurança foi uma checagem cruzada. Somando o número de tentativas registrado em sessões, a tabela de palpites deveria ter cerca de 142.807 linhas. Limpando defeito por defeito, cheguei a 142.702. Dois caminhos independentes batendo quase no mesmo número, sinal de que a limpeza não foi no chute.

### Perfil dos usuários (a pesquisa)

São 800 pessoas, uma por linha. Aqui o primeiro alerta é de escopo: nem todo mundo que joga respondeu a pesquisa (a base de jogadores tem cerca de 1.200 usuários), então qualquer conclusão tirada do perfil vale só para essa fatia.

O campo de food delivery misturava True, False, "sim" e "não" para dizer a mesma coisa, e padronizei tudo para verdadeiro/falso. O campo de cargo tinha o mesmo problema de maiúsculas e minúsculas das sessões (Gerente e gerente contados separados), que unifiquei.

A coluna de cidade eu descartei inteira, e essa foi a decisão mais drástica. Das cidades preenchidas, 95% eram geograficamente impossíveis, como Belo Horizonte aparecendo no Rio Grande do Norte. Somado a isso, 37% do campo estava vazio. Não dava para confiar nem para consertar (não sei se o errado é a cidade ou o estado), então a coluna não tinha informação aproveitável. Mantive o estado, que está íntegro.

Sobre os vazios em idade e salário, tomei uma decisão consciente de não mexer. Não removi essas pessoas, porque jogar fora alguém por causa de uma célula em branco descartaria tudo o que ela tem de útil (setor, aparelho, food delivery). E não preenchi os vazios com um valor médio, porque isso seria inventar dado e enviesar a análise. Mantive os vazios e vou tratá-los na hora de analisar cada variável, usando só quem informou salário quando o assunto for salário, e todo mundo nas demais perguntas. Vale notar que quem não informou pode ser sistematicamente diferente de quem informou, então qualquer leitura sobre salário carrega essa ressalva.

### O que isso significa para a análise

Saio da limpeza com três avisos que vou carregar para a próxima etapa. As variáveis "tentativas" e "resultado" são redundantes e não explicam retenção. O perfil cobre só uma parte dos usuários e pode ter viés de quem escolheu responder. E os dados estão por partida, não por pessoa, então preciso agregá-los por usuário antes de cruzar com o perfil.

---

## 2. Análise: o que prediz retenção

Antes de cruzar qualquer coisa, precisei resolver uma questão de granularidade. Os dados estão por partida, mas a pergunta é sobre o usuário, então agreguei tudo por pessoa. E precisei definir o que "retenção de 30 dias" significa, porque a informação vinha medida por partida (ativo 30 dias após aquela partida específica), o que varia dentro do mesmo usuário. Adotei a definição mais usada: olhei a primeira partida de cada pessoa e perguntei se ela seguia ativa 30 dias depois. Por essa medida, a retenção de 30 dias do Palavritas é de 30,4%, ou seja, de cada 10 pessoas que começam, cerca de 3 ainda jogam um mês depois.

Olhei os dois alvos separados, porque eles têm naturezas opostas.

Voltar no dia seguinte se mostrou um comportamento de hábito. À primeira vista, a sequência de dias seguidos (o streak) explicava quase tudo. Mas percebi que isso é uma armadilha: o streak é construído a partir de voltar dias seguidos, então dizer que "quem tem sequência longa volta amanhã" é circular, é o mesmo comportamento medido de dois jeitos. Quando tirei essa circularidade e testei os fatores que o time realmente controla (horário, newsletter, ter vencido a partida, aparelho), nenhum deles move o ponteiro: a chance de voltar no dia seguinte fica em torno de 22% independente de qualquer um deles. Ou seja, voltar amanhã é dominado por hábito já formado, não por nada que se possa mexer na partida.

Reter 30 dias é mais difícil de prever, e foi onde encontrei o único sinal sobre o qual o time pode agir. Quem começa jogando de manhã retém 34,5%, contra 28,5% de quem começa em outro horário, uma diferença de 6 pontos percentuais. Testei se essa diferença poderia ser fruto do acaso, e ela se mostrou consistente: a probabilidade de ela aparecer só por sorte é de cerca de 4%. É um efeito real, porém pequeno. Um ponto importante: nos dados, jogar de manhã e abrir a newsletter são praticamente a mesma coisa, porque a newsletter nunca abre fora da manhã. Então não consigo separar o "efeito da manhã" do "efeito da newsletter" olhando só o histórico. Os dois estão grudados.

Por fim, testei se o perfil explica retenção, e no geral não explica. Setor, aparelho, cargo, idade, food delivery, porte da empresa, nenhum prevê a retenção de forma consistente. A única exceção foi o salário, com uma relação que dificilmente seria acaso. Mesmo assim, trato esse achado com cautela: vem de uma amostra parcial (só os 800 que responderam a pesquisa, com viés de quem escolhe responder), e foi o único resultado forte entre sete variáveis testadas. Quando se testa muita coisa, é esperado que uma se destaque por sorte. Não é base sólida para decidir nada.

O resumo da análise é que a retenção do Palavritas é movida por hábito, não por características da partida nem por perfil demográfico. As relações mais fortes que apareceram eram enganosas (a sequência circular, o número de partidas). O único empurrão real sobre o qual dá para agir é o ritual matinal, pequeno mas consistente, e impossível de separar da newsletter sem um experimento.

---

## 3. Proposta

O que eu mudaria parte direto do único achado sobre o qual dá para agir: 68,5% das partidas acontecem fora da manhã, e quem não tem o ritual matinal retém 6 pontos a menos. Existe um grupo grande recebendo menos do gatilho que está associado a reter.

**Hipótese:** acredito que parte da retenção se perde em usuários que não jogam de manhã e acabam esquecendo a palavra do dia, porque o ritual matinal foi o único fator sobre o qual dá para agir que apareceu associado a mais retenção, e a maioria das partidas acontece fora desse horário.

**Ação:** criar um lembrete único de fim de dia, disparado apenas para quem não jogou até a tarde ("sua Palavritas de hoje ainda está te esperando"). É uma segunda chance no mesmo dia, sem incomodar quem já jogou (esse não recebe nada). Rodaria como teste A/B: metade dos usuários que costumam não jogar de manhã recebe o lembrete, metade não. O experimento ainda resolve de quebra o problema de eu não conseguir separar manhã de newsletter no histórico, porque aqui eu meço o efeito limpo da intervenção.

**Critério de sucesso:** saberei que funcionou quando o grupo que recebeu o lembrete tiver mais partidas completadas no dia e retenção de 30 dias maior que o controle, com uma diferença que não possa ser explicada por acaso, mirando os mesmos 5 a 6 pontos de diferença que observei entre quem tem e quem não tem o ritual matinal.

---

### Ressalvas e próximos passos

Duas honestidades que carrego junto com a proposta. Primeiro, o efeito da manhã é real porém pequeno, então o lembrete deve ser visto como um ajuste incremental, não uma virada de chave. Segundo, como a maior parte da retenção é explicada por hábito já formado (e não por fatores sobre os quais dá para agir), o ganho mais estrutural provavelmente está em ajudar o usuário novo a formar rotina, e não em recuperar quem já largou. O teste do lembrete é o primeiro passo barato e mensurável nessa direção.

---

### Nota técnica (para quem quiser conferir os números)

Para as comparações de retenção usei o teste qui-quadrado de independência, e reporto também o tamanho do efeito (phi).

- Começar de manhã x retenção de 30 dias: p = 0,043 (significativo a 5%), phi = 0,06 (efeito pequeno). Retenção de 34,5% (manhã) contra 28,5% (fora da manhã).
- Salário x retenção de 30 dias: p = 0,003, phi = 0,16. Único resultado significativo entre sete variáveis de perfil testadas (setor, salário, aparelho, food delivery, cargo, idade, porte da empresa), o que pede cautela por múltiplas comparações.
- Sequência de dias (streak) x voltar no dia seguinte: correlação de 0,02 no nível da partida, contra 0,82 quando agregada por usuário. A diferença evidencia a circularidade da métrica.
- Retenção de 30 dias definida por coorte (status da primeira partida de cada usuário): 30,4%.
