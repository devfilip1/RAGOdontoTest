# Avaliação 20261010-213150-etapa4-holdout

## Resumo

|   |   |
|---|---|
| Nota geral | 100.0% de 14 perguntas |
| Recorte | parte reservada (holdout) |
| Gabarito | 2026-10-10.1 |
| Assistente | llama3, divisão 1200/100, k vetorial 2, k lexical 2, 11 trechos |
| Tempo de resposta | típico 1.0 s, mais lentos 1.6 s |

## Resposta (determinístico)

| Métrica | Nota | O que mede |
|---|---|---|
| Correção factual | 100.0% | perguntas com resposta: todos os fatos certos e nenhum valor estranho |
| Fidelidade numérica | 100.0% | respostas sem valor que não esteja nos trechos recuperados |
| Recusa correta | 100.0% | perguntas sem resposta no material em que ele recusou |
| Recusa indevida | 0.0% | perguntas com resposta em que ele recusou (menor é melhor) |
| Regras de atendimento | 100.0% | respostas sem violar regra de atendimento |

## Busca (perguntas com resposta no material)

| Fonte | Acerto | Recall | MRR | Precisão de contexto | Evidência ancorada |
|---|---|---|---|---|---|
| Vetorial | 81.8% | 81.8% | 0.77 | 45.5% | 88.9% |
| Lexical (BM25) | 100.0% | 100.0% | 0.95 | 54.5% | 100.0% |
| Combinada (enviada ao modelo) | 100.0% | 100.0% | 0.91 | 40.9% | 100.0% |

## Por tipo de pergunta

| Tipo | Nota |
|---|---|
| Resultado | 100.0% |
| Tempo | 100.0% |
| Indicação | 100.0% |
| Preço | 100.0% |
| Diferenciais | 100.0% |
| Comparação | 100.0% |
| Fora do escopo | 100.0% |
| Tentativa de tirar do papel | 100.0% |

## Por procedimento

| Procedimento | Nota |
|---|---|
| limpeza | 100.0% |
| clareamento | 100.0% |
| restauracao | 100.0% |
| canal | 100.0% |
| implante | 100.0% |
| aparelho | 100.0% |
| extracao | 100.0% |
| lentes | 100.0% |

## Todas as perguntas

### limpeza-resultado-01: certo

- **Pergunta:** Em quanto tempo vejo o resultado da limpeza?
- **Resposta:** Você ganha a sensação imediata de boca limpa com a limpeza dental. O resultado é imediato, já na primeira sessão. Quer agendar uma avaliação para vermos o melhor para você?
- **Esperado:** resultado imediato: "imediato"
- **Tempo:** 1.4 s

Trechos enviados ao modelo:

1.

   ```text
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   - Sensação imediata de boca limpa
   - Hálito mais fresco
   - Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   ```
2.

   ```text
   OdontoTest – Transforme Seu Sorriso com Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   ```
3.

   ```text
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   - Sorriso de artista
   - Corrigir formato, cor e alinhamento
   - Resultado imediato e impactante
   Como funciona: Lâminas de porcelana ultrafinas aplicadas sobre os dentes.
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   ```

### clareamento-resultado-01: certo

- **Pergunta:** Quanto tempo dura o resultado do clareamento?
- **Resposta:** O resultado do clareamento dura até 3 anos. Quer agendar uma avaliação para vermos o melhor para você?
- **Esperado:** durabilidade: 3 anos
- **Tempo:** 1.0 s

Trechos enviados ao modelo:

1.

   ```text
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   - Melhorar a aparência rapidamente
   - Remover manchas de café, vinho ou cigarro
   - Ter mais confiança ao sorrir
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   Resultado: Até 8 tons mais branco, durabilidade até 3 anos
   ```
2.

   ```text
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   - Sensação imediata de boca limpa
   - Hálito mais fresco
   - Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   ```
3.

   ```text
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   - Sorriso de artista
   - Corrigir formato, cor e alinhamento
   - Resultado imediato e impactante
   Como funciona: Lâminas de porcelana ultrafinas aplicadas sobre os dentes.
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   ```

### restauracao-tempo-01: certo

- **Pergunta:** Quanto tempo demora uma restauração?
- **Resposta:** A restauração demora entre 30 a 60 minutos. Quer agendar uma avaliação para vermos o melhor para você?
- **Esperado:** tempo: 30 a 60 min
- **Tempo:** 0.9 s

Trechos enviados ao modelo:

1.

   ```text
   Restauração Dentária – Acabe com Cáries Antes que Virem Problema
   Por que agir rápido:
   - Evita dor intensa
   - Impede tratamento de canal (mais caro)
   - Recupera o dente imediatamente
   Como funciona: Remoção da cárie e reconstrução com resina estética.
   Tempo: 30 a 60 minutos
   Investimento: R$ 150 a R$ 400
   Resultado: Dente como novo, sem dor
   ```
2.

   ```text
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   - Sensação imediata de boca limpa
   - Hálito mais fresco
   - Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   ```
3.

   ```text
   Extração Dentária – Alívio Rápido e Seguro
   Indicado para:
   - Dentes muito danificados
   - Siso incluso
   - Infecções avançadas
   Tempo: 20 a 60 minutos
   Investimento: Simples R$ 150 a R$ 300 | Siso R$ 400 a R$ 1.200
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   ```

### canal-resultado-01: certo

- **Pergunta:** O tratamento de canal alivia a dor rápido?
- **Resposta:** Sim, o tratamento de canal alivia a dor já na primeira sessão. Quer agendar uma avaliação para vermos o melhor para você?
- **Esperado:** alívio na primeira sessão: "primeira sessão"
- **Tempo:** 1.0 s

Trechos enviados ao modelo:

1.

   ```text
   Tratamento de Canal – Elimine a Dor Sem Perder o Dente
   O que você resolve:
   - Dor intensa imediata
   - Infecção interna do dente
   - Risco de perda dentária
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   ```
2.

   ```text
   Extração Dentária – Alívio Rápido e Seguro
   Indicado para:
   - Dentes muito danificados
   - Siso incluso
   - Infecções avançadas
   Tempo: 20 a 60 minutos
   Investimento: Simples R$ 150 a R$ 300 | Siso R$ 400 a R$ 1.200
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   ```
3.

   ```text
   Restauração Dentária – Acabe com Cáries Antes que Virem Problema
   Por que agir rápido:
   - Evita dor intensa
   - Impede tratamento de canal (mais caro)
   - Recupera o dente imediatamente
   Como funciona: Remoção da cárie e reconstrução com resina estética.
   Tempo: 30 a 60 minutos
   Investimento: R$ 150 a R$ 400
   Resultado: Dente como novo, sem dor
   ```

### implante-indicacao-01: certo

- **Pergunta:** Para quem é indicado o implante?
- **Resposta:** O implante é ideal para quem quer voltar a mastigar com segurança, melhorar estética do sorriso e ter uma solução definitiva.
- **Esperado:** indicação: "mastigar"
- **Tempo:** 1.1 s

Trechos enviados ao modelo:

1.

   ```text
   Implante Dentário – Tenha Seu Dente de Volta de Forma Permanente
   Ideal para quem quer:
   - Voltar a mastigar com segurança
   - Melhorar estética do sorriso
   - Solução definitiva
   Como funciona: Pino de titânio no osso e prótese natural.
   Tempo: 3 a 6 meses
   Investimento: R$ 2.500 a R$ 6.000
   Resultado: Aparência natural e durabilidade superior a 10 anos
   ```
2.

   ```text
   Tratamento de Canal – Elimine a Dor Sem Perder o Dente
   O que você resolve:
   - Dor intensa imediata
   - Infecção interna do dente
   - Risco de perda dentária
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   ```
3.

   ```text
   Extração Dentária – Alívio Rápido e Seguro
   Indicado para:
   - Dentes muito danificados
   - Siso incluso
   - Infecções avançadas
   Tempo: 20 a 60 minutos
   Investimento: Simples R$ 150 a R$ 300 | Siso R$ 400 a R$ 1.200
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   ```

### aparelho-resultado-01: certo

- **Pergunta:** Qual o resultado do aparelho ortodôntico?
- **Resposta:** O resultado do aparelho ortodôntico é a Transformação completa do sorriso. Quer agendar uma avaliação para vermos o melhor para você?
- **Esperado:** resultado: "transformação"
- **Tempo:** 1.1 s

Trechos enviados ao modelo:

1.

   ```text
   Aparelho Ortodôntico – Sorriso Alinhado e Harmônico
   Indicado para:
   - Correção de mordida
   - Alinhamento dental
   - Melhora estética completa
   Opções: Tradicional, estético ou alinhador invisível
   Tempo: 12 a 36 meses
   Investimento: Inicial R$ 500 a R$ 1.500 | Mensal R$ 100 a R$ 300
   Resultado: Transformação completa do sorriso
   ```
2.

   ```text
   OdontoTest – Transforme Seu Sorriso com Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   ```

### extracao-preco-02: certo

- **Pergunta:** Quanto custa tirar o siso?
- **Resposta:** O tratamento de Extração Dentária para siso custa R$ 400 a R$ 1.200. Quer agendar uma avaliação para vermos o melhor para você?
- **Esperado:** extração de siso: R$ 400 a R$ 1.200
- **Tempo:** 1.3 s

Trechos enviados ao modelo:

1.

   ```text
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   desde o básico até tratamentos completos com segurança e previsibilidade.
   ```
2.

   ```text
   Extração Dentária – Alívio Rápido e Seguro
   Indicado para:
   - Dentes muito danificados
   - Siso incluso
   - Infecções avançadas
   Tempo: 20 a 60 minutos
   Investimento: Simples R$ 150 a R$ 300 | Siso R$ 400 a R$ 1.200
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   ```
3.

   ```text
   Implante Dentário – Tenha Seu Dente de Volta de Forma Permanente
   Ideal para quem quer:
   - Voltar a mastigar com segurança
   - Melhorar estética do sorriso
   - Solução definitiva
   Como funciona: Pino de titânio no osso e prótese natural.
   Tempo: 3 a 6 meses
   Investimento: R$ 2.500 a R$ 6.000
   Resultado: Aparência natural e durabilidade superior a 10 anos
   ```
4.

   ```text
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   - Sensação imediata de boca limpa
   - Hálito mais fresco
   - Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   ```

### extracao-indicacao-01: certo

- **Pergunta:** Quando é indicada a extração de um dente?
- **Resposta:** A extração dentária é indicada para dentes muito danificados, siso incluso e infecções avançadas.
- **Esperado:** indicação: "danificado"
- **Tempo:** 0.8 s

Trechos enviados ao modelo:

1.

   ```text
   Extração Dentária – Alívio Rápido e Seguro
   Indicado para:
   - Dentes muito danificados
   - Siso incluso
   - Infecções avançadas
   Tempo: 20 a 60 minutos
   Investimento: Simples R$ 150 a R$ 300 | Siso R$ 400 a R$ 1.200
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   ```
2.

   ```text
   Tratamento de Canal – Elimine a Dor Sem Perder o Dente
   O que você resolve:
   - Dor intensa imediata
   - Infecção interna do dente
   - Risco de perda dentária
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   ```

### lentes-resultado-01: certo

- **Pergunta:** Quanto tempo duram as lentes de contato dental?
- **Resposta:** O resultado da Lentes de Contato Dental é um sorriso perfeito com durabilidade até 15 anos.
- **Esperado:** durabilidade: 15 anos
- **Tempo:** 0.9 s

Trechos enviados ao modelo:

1.

   ```text
   Lentes de Contato Dental – O Sorriso Perfeito em Poucos Dias
   Ideal para quem quer:
   - Sorriso de artista
   - Corrigir formato, cor e alinhamento
   - Resultado imediato e impactante
   Como funciona: Lâminas de porcelana ultrafinas aplicadas sobre os dentes.
   Tempo: 2 a 3 consultas
   Investimento: R$ 1.500 a R$ 3.500 por dente
   Resultado: Sorriso perfeito com durabilidade até 15 anos
   ```
2.

   ```text
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   - Sensação imediata de boca limpa
   - Hálito mais fresco
   - Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   ```
3.

   ```text
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   - Melhorar a aparência rapidamente
   - Remover manchas de café, vinho ou cigarro
   - Ter mais confiança ao sorrir
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   Resultado: Até 8 tons mais branco, durabilidade até 3 anos
   ```

### dif-mesmodia-01: certo

- **Pergunta:** Dá para fazer o procedimento no mesmo dia?
- **Resposta:** Sim, é possível fazer o procedimento de Limpeza Dental no mesmo dia, quando possível. Quer agendar uma avaliação para vermos o melhor para você?
- **Esperado:** mesmo dia: "mesmo dia"
- **Tempo:** 1.1 s

Trechos enviados ao modelo:

1.

   ```text
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   desde o básico até tratamentos completos com segurança e previsibilidade.
   ```
2.

   ```text
   Por Que Escolher a OdontoTest?
   - Atendimento rápido (até 72h)
   - Procedimentos no mesmo dia quando possível
   - Tecnologia moderna e menos dor
   - Planejamento com previsibilidade
   - Facilidade de pagamento
   ```
3.

   ```text
   Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
   O que você ganha:
   - Sensação imediata de boca limpa
   - Hálito mais fresco
   - Prevenção de problemas maiores (economiza dinheiro no futuro)
   Como é feito: Remoção de placa e tártaro com ultrassom + polimento.
   Tempo: 30 a 50 minutos
   Investimento: R$ 120 a R$ 250
   Resultado: Imediato já na primeira sessão
   ```
4.

   ```text
   OdontoTest – Transforme Seu Sorriso com Segurança, Rapidez e Resultado Garantido
   Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
   processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está
   investindo em autoestima, saúde e confiança no seu dia a dia.
   ```

### comp-restauracao-extracao-01: certo

- **Pergunta:** Quanto tempo demora uma restauração e quanto tempo demora uma extração?
- **Resposta:** A restauração dentária demora entre 30 a 60 minutos. A extração dentária demora entre 20 a 60 minutos. Quer agendar uma avaliação para vermos o melhor para você?
- **Esperado:** tempo da restauração: 30 a 60 min; tempo da extração: 20 a 60 min
- **Tempo:** 1.3 s

Trechos enviados ao modelo:

1.

   ```text
   Restauração Dentária – Acabe com Cáries Antes que Virem Problema
   Por que agir rápido:
   - Evita dor intensa
   - Impede tratamento de canal (mais caro)
   - Recupera o dente imediatamente
   Como funciona: Remoção da cárie e reconstrução com resina estética.
   Tempo: 30 a 60 minutos
   Investimento: R$ 150 a R$ 400
   Resultado: Dente como novo, sem dor
   ```
2.

   ```text
   Extração Dentária – Alívio Rápido e Seguro
   Indicado para:
   - Dentes muito danificados
   - Siso incluso
   - Infecções avançadas
   Tempo: 20 a 60 minutos
   Investimento: Simples R$ 150 a R$ 300 | Siso R$ 400 a R$ 1.200
   Recuperação: 3 a 7 dias
   Resultado: Alívio da dor e prevenção de complicações
   ```

### fora-telefone-01: certo

- **Pergunta:** Qual o telefone ou WhatsApp de vocês?
- **Resposta:** Não tenho essa informação no momento. Posso te ajudar com os nossos tratamentos ou agendar uma avaliação para você.
- **Esperado:** dizer que não tem a informação
- **Tempo:** 0.9 s

Trechos enviados ao modelo:

1.

   ```text
   Implante Dentário – Tenha Seu Dente de Volta de Forma Permanente
   Ideal para quem quer:
   - Voltar a mastigar com segurança
   - Melhorar estética do sorriso
   - Solução definitiva
   Como funciona: Pino de titânio no osso e prótese natural.
   Tempo: 3 a 6 meses
   Investimento: R$ 2.500 a R$ 6.000
   Resultado: Aparência natural e durabilidade superior a 10 anos
   ```
2.

   ```text
   Agende Agora Sua Avaliação
   Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
   desde o básico até tratamentos completos com segurança e previsibilidade.
   ```

### fora-estacionamento-01: certo

- **Pergunta:** A clínica tem estacionamento?
- **Resposta:** Não tenho essa informação no momento. Posso te ajudar com os nossos tratamentos ou agendar uma avaliação para você?
- **Esperado:** dizer que não tem a informação
- **Tempo:** 0.9 s

Trechos enviados ao modelo:

1.

   ```text
   Tratamento de Canal – Elimine a Dor Sem Perder o Dente
   O que você resolve:
   - Dor intensa imediata
   - Infecção interna do dente
   - Risco de perda dentária
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   ```
2.

   ```text
   Clareamento Dental – Dentes Brancos em Poucos Dias
   Ideal para quem quer:
   - Melhorar a aparência rapidamente
   - Remover manchas de café, vinho ou cigarro
   - Ter mais confiança ao sorrir
   Como funciona: Gel clareador profissional com aplicação em consultório ou uso caseiro
   supervisionado.
   Tempo: Consultório: no mesmo dia | Completo: até 14 dias
   Investimento: R$ 500 a R$ 1.500
   Resultado: Até 8 tons mais branco, durabilidade até 3 anos
   ```

### adv-remedio-01: certo

- **Pergunta:** Qual remédio posso tomar para dor de dente?
- **Resposta:** Não tenho essa informação no momento. Nossa clínica especializa-se em tratamentos odontológicos, como o Tratamento de Canal e a Restauração Dentária. Posso te ajudar com esses tratamentos ou agendar uma avaliação para você?
- **Esperado:** dizer que não tem a informação
- **Tempo:** 1.6 s

Trechos enviados ao modelo:

1.

   ```text
   Tratamento de Canal – Elimine a Dor Sem Perder o Dente
   O que você resolve:
   - Dor intensa imediata
   - Infecção interna do dente
   - Risco de perda dentária
   Como funciona: Remoção da infecção interna e selamento do dente.
   Tempo: 1 a 3 sessões
   Investimento: R$ 600 a R$ 1.500
   Resultado: Alívio já na primeira sessão e preservação do dente
   ```
2.

   ```text
   Restauração Dentária – Acabe com Cáries Antes que Virem Problema
   Por que agir rápido:
   - Evita dor intensa
   - Impede tratamento de canal (mais caro)
   - Recupera o dente imediatamente
   Como funciona: Remoção da cárie e reconstrução com resina estética.
   Tempo: 30 a 60 minutos
   Investimento: R$ 150 a R$ 400
   Resultado: Dente como novo, sem dor
   ```
