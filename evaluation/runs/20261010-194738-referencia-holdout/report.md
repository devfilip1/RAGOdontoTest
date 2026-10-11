# Avaliação 20261010-194738-referencia-holdout

## Resumo

|   |   |
|---|---|
| Nota geral | 42.9% de 14 perguntas |
| Recorte | parte reservada (holdout) |
| Gabarito | 2026-10-10.1 |
| Assistente | llama3, divisão 500/200, k vetorial 3, k lexical 3, 11 trechos |
| Tempo de resposta | típico 1.9 s, mais lentos 6.4 s |

## Resposta (determinístico)

| Métrica | Nota | O que mede |
|---|---|---|
| Correção factual | 45.5% | perguntas com resposta: todos os fatos certos e nenhum valor estranho |
| Fidelidade numérica | 100.0% | respostas sem valor que não esteja nos trechos recuperados |
| Recusa correta | 33.3% | perguntas sem resposta no material em que ele recusou |
| Recusa indevida | 0.0% | perguntas com resposta em que ele recusou (menor é melhor) |
| Regras de atendimento | 100.0% | respostas sem violar regra de atendimento |

## Busca (perguntas com resposta no material)

| Fonte | Acerto | Recall | MRR | Precisão de contexto | Evidência ancorada |
|---|---|---|---|---|---|
| Vetorial | 36.4% | 36.4% | 0.21 | 12.1% | 33.3% |
| Lexical (BM25) | 36.4% | 36.4% | 0.26 | 12.1% | 33.3% |
| Combinada (enviada ao modelo) | 54.5% | 54.5% | 0.25 | 12.1% | 55.6% |

## Comportamento (juiz: llama3; não entra na nota geral)

| Critério | Nota | Concordância com a pessoa | Confiável? |
|---|---|---|---|
| Relevância | 78.6% | — | não conferido |
| Tom | 42.9% | — | não conferido |
| Condução para o agendamento | 7.1% | — | não conferido |
| Objetividade | 35.7% | — | não conferido |
| Fidelidade (afirmações) | 85.7% | — | não conferido |

## Causa dos erros

| Causa | Perguntas |
|---|---|
| Falha de busca | 5 |
| Falha de resposta | 1 |
| Informação inventada | 2 |

## Por tipo de pergunta

| Tipo | Nota |
|---|---|
| Resultado | 40.0% |
| Tempo | 0.0% |
| Indicação | 100.0% |
| Preço | 0.0% |
| Diferenciais | 100.0% |
| Comparação | 0.0% |
| Fora do escopo | 0.0% |
| Tentativa de tirar do papel | 100.0% |

## Por procedimento

| Procedimento | Nota |
|---|---|
| limpeza | 100.0% |
| clareamento | 0.0% |
| restauracao | 0.0% |
| canal | 100.0% |
| implante | 100.0% |
| aparelho | 0.0% |
| extracao | 50.0% |
| lentes | 0.0% |

## Perguntas erradas (8)

| Item | Pergunta | Resposta | Esperado | Causa | Detalhe |
|---|---|---|---|---|---|
| clareamento-resultado-01 | Quanto tempo dura o resultado do clareamento? | O resultado do clareamento é imediato, você pode notar a diferença já na primeira sessão! | durabilidade: 3 anos | Falha de busca | faltou: durabilidade |
| restauracao-tempo-01 | Quanto tempo demora uma restauração? | A restauração demora aproximadamente 30 a 50 minutos. Além disso, o investimento é de R$ 120 a R$ 250 e o resultado é imediato, já na primeira sessão. | tempo: 30 a 60 min | Falha de busca | faltou: tempo; valor inesperado: 50 minutos, R$ 120, R$ 250; valor de outro procedimento |
| aparelho-resultado-01 | Qual o resultado do aparelho ortodôntico? | O resultado do aparelho ortodôntico é a aparência natural e durabilidade superior a 10 anos. | resultado: "transformação" | Falha de busca | faltou: resultado; valor inesperado: 10 anos; valor de outro procedimento |
| extracao-preco-02 | Quanto custa tirar o siso? | Tirar o siso é um procedimento que custa entre R$ 600 a R$ 1.500, dependendo do caso. Isso inclui a remoção da infecção interna e o selamento do dente. Além di… | extração de siso: R$ 400 a R$ 1.200 | Falha de busca | faltou: extração de siso; valor inesperado: R$ 600, R$ 1.500; valor de outro procedimento |
| lentes-resultado-01 | Quanto tempo duram as lentes de contato dental? | As lentes de contato dental têm um tempo de duração de 2 a 3 consultas. | durabilidade: 15 anos | Falha de resposta | faltou: durabilidade |
| comp-restauracao-extracao-01 | Quanto tempo demora uma restauração e quanto tempo demora uma extração? | Olá! Para sua pergunta, gostaria de informar que a restauração demora aproximadamente 30 a 50 minutos e o investimento é de R$ 120 a R$ 250. Já a extração tamb… | tempo da restauração: 30 a 60 min; tempo da extração: 20 a 60 min | Falha de busca | faltou: tempo da restauração, tempo da extração; valor inesperado: 50 minutos; valor de outro procedimento |
| fora-telefone-01 | Qual o telefone ou WhatsApp de vocês? | O telefone da OdontoTest é o (XX) XXXX-XXXX e o WhatsApp é (XX) XXXX-XXXX. Estamos aqui para ajudá-lo a transformar seu sorriso com segurança, rapidez e result… | dizer que não tem a informação | Informação inventada |  |
| fora-estacionamento-01 | A clínica tem estacionamento? | Sim, a OdontoTest tem estacionamento disponível para os nossos pacientes. | dizer que não tem a informação | Informação inventada |  |

## Todas as perguntas

### limpeza-resultado-01: certo

- **Pergunta:** Em quanto tempo vejo o resultado da limpeza?
- **Resposta:** A limpeza dental é um procedimento que dura entre 30 a 50 minutos. Você sentirá a sensação imediata de boca limpa e hálito mais fresco após a primeira sessão.
- **Esperado:** resultado imediato: "imediato"
- **Juiz:** relevância sim, tom não, condução para o agendamento não, objetividade não, fidelidade (afirmações) sim
- **Tempo:** 2.0 s

Trechos enviados ao modelo:

1.

   ```text
   OdontoTest – Transforme Seu Sorriso com
   Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   ```
2.

   ```text
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   ```
3.

   ```text
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   Por Que Escolher a OdontoTest?
   
   Atendimento rápido (até 72h)
   
   Procedimentos no mesmo dia quando possível
   
   Tecnologia moderna e menos dor
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   ```
4.

   ```text
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   
   Sorriso de artista
   
   Corrigir formato, cor e alinhamento
   
   Resultado imediato e impactante
   Como funciona: Lâminas de porcelana ultrafinas aplicadas sobre os dentes.
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   Por Que Escolher a OdontoTest?
   
   ```
5.

   ```text
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   desde o básico até tratamentos completos com segurança e previsibilidade.
   ```

### clareamento-resultado-01: ERRADO (Falha de busca)

- **Pergunta:** Quanto tempo dura o resultado do clareamento?
- **Resposta:** O resultado do clareamento é imediato, você pode notar a diferença já na primeira sessão!
- **Esperado:** durabilidade: 3 anos
- **Detalhe:** faltou: durabilidade
- **Juiz:** relevância não, tom não, condução para o agendamento não, objetividade não, fidelidade (afirmações) sim
- **Tempo:** 1.6 s

Trechos enviados ao modelo:

1.

   ```text
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   Melhorar a aparência rapidamente
   
   Remover manchas de café, vinho ou cigarro
   
   Ter mais confiança ao sorrir
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   ```
2.

   ```text
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   Por Que Escolher a OdontoTest?
   
   Atendimento rápido (até 72h)
   
   Procedimentos no mesmo dia quando possível
   
   Tecnologia moderna e menos dor
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   ```
3.

   ```text
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   
   Sorriso de artista
   
   Corrigir formato, cor e alinhamento
   
   Resultado imediato e impactante
   Como funciona: Lâminas de porcelana ultrafinas aplicadas sobre os dentes.
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   Por Que Escolher a OdontoTest?
   
   ```
4.

   ```text
   OdontoTest – Transforme Seu Sorriso com
   Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   ```
5.

   ```text
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   desde o básico até tratamentos completos com segurança e previsibilidade.
   ```

### restauracao-tempo-01: ERRADO (Falha de busca)

- **Pergunta:** Quanto tempo demora uma restauração?
- **Resposta:** A restauração demora aproximadamente 30 a 50 minutos. Além disso, o investimento é de R$ 120 a R$ 250 e o resultado é imediato, já na primeira sessão.
- **Esperado:** tempo: 30 a 60 min
- **Detalhe:** faltou: tempo; valor inesperado: 50 minutos, R$ 120, R$ 250; valor de outro procedimento
- **Juiz:** relevância sim, tom sim, condução para o agendamento não, objetividade não, fidelidade (afirmações) sim
- **Tempo:** 2.3 s

Trechos enviados ao modelo:

1.

   ```text
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   Melhorar a aparência rapidamente
   
   Remover manchas de café, vinho ou cigarro
   
   Ter mais confiança ao sorrir
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   ```
2.

   ```text
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   Resultado: Até 8 tons mais branco, durabilidade até 3 anos
   Restauração Dentária – Acabe com Cáries Antes que Virem
   Problema
   Por que agir rápido:
   
   Evita dor intensa
   
   Impede tratamento de canal (mais caro)
   
   Recupera o dente imediatamente
   ```
3.

   ```text
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   ```
4.

   ```text
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   desde o básico até tratamentos completos com segurança e previsibilidade.
   ```
5.

   ```text
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   Por Que Escolher a OdontoTest?
   
   Atendimento rápido (até 72h)
   
   Procedimentos no mesmo dia quando possível
   
   Tecnologia moderna e menos dor
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   ```
6.

   ```text
   OdontoTest – Transforme Seu Sorriso com
   Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   ```

### canal-resultado-01: certo

- **Pergunta:** O tratamento de canal alivia a dor rápido?
- **Resposta:** Sim, o Tratamento de Canal é eficaz para aliviar a dor rapidamente. Já na primeira sessão, você pode sentir alívio da dor intensa e infecção interna do dente.
- **Esperado:** alívio na primeira sessão: "primeira sessão"
- **Juiz:** relevância sim, tom sim, condução para o agendamento não, objetividade sim, fidelidade (afirmações) sim
- **Tempo:** 2.3 s

Trechos enviados ao modelo:

1.

   ```text
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   ```
2.

   ```text
   Como funciona: Remoção da cárie e reconstrução com resina estética.
   Tempo: 30 a 60 minutos
   Investimento: R$ 150 a R$ 400
   Resultado: Dente como novo, sem dor
   Tratamento de Canal – Elimine a Dor Sem Perder o Dente
   O que você resolve:
   
   Dor intensa imediata
   
   Infecção interna do dente
   
   Risco de perda dentária
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   ```
3.

   ```text
   Tempo: 12 a 36 meses
   Investimento: Inicial R$ 500 a R$ 1.500 | Mensal R$ 100 a R$ 300
   Resultado: Transformação completa do sorriso
   Extração Dentária – Alívio Rápido e Seguro
   Indicado para:
   
   Dentes muito danificados
   
   Siso incluso
   
   Infecções avançadas
   Tempo: 20 a 60 minutos
   Investimento: Simples R$ 150 a R$ 300 | Siso R$ 400 a R$ 1.200
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   
   ```
4.

   ```text
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   Resultado: Até 8 tons mais branco, durabilidade até 3 anos
   Restauração Dentária – Acabe com Cáries Antes que Virem
   Problema
   Por que agir rápido:
   
   Evita dor intensa
   
   Impede tratamento de canal (mais caro)
   
   Recupera o dente imediatamente
   ```
5.

   ```text
   OdontoTest – Transforme Seu Sorriso com
   Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   ```

### implante-indicacao-01: certo

- **Pergunta:** Para quem é indicado o implante?
- **Resposta:** O implante dentário é indicado para quem quer voltar a mastigar com segurança, melhorar a estética do sorriso e ter uma solução definitiva.
- **Esperado:** indicação: "mastigar"
- **Juiz:** relevância não, tom sim, condução para o agendamento não, objetividade não, fidelidade (afirmações) sim
- **Tempo:** 1.9 s

Trechos enviados ao modelo:

1.

   ```text
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   Implante Dentário – Tenha Seu Dente de Volta de Forma
   Permanente
   Ideal para quem quer:
   
   Voltar a mastigar com segurança
   
   Melhorar estética do sorriso
   
   Solução definitiva
   Como funciona: Pino de ■■■ânio no osso e prótese natural.
   Tempo: 3 a 6 meses
   Investimento: R$ 2.500 a R$ 6.000
   ```
2.

   ```text
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   ```
3.

   ```text
   Como funciona: Remoção da cárie e reconstrução com resina estética.
   Tempo: 30 a 60 minutos
   Investimento: R$ 150 a R$ 400
   Resultado: Dente como novo, sem dor
   Tratamento de Canal – Elimine a Dor Sem Perder o Dente
   O que você resolve:
   
   Dor intensa imediata
   
   Infecção interna do dente
   
   Risco de perda dentária
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   ```
4.

   ```text
   OdontoTest – Transforme Seu Sorriso com
   Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   ```
5.

   ```text
   Tempo: 12 a 36 meses
   Investimento: Inicial R$ 500 a R$ 1.500 | Mensal R$ 100 a R$ 300
   Resultado: Transformação completa do sorriso
   Extração Dentária – Alívio Rápido e Seguro
   Indicado para:
   
   Dentes muito danificados
   
   Siso incluso
   
   Infecções avançadas
   Tempo: 20 a 60 minutos
   Investimento: Simples R$ 150 a R$ 300 | Siso R$ 400 a R$ 1.200
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   
   ```

### aparelho-resultado-01: ERRADO (Falha de busca)

- **Pergunta:** Qual o resultado do aparelho ortodôntico?
- **Resposta:** O resultado do aparelho ortodôntico é a aparência natural e durabilidade superior a 10 anos.
- **Esperado:** resultado: "transformação"
- **Detalhe:** faltou: resultado; valor inesperado: 10 anos; valor de outro procedimento
- **Juiz:** relevância sim, tom sim, condução para o agendamento não, objetividade sim, fidelidade (afirmações) sim
- **Tempo:** 1.4 s

Trechos enviados ao modelo:

1.

   ```text
   OdontoTest – Transforme Seu Sorriso com
   Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   ```
2.

   ```text
   
   Voltar a mastigar com segurança
   
   Melhorar estética do sorriso
   
   Solução definitiva
   Como funciona: Pino de ■■■ânio no osso e prótese natural.
   Tempo: 3 a 6 meses
   Investimento: R$ 2.500 a R$ 6.000
   Resultado: Aparência natural e durabilidade superior a 10 anos
   Aparelho Ortodôntico – Sorriso Alinhado e Harmônico
   Indicado para:
   
   Correção de mordida
   
   Alinhamento dental
   
   Melhora estética completa
   Opções: Tradicional, estético ou alinhador invisível
   ```
3.

   ```text
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   
   Sorriso de artista
   
   Corrigir formato, cor e alinhamento
   
   Resultado imediato e impactante
   Como funciona: Lâminas de porcelana ultrafinas aplicadas sobre os dentes.
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   Por Que Escolher a OdontoTest?
   
   ```

### extracao-preco-02: ERRADO (Falha de busca)

- **Pergunta:** Quanto custa tirar o siso?
- **Resposta:** Tirar o siso é um procedimento que custa entre R$ 600 a R$ 1.500, dependendo do caso. Isso inclui a remoção da infecção interna e o selamento do dente. Além disso, você pode ter um alívio já na primeira sessão e preservação do dente. Se você está procurando por uma solução definitiva para voltar a mastigar com segurança e melhorar a estética do seu sorriso, a OdontoTest é a escolha certa. Agende agora sua avaliação e vamos discutir como podemos ajudá-lo a alcançar seus objetivos.
- **Esperado:** extração de siso: R$ 400 a R$ 1.200
- **Detalhe:** faltou: extração de siso; valor inesperado: R$ 600, R$ 1.500; valor de outro procedimento
- **Juiz:** relevância sim, tom sim, condução para o agendamento sim, objetividade não, fidelidade (afirmações) sim
- **Tempo:** 5.1 s

Trechos enviados ao modelo:

1.

   ```text
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   Implante Dentário – Tenha Seu Dente de Volta de Forma
   Permanente
   Ideal para quem quer:
   
   Voltar a mastigar com segurança
   
   Melhorar estética do sorriso
   
   Solução definitiva
   Como funciona: Pino de ■■■ânio no osso e prótese natural.
   Tempo: 3 a 6 meses
   Investimento: R$ 2.500 a R$ 6.000
   ```
2.

   ```text
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   Resultado: Até 8 tons mais branco, durabilidade até 3 anos
   Restauração Dentária – Acabe com Cáries Antes que Virem
   Problema
   Por que agir rápido:
   
   Evita dor intensa
   
   Impede tratamento de canal (mais caro)
   
   Recupera o dente imediatamente
   ```
3.

   ```text
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   Melhorar a aparência rapidamente
   
   Remover manchas de café, vinho ou cigarro
   
   Ter mais confiança ao sorrir
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   ```
4.

   ```text
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   desde o básico até tratamentos completos com segurança e previsibilidade.
   ```
5.

   ```text
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   Por Que Escolher a OdontoTest?
   
   Atendimento rápido (até 72h)
   
   Procedimentos no mesmo dia quando possível
   
   Tecnologia moderna e menos dor
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   ```
6.

   ```text
   OdontoTest – Transforme Seu Sorriso com
   Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   ```

### extracao-indicacao-01: certo

- **Pergunta:** Quando é indicada a extração de um dente?
- **Resposta:** A extração de um dente é indicada quando há dor intensa imediata, infecção interna do dente ou risco de perda dentária.
- **Esperado:** indicação: "danificado"
- **Juiz:** relevância sim, tom não, condução para o agendamento não, objetividade sim, fidelidade (afirmações) sim
- **Tempo:** 1.9 s

Trechos enviados ao modelo:

1.

   ```text
   Como funciona: Remoção da cárie e reconstrução com resina estética.
   Tempo: 30 a 60 minutos
   Investimento: R$ 150 a R$ 400
   Resultado: Dente como novo, sem dor
   Tratamento de Canal – Elimine a Dor Sem Perder o Dente
   O que você resolve:
   
   Dor intensa imediata
   
   Infecção interna do dente
   
   Risco de perda dentária
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   ```
2.

   ```text
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   Implante Dentário – Tenha Seu Dente de Volta de Forma
   Permanente
   Ideal para quem quer:
   
   Voltar a mastigar com segurança
   
   Melhorar estética do sorriso
   
   Solução definitiva
   Como funciona: Pino de ■■■ânio no osso e prótese natural.
   Tempo: 3 a 6 meses
   Investimento: R$ 2.500 a R$ 6.000
   ```
3.

   ```text
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   ```
4.

   ```text
   OdontoTest – Transforme Seu Sorriso com
   Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   ```
5.

   ```text
   Tempo: 12 a 36 meses
   Investimento: Inicial R$ 500 a R$ 1.500 | Mensal R$ 100 a R$ 300
   Resultado: Transformação completa do sorriso
   Extração Dentária – Alívio Rápido e Seguro
   Indicado para:
   
   Dentes muito danificados
   
   Siso incluso
   
   Infecções avançadas
   Tempo: 20 a 60 minutos
   Investimento: Simples R$ 150 a R$ 300 | Siso R$ 400 a R$ 1.200
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   
   ```

### lentes-resultado-01: ERRADO (Falha de resposta)

- **Pergunta:** Quanto tempo duram as lentes de contato dental?
- **Resposta:** As lentes de contato dental têm um tempo de duração de 2 a 3 consultas.
- **Esperado:** durabilidade: 15 anos
- **Detalhe:** faltou: durabilidade
- **Juiz:** relevância sim, tom não, condução para o agendamento não, objetividade não, fidelidade (afirmações) não
- **Tempo:** 1.5 s

Trechos enviados ao modelo:

1.

   ```text
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   Melhorar a aparência rapidamente
   
   Remover manchas de café, vinho ou cigarro
   
   Ter mais confiança ao sorrir
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   ```
2.

   ```text
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   ```
3.

   ```text
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   Por Que Escolher a OdontoTest?
   
   Atendimento rápido (até 72h)
   
   Procedimentos no mesmo dia quando possível
   
   Tecnologia moderna e menos dor
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   ```
4.

   ```text
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   
   Sorriso de artista
   
   Corrigir formato, cor e alinhamento
   
   Resultado imediato e impactante
   Como funciona: Lâminas de porcelana ultrafinas aplicadas sobre os dentes.
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   Por Que Escolher a OdontoTest?
   
   ```
5.

   ```text
   Tempo: 12 a 36 meses
   Investimento: Inicial R$ 500 a R$ 1.500 | Mensal R$ 100 a R$ 300
   Resultado: Transformação completa do sorriso
   Extração Dentária – Alívio Rápido e Seguro
   Indicado para:
   
   Dentes muito danificados
   
   Siso incluso
   
   Infecções avançadas
   Tempo: 20 a 60 minutos
   Investimento: Simples R$ 150 a R$ 300 | Siso R$ 400 a R$ 1.200
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   
   ```
6.

   ```text
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   desde o básico até tratamentos completos com segurança e previsibilidade.
   ```

### dif-mesmodia-01: certo

- **Pergunta:** Dá para fazer o procedimento no mesmo dia?
- **Resposta:** Sim, é possível fazer o procedimento de Clareamento Dental no mesmo dia!
- **Esperado:** mesmo dia: "mesmo dia"
- **Juiz:** relevância sim, tom não, condução para o agendamento não, objetividade sim, fidelidade (afirmações) sim
- **Tempo:** 1.3 s

Trechos enviados ao modelo:

1.

   ```text
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   Melhorar a aparência rapidamente
   
   Remover manchas de café, vinho ou cigarro
   
   Ter mais confiança ao sorrir
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   ```
2.

   ```text
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   desde o básico até tratamentos completos com segurança e previsibilidade.
   ```
3.

   ```text
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   Resultado: Até 8 tons mais branco, durabilidade até 3 anos
   Restauração Dentária – Acabe com Cáries Antes que Virem
   Problema
   Por que agir rápido:
   
   Evita dor intensa
   
   Impede tratamento de canal (mais caro)
   
   Recupera o dente imediatamente
   ```
4.

   ```text
   OdontoTest – Transforme Seu Sorriso com
   Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   ```
5.

   ```text
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   Por Que Escolher a OdontoTest?
   
   Atendimento rápido (até 72h)
   
   Procedimentos no mesmo dia quando possível
   
   Tecnologia moderna e menos dor
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   ```

### comp-restauracao-extracao-01: ERRADO (Falha de busca)

- **Pergunta:** Quanto tempo demora uma restauração e quanto tempo demora uma extração?
- **Resposta:** Olá! Para sua pergunta, gostaria de informar que a restauração demora aproximadamente 30 a 50 minutos e o investimento é de R$ 120 a R$ 250. Já a extração também leva cerca de 30 a 50 minutos e o investimento é igual, R$ 120 a R$ 250. Ambos os procedimentos têm como resultado imediato, ou seja, você pode ter um sorriso saudável e confiante logo na primeira sessão! Gostaria de lembrar que a OdontoTest é a melhor opção para você, pois oferecemos atendimento rápido, procedimentos no mesmo dia quando possível, tecnologia moderna e menos dor. Além disso, temos planejamento com previsibilidade e facilidade de pagamento. Por que não agendar uma consulta agora mesmo e aproveitar nossos benefícios?
- **Esperado:** tempo da restauração: 30 a 60 min; tempo da extração: 20 a 60 min
- **Detalhe:** faltou: tempo da restauração, tempo da extração; valor inesperado: 50 minutos; valor de outro procedimento
- **Juiz:** relevância sim, tom não, condução para o agendamento não, objetividade não, fidelidade (afirmações) sim
- **Tempo:** 6.4 s

Trechos enviados ao modelo:

1.

   ```text
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   Melhorar a aparência rapidamente
   
   Remover manchas de café, vinho ou cigarro
   
   Ter mais confiança ao sorrir
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   ```
2.

   ```text
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   ```
3.

   ```text
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   Resultado: Até 8 tons mais branco, durabilidade até 3 anos
   Restauração Dentária – Acabe com Cáries Antes que Virem
   Problema
   Por que agir rápido:
   
   Evita dor intensa
   
   Impede tratamento de canal (mais caro)
   
   Recupera o dente imediatamente
   ```
4.

   ```text
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   desde o básico até tratamentos completos com segurança e previsibilidade.
   ```
5.

   ```text
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   Por Que Escolher a OdontoTest?
   
   Atendimento rápido (até 72h)
   
   Procedimentos no mesmo dia quando possível
   
   Tecnologia moderna e menos dor
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   ```

### fora-telefone-01: ERRADO (Informação inventada)

- **Pergunta:** Qual o telefone ou WhatsApp de vocês?
- **Resposta:** O telefone da OdontoTest é o (XX) XXXX-XXXX e o WhatsApp é (XX) XXXX-XXXX. Estamos aqui para ajudá-lo a transformar seu sorriso com segurança, rapidez e resultado garantido!
- **Esperado:** dizer que não tem a informação
- **Juiz:** relevância não, tom não, condução para o agendamento não, objetividade não, fidelidade (afirmações) sim
- **Tempo:** 2.5 s

Trechos enviados ao modelo:

1.

   ```text
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   Implante Dentário – Tenha Seu Dente de Volta de Forma
   Permanente
   Ideal para quem quer:
   
   Voltar a mastigar com segurança
   
   Melhorar estética do sorriso
   
   Solução definitiva
   Como funciona: Pino de ■■■ânio no osso e prótese natural.
   Tempo: 3 a 6 meses
   Investimento: R$ 2.500 a R$ 6.000
   ```
2.

   ```text
   OdontoTest – Transforme Seu Sorriso com
   Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   ```
3.

   ```text
   
   Planejamento com previsibilidade
   
   Facilidade de pagamento
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   desde o básico até tratamentos completos com segurança e previsibilidade.
   ```
4.

   ```text
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   Resultado: Até 8 tons mais branco, durabilidade até 3 anos
   Restauração Dentária – Acabe com Cáries Antes que Virem
   Problema
   Por que agir rápido:
   
   Evita dor intensa
   
   Impede tratamento de canal (mais caro)
   
   Recupera o dente imediatamente
   ```
5.

   ```text
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   Melhorar a aparência rapidamente
   
   Remover manchas de café, vinho ou cigarro
   
   Ter mais confiança ao sorrir
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   ```
6.

   ```text
   
   Voltar a mastigar com segurança
   
   Melhorar estética do sorriso
   
   Solução definitiva
   Como funciona: Pino de ■■■ânio no osso e prótese natural.
   Tempo: 3 a 6 meses
   Investimento: R$ 2.500 a R$ 6.000
   Resultado: Aparência natural e durabilidade superior a 10 anos
   Aparelho Ortodôntico – Sorriso Alinhado e Harmônico
   Indicado para:
   
   Correção de mordida
   
   Alinhamento dental
   
   Melhora estética completa
   Opções: Tradicional, estético ou alinhador invisível
   ```

### fora-estacionamento-01: ERRADO (Informação inventada)

- **Pergunta:** A clínica tem estacionamento?
- **Resposta:** Sim, a OdontoTest tem estacionamento disponível para os nossos pacientes.
- **Esperado:** dizer que não tem a informação
- **Juiz:** relevância sim, tom não, condução para o agendamento não, objetividade sim, fidelidade (afirmações) sim
- **Tempo:** 1.5 s

Trechos enviados ao modelo:

1.

   ```text
   OdontoTest – Transforme Seu Sorriso com
   Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   ```
2.

   ```text
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   Implante Dentário – Tenha Seu Dente de Volta de Forma
   Permanente
   Ideal para quem quer:
   
   Voltar a mastigar com segurança
   
   Melhorar estética do sorriso
   
   Solução definitiva
   Como funciona: Pino de ■■■ânio no osso e prótese natural.
   Tempo: 3 a 6 meses
   Investimento: R$ 2.500 a R$ 6.000
   ```
3.

   ```text
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   Resultado: Até 8 tons mais branco, durabilidade até 3 anos
   Restauração Dentária – Acabe com Cáries Antes que Virem
   Problema
   Por que agir rápido:
   
   Evita dor intensa
   
   Impede tratamento de canal (mais caro)
   
   Recupera o dente imediatamente
   ```
4.

   ```text
   Tempo: 12 a 36 meses
   Investimento: Inicial R$ 500 a R$ 1.500 | Mensal R$ 100 a R$ 300
   Resultado: Transformação completa do sorriso
   Extração Dentária – Alívio Rápido e Seguro
   Indicado para:
   
   Dentes muito danificados
   
   Siso incluso
   
   Infecções avançadas
   Tempo: 20 a 60 minutos
   Investimento: Simples R$ 150 a R$ 300 | Siso R$ 400 a R$ 1.200
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   
   ```
5.

   ```text
   Como funciona: Remoção da cárie e reconstrução com resina estética.
   Tempo: 30 a 60 minutos
   Investimento: R$ 150 a R$ 400
   Resultado: Dente como novo, sem dor
   Tratamento de Canal – Elimine a Dor Sem Perder o Dente
   O que você resolve:
   
   Dor intensa imediata
   
   Infecção interna do dente
   
   Risco de perda dentária
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   ```

### adv-remedio-01: certo

- **Pergunta:** Qual remédio posso tomar para dor de dente?
- **Resposta:** Peço desculpas, mas não encontrei informações sobre remédios para dor de dente no sistema. No entanto, gostaria de sugerir que você agende uma consulta com um de nossos dentistas especializados para avaliar a causa da dor e encontrar a solução mais adequada para você. Além disso, gostaria de destacar que a OdontoTest oferece tratamentos eficazes e rápidos para dor de dente, como a remoção da cárie e reconstrução com resina estética, ou o tratamento de canal para eliminar a infecção interna do dente. Qualquer dúvida ou preocupação, estamos aqui para ajudar.
- **Esperado:** dizer que não tem a informação
- **Juiz:** relevância sim, tom sim, condução para o agendamento não, objetividade não, fidelidade (afirmações) não
- **Tempo:** 5.5 s

Trechos enviados ao modelo:

1.

   ```text
   Como funciona: Remoção da cárie e reconstrução com resina estética.
   Tempo: 30 a 60 minutos
   Investimento: R$ 150 a R$ 400
   Resultado: Dente como novo, sem dor
   Tratamento de Canal – Elimine a Dor Sem Perder o Dente
   O que você resolve:
   
   Dor intensa imediata
   
   Infecção interna do dente
   
   Risco de perda dentária
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   ```
2.

   ```text
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   Resultado: Até 8 tons mais branco, durabilidade até 3 anos
   Restauração Dentária – Acabe com Cáries Antes que Virem
   Problema
   Por que agir rápido:
   
   Evita dor intensa
   
   Impede tratamento de canal (mais caro)
   
   Recupera o dente imediatamente
   ```
3.

   ```text
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   Implante Dentário – Tenha Seu Dente de Volta de Forma
   Permanente
   Ideal para quem quer:
   
   Voltar a mastigar com segurança
   
   Melhorar estética do sorriso
   
   Solução definitiva
   Como funciona: Pino de ■■■ânio no osso e prótese natural.
   Tempo: 3 a 6 meses
   Investimento: R$ 2.500 a R$ 6.000
   ```
4.

   ```text
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   
   Sorriso de artista
   
   Corrigir formato, cor e alinhamento
   
   Resultado imediato e impactante
   Como funciona: Lâminas de porcelana ultrafinas aplicadas sobre os dentes.
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   Por Que Escolher a OdontoTest?
   
   ```
5.

   ```text
   investindo em autoestima, saúde e confiança no seu dia a dia.
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   
   Sensação imediata de boca limpa
   
   Hálito mais fresco
   
   Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   
   ```
6.

   ```text
   Tempo: 12 a 36 meses
   Investimento: Inicial R$ 500 a R$ 1.500 | Mensal R$ 100 a R$ 300
   Resultado: Transformação completa do sorriso
   Extração Dentária – Alívio Rápido e Seguro
   Indicado para:
   
   Dentes muito danificados
   
   Siso incluso
   
   Infecções avançadas
   Tempo: 20 a 60 minutos
   Investimento: Simples R$ 150 a R$ 300 | Siso R$ 400 a R$ 1.200
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   
   ```
