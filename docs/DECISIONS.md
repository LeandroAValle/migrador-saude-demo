# Decisões técnicas

| Decisão | Motivo | Consequência |
| --- | --- | --- |
| Criar um demo separado | O original contém fluxos operacionais e trabalho em andamento | Nenhum arquivo ou histórico privado é publicado |
| Guard antes do simulador | Tornar explícita a proteção de escrita | Execução em ambiente `production` gera erro antes de processar |
| Separar envio e consulta | Receber lote não prova sucesso do item | `SUCESSO` só aparece no fim da consulta |
| Histórico por registro | Permitir investigação e reprocessamento conceitual | Cada chave expõe os estados percorridos |
| Semente fixa | Facilitar testes e revisão | Os números são demonstrativos, não operacionais |
| Capturar somente a autenticação pública | Mostrar a aparência real sem acessar registros de produção | O Cloudflare Access bloqueia páginas internas; a demonstração sintética roda localmente |

O demo não implementa regras de mapeamento da Betha, nem afirma equivalência com o Migrador Saúde v2 privado.
